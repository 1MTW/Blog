from django.urls import path
from .views import (
    PDFUploadAPIView,
    PDFEmbeddingStatusAPIView,
    PDFProgressAPIView,
    ChatResponseAPIView,
    EvidenceRetrievalAPIView,
    StartChatAPIView,
    ChatHistoryAPIView,
    UploadedPDFListAPIView,
)

urlpatterns = [
    path("upload/", PDFUploadAPIView.as_view(), name="api_upload_pdf"),
    path("uploaded_pdfs/", UploadedPDFListAPIView.as_view(), name="uploaded_pdf_list"),
    path("status/<int:pdf_id>/", PDFEmbeddingStatusAPIView.as_view(), name="api_check_status"),
    path("progress/<int:pdf_id>/", PDFProgressAPIView.as_view(), name="api_progress"),
    path("chat/", ChatResponseAPIView.as_view(), name="api_chat"),
    path("chat/history/<int:pdf_id>/", ChatHistoryAPIView.as_view(), name="chat_history"),
    path("retrieve/", EvidenceRetrievalAPIView.as_view(), name="api_evidence_retrieval"),
    path("start_chat/", StartChatAPIView.as_view(), name="start_chat"),
]
