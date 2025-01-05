import os
import json
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import UploadedPDF, PDFEmbedding
from .utils import (
    pdf_to_markdown_with_markitdown,
    create_embedding,
    save_faiss_index,
    load_faiss_index,
    create_openai_completion,
)
from dotenv import load_dotenv

load_dotenv()
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")


class PDFUploadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uploaded_pdf = UploadedPDF.objects.create(user=request.user, file=file)

            pdf_path = uploaded_pdf.file.path
            markdown_text = pdf_to_markdown_with_markitdown(pdf_path)
            if not markdown_text.strip():
                raise RuntimeError("No valid content found in the PDF.")
        except Exception as e:
            return Response({"error": f"Failed to process PDF: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            embeddings = []
            metadata = []
            pages = markdown_text.split("\n### Page")
            for page_number, page_content in enumerate(pages, start=1):
                text = page_content.strip()
                if text:
                    embedding = create_embedding(text)
                    embeddings.append(embedding)
                    metadata.append({"page_number": page_number, "text": text})

            if not embeddings:
                raise RuntimeError("No embeddings were generated.")

            index_file = f"faiss_indices/{uploaded_pdf.id}_index.bin"
            metadata_file = f"faiss_indices/{uploaded_pdf.id}_metadata.json"
            save_faiss_index(embeddings, metadata, index_file, metadata_file)

            uploaded_pdf.processed = True
            uploaded_pdf.embedding_created = True
            uploaded_pdf.processing_progress = 100
            uploaded_pdf.save()
        except Exception as e:
            return Response({"error": f"Failed to save embeddings or metadata: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "PDF processed successfully", "pdf_id": uploaded_pdf.id}, status=status.HTTP_200_OK)


class EvidenceRetrievalAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        pdf_id = request.data.get("pdf_id")
        question = request.data.get("question")
        top_k = int(request.data.get("top_k", 5))

        if not pdf_id or not question:
            return Response({"error": "PDF ID and question are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            index_file = f"faiss_indices/{pdf_id}_index.bin"
            metadata_file = f"faiss_indices/{pdf_id}_metadata.json"
            index, metadata = load_faiss_index(index_file, metadata_file)

            query_embedding = create_embedding(question).reshape(1, -1)

            distances, indices = index.search(query_embedding, top_k=top_k)

            evidence = [metadata[i] for i in indices[0]]

            context = "\n".join([f"Page {item['page_number']}: {item['text']}" for item in evidence])
            prompt = f"""
            Question: {question}
            Context:
            {context}
            Answer the question using the context.
            """
            response = create_openai_completion(prompt)

            return Response({
                "question": question,
                "answer": response["choices"][0]["text"].strip(),
                "evidence": evidence
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Failed to process question: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PDFEmbeddingStatusAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pdf_id, *args, **kwargs):
        pdf = get_object_or_404(UploadedPDF, id=pdf_id, user=request.user)
        return Response({
            "processed": pdf.processed,
            "embedding_created": pdf.embedding_created
        }, status=status.HTTP_200_OK)


class PDFProgressAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pdf_id, *args, **kwargs):
        pdf = get_object_or_404(UploadedPDF, id=pdf_id, user=request.user)
        progress = getattr(pdf, "processing_progress", None)

        if progress is None:
            return Response({"error": "Progress tracking not available for this PDF."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"progress": progress}, status=status.HTTP_200_OK)


class ChatResponseAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        context = request.data.get("context")
        claim_text = request.data.get("claim_text")
        evidence_list = request.data.get("evidence")

        if not claim_text or not evidence_list:
            return Response({"error": "Claim text and evidence are required."}, status=status.HTTP_400_BAD_REQUEST)

        headers = {
            "Authorization": f"Bearer {deepseek_api_key}",
            "Content-Type": "application/json"
        }

        prompt = f"""
        Claim: {claim_text}
        Context: {context}
        Evidence:
        {json.dumps(evidence_list, indent=2)}
        """

        try:
            response = requests.post(
                url=f"{deepseek_base_url}/chat/completions",
                headers=headers,
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "system", "content": prompt}]
                }
            )
            response.raise_for_status()
            data = response.json()

            if "choices" not in data or not data["choices"]:
                return Response({"error": "Invalid response from DeepSeek API"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                "response": data["choices"][0]["message"]["content"]
            }, status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
