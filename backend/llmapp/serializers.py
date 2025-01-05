from rest_framework import serializers
from .models import UploadedPDF, ChatMessage

class UploadedPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedPDF
        fields = ["id", "file", "uploaded_at", "processed", "embedding_created"]

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "session", "sender", "message", "created_at"]
