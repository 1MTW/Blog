import os
import json
import numpy as np
import faiss
from markitdown import MarkItDown
from openai import OpenAI, AuthenticationError, APIConnectionError, RateLimitError, OpenAIError
from dotenv import load_dotenv
import openai
import requests
import re

from PyPDF2 import PdfReader # markitdown 버려. 페이지 인식 이슈

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

def pdf_to_markdown_with_markitdown(pdf_path):
    try:
        md = MarkItDown()
        result = md.convert(pdf_path)
        return result.text_content
    except Exception as e:
        raise RuntimeError(f"Failed to convert PDF to Markdown: {str(e)}")

def extract_text_with_page_numbers(pdf_path):
    reader = PdfReader(pdf_path)
    nodes = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        nodes.append({
            "page_number": i + 1,  # Page numbers start from 1
            "text": text.strip()
        })
    return nodes

import re

def createPDFChunk(pdf_path, CHUNK_SIZE, CHUNK_OVERLAP):
    pdf_nodes = extract_text_with_page_numbers(pdf_path)
    nodes = []

    for node in pdf_nodes:
        text = node["text"]
        page_number = node["page_number"]

        sentences = re.split(r'(?<=[.?!])\s+', text)
        current_chunk = []
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = len(sentence.split())  # 단어 개수로 토큰 수 추정
            if current_tokens + sentence_tokens > CHUNK_SIZE:
                nodes.append({
                    "page_label": page_number,
                    "text": " ".join(current_chunk)
                })
                # 겹치는 부분 추가
                current_chunk = current_chunk[-CHUNK_OVERLAP:] if CHUNK_OVERLAP > 0 else []
                current_tokens = sum(len(s.split()) for s in current_chunk)

            current_chunk.append(sentence)
            current_tokens += sentence_tokens

        # 마지막 청크 추가
        if current_chunk:
            nodes.append({
                "page_label": page_number,
                "text": " ".join(current_chunk)
            })

    return nodes



def create_embedding(text):
    try:
        if not isinstance(text, str):
            raise ValueError(f"Input text must be a string. Got: {type(text)}")
        #if len(text) > 10000:  # OpenAI 텍스트 길이 제한 확인
        #    raise ValueError("Input text exceeds the 10,000 character limit.")

        client = OpenAI(api_key=openai_api_key)
        response = client.embeddings.create(model="text-embedding-3-small", input=text)
        #print("response: ", response)

        embedding_data = response.data
        if not isinstance(embedding_data, list) or not embedding_data:
            raise RuntimeError(f"Invalid API response: response.data is not a non-empty list. Actual data: {embedding_data}")

        first_item = embedding_data[0]
        if not isinstance(first_item, openai.types.embedding.Embedding):
            raise RuntimeError(f"Unexpected type for response.data[0]: {type(first_item)}. Expected openai.types.embedding.Embedding.")
        if not hasattr(first_item, "embedding"):
            raise RuntimeError(f"'embedding' attribute is missing in response.data[0]: {first_item}")

        # 임베딩 추출
        embedding = np.array(first_item.embedding, dtype=np.float32)
        return embedding
    except Exception as e:
        print(f"Error during embedding creation: {e}")
        raise RuntimeError(f"Failed to create embedding: {e}")


def save_faiss_index(embeddings, metadata, index_file, metadata_file):
    try:
        embeddings = np.array(embeddings, dtype=np.float32)
        if embeddings.ndim != 2:
            raise ValueError(f"Embeddings must be a 2D array. Current shape: {embeddings.shape}")
        if embeddings.shape[0] < 1:
            raise ValueError("At least one embedding is required to create a FAISS index.")

        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)

        os.makedirs(os.path.dirname(index_file), exist_ok=True)
        faiss.write_index(index, index_file)

        with open(metadata_file, "w") as f:
            json.dump(metadata, f)
    except Exception as e:
        raise RuntimeError(f"Failed to save FAISS index: {str(e)}")


def load_faiss_index(index_file, metadata_file):
    try:
        if not os.path.exists(index_file) or not os.path.exists(metadata_file):
            raise FileNotFoundError(f"FAISS index or metadata file not found: {index_file}, {metadata_file}")

        index = faiss.read_index(index_file)
        with open(metadata_file, "r") as f:
            metadata = json.load(f)

        return index, metadata
    except Exception as e:
        raise RuntimeError(f"Failed to load FAISS index: {str(e)}")


def create_openai_completion(prompt, model="deepseek-chat"):
    print("DeepSeek API 요청 생성 중...")
    headers = {
        "Authorization": f"Bearer {deepseek_api_key}",
        "Content-Type": "application/json"
    }

    try:
        #print("DeepSeek API 호출 중...")
        response = requests.post(
            url=f"{deepseek_base_url}/chat/completions",
            headers=headers,
            json={
                "model": model,
                "messages": [{"role": "system", "content": prompt}],
                "max_tokens": 1500,
                "temperature": 1.0
            }
        )
        #print("DeepSeek API 호출 완료")
        response.raise_for_status()
        data = response.json()
        #print("DeepSeek API 응답 데이터: ", data)

        # 응답 데이터 검증
        if "choices" not in data or not data["choices"]:
            raise ValueError("DeepSeek API에서 올바르지 않은 응답 형식이 반환되었습니다.")
        #print(data["choices"][0]["message"]["content"])
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"DeepSeek API 호출 실패: {e}")
    except ValueError as e:
        raise RuntimeError(f"DeepSeek 응답 처리 실패: {e}")
    

def build_prompt_for_pdf(context, question, evidence_list):
    evidence_strings = []
    for evidence in evidence_list:
        evidence_strings.append(
            f"- **Page:** {evidence['page_number']}  \n  **Evidence:** \"{evidence['text']}\""
        )
    evidence_section = "\n".join(evidence_strings)

    prompt = f"""
    You are an expert AI system tasked with generating accurate and evidence-based answers strictly from the provided PDF document. 
    The answers must be written in Korean using Markdown formatting. 
    Always reference the evidence from the PDF, including page numbers, and do not include any information outside the provided context.

    ### Question
    "{question}"

    ### Context
    "{context}"

    ### Evidence extracted from the PDF
    {evidence_section}

    ### Instructions (Enhanced HTML Formatting)
    1. **Answer the question based exclusively on the information provided in the PDF document.**
    2. Use **HTML** to format your answer with an elegant and clear structure, adhering to the following:
       - **Headings** (`<h1>`, `<h2>`, `<h3>`) for major sections:
         - `<h1>` for the main title (e.g., 답변, 근거, 결론).
         - `<h2>` for subsections or subtopics if needed.
       - **Bold text** (`<strong>`) for emphasis.
       - **Bullet points** (`<ul>`) or numbered lists (`<ol>`) for clarity and organization.
       - **Code blocks** (`<pre>` and `<code>`) or inline code (`<code>`) for referencing technical details.
       - **Table elements** (`<table>`, `<tr>`, `<th>`, `<td>`) for structured data when applicable.
       - **Links** (`<a href="URL">`) to online resources, if URLs are mentioned in the PDF content.
    3. **Cite evidence clearly** for each point, including:
       - The **page number** and relevant text.
       - Highlight specific keywords from the evidence using **bold** or **italic** formatting.
    4. If the question cannot be answered based on the PDF content, clearly state:
       <p><strong>PDF 문서에서는 해당 정보가 제공되지 않습니다.</strong></p>
    5. Write the entire answer in **Korean**.

    ### Response Format (Use HTML Format)
    <h1>답변</h1>
    <p>
        PDF 문서에서는 질문에 대한 정보가 제공되지 않습니다.
    </p>
    
    <h1>근거</h1>
    <ul>
        <li>
            <strong>Page:</strong> [Page number]<br>
            <strong>Text:</strong> "[Relevant text here]"
        </li>
        <li>
            <strong>Page:</strong> [Page number]<br>
            <strong>Text:</strong> "[Relevant text here]"
        </li>
    </ul>
    
    <h1>결론</h1>
    <p>
        PDF 문서에서 질문에 대한 정보는 찾을 수 없었습니다. 
        <strong>따라서, 제공된 자료로는 답변을 구성할 수 없습니다.</strong>
    </p>

    """
    print("Prompt2: ", prompt)
    return prompt

