from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import default_storage
from .models import UploadedPDF
from django.shortcuts import get_object_or_404

class PDFUploadAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        """Handle PDF upload."""
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file provided."}, status=400)

        # Save the uploaded file
        file_path = default_storage.save(f"uploads/pdfs/{file.name}", file)
        uploaded_pdf = UploadedPDF.objects.create(file=file_path)

        return Response({"message": "File uploaded successfully!", "id": uploaded_pdf.id}, status=201)

class PDFEmbeddingStatusAPIView(APIView):
    def get(self, request, pdf_id, *args, **kwargs):
        """Check embedding processing status for a specific PDF."""
        pdf = get_object_or_404(UploadedPDF, id=pdf_id)
        return Response({"processed": pdf.processed}, status=200)

class ChatAPIView(APIView):
    def post(self, request, *args, **kwargs):
        """Handle chat requests."""
        data = request.data
        user_message = data.get("message")
        pdf_id = data.get("pdf_id")

        if not user_message or not pdf_id:
            return Response({"error": "Invalid request."}, status=400)

        # Simulated response (replace with actual chat logic)
        response_message = f"Received: {user_message}. PDF ID: {pdf_id}"

        return Response({"response": response_message}, status=200)
