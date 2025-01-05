import os
import json
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import UploadedPDF, PDFEmbedding, ChatSession, ChatMessage
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
        # 클라이언트로부터 데이터 수신
        session_id = request.data.get("session_id")
        message = request.data.get("message")

        if not session_id or not message:
            return Response(
                {"error": "Session ID and message are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 세션 유효성 검증
        chat_session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        pdf = chat_session.pdf
        try:
            # PDF와 연관된 인덱스 및 메타데이터 로드
            index_file = f"faiss_indices/{pdf.id}_index.bin"
            metadata_file = f"faiss_indices/{pdf.id}_metadata.json"
            index, metadata = load_faiss_index(index_file, metadata_file)

            # 질문 메시지로 임베딩 생성
            query_embedding = create_embedding(message).reshape(1, -1)
            # 가장 관련성 높은 페이지 검색
            print(f"Query embedding shape: {query_embedding.shape}, dtype: {query_embedding.dtype}")
            print(f"Index dimensions: {index.d}")
            print(f"FAISS index total vectors: {index.ntotal}")
            distances, indices = index.search(query_embedding, top_k=5) ## 여기가 문제지점. 췤
            print("checkpoint: 2")
            evidence = [metadata[i] for i in indices[0]]
            # 문맥 생성
            context = "\n".join([f"Page {item['page_number']}: {item['text']}" for item in evidence])
            prompt = f"""
            Question: {message}
            Context:
            {context}
            Answer the question using the context.
            """
            print("Prompt: ", prompt)

            # OpenAI API를 통해 응답 생성
            response = create_openai_completion(prompt)

            # 메시지 저장 (DB)
            ChatMessage.objects.create(
                session=chat_session,
                sender="user",
                message=message
            )
            ChatMessage.objects.create(
                session=chat_session,
                sender="system",
                message=response["choices"][0]["text"].strip()
            )

            return Response({
                "response": response["choices"][0]["text"].strip(),
                "evidence": evidence
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Failed to process chat: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StartChatAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        pdf_id = request.data.get("pdf_id")
        if not pdf_id:
            return Response({"error": "PDF ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        pdf = UploadedPDF.objects.filter(id=pdf_id, user=request.user).first()
        if not pdf or not pdf.processed or not pdf.embedding_created:
            return Response({"error": "PDF is not ready for chat."}, status=status.HTTP_400_BAD_REQUEST)

        chat_session = ChatSession.objects.create(user=request.user, pdf=pdf)
        return Response({"chat_session_id": chat_session.id}, status=status.HTTP_200_OK)