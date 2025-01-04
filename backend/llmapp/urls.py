from django.urls import path
from .views import PDFUploadAPIView, PDFEmbeddingStatusAPIView, ChatAPIView

urlpatterns = [
    path("upload/", PDFUploadAPIView.as_view(), name="api_upload_pdf"),
    path("status/<int:pdf_id>/", PDFEmbeddingStatusAPIView.as_view(), name="api_check_status"),
    path("chat/", ChatAPIView.as_view(), name="api_chat"),
]
