from django.urls import path
from .views import (
    PDFUploadAPIView,
    PDFEmbeddingStatusAPIView,
    PDFProgressAPIView,
    ChatResponseAPIView,
    EvidenceRetrievalAPIView,
)

urlpatterns = [
    path("upload/", PDFUploadAPIView.as_view(), name="api_upload_pdf"),
    path("status/<int:pdf_id>/", PDFEmbeddingStatusAPIView.as_view(), name="api_check_status"),
    path("progress/<int:pdf_id>/", PDFProgressAPIView.as_view(), name="api_progress"),
    path("chat/", ChatResponseAPIView.as_view(), name="api_chat"),
    path("retrieve/", EvidenceRetrievalAPIView.as_view(), name="api_evidence_retrieval"),
]
