import os
import json
import numpy as np
import faiss
from markitdown import MarkItDown
from openai import OpenAI, AuthenticationError, APIConnectionError, RateLimitError, OpenAIError
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")


def pdf_to_markdown_with_markitdown(pdf_path):
    try:
        md = MarkItDown()  # MarkItDown 객체 생성
        result = md.convert(pdf_path)  # PDF 변환
        return result.text_content  # 변환된 마크다운 텍스트 반환
    except Exception as e:
        raise RuntimeError(f"Failed to convert PDF to Markdown: {str(e)}")


def create_embedding(text):
    try:
        if not isinstance(text, str):
            raise ValueError(f"Input text must be a string. Got: {type(text)}")
        if len(text) > 10000:  # OpenAI 텍스트 길이 제한 확인
            raise ValueError("Input text exceeds the 10,000 character limit.")

        client = OpenAI(api_key=openai_api_key)
        response = client.embeddings.create(model="text-embedding-3-small", input=text)

        embedding_data = response.data
        if not embedding_data or "embedding" not in embedding_data[0]:
            raise RuntimeError(f"Invalid or incomplete API response: {response}")

        embedding = np.array(embedding_data[0]["embedding"], dtype=np.float32)
        return embedding
    except Exception as e:
        raise RuntimeError(f"Failed to create embedding: {str(e)}")


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


def create_openai_completion(prompt, model="text-davinci-003"):
    # 딥시크로 수정해놔
    try:
        client = OpenAI(api_key=openai_api_key)
        response = client.completions.create(
            model=model,
            prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )
        return response
    except Exception as e:
        raise RuntimeError(f"OpenAI Completion failed: {str(e)}")
