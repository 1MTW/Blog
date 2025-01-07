from rest_framework import serializers
from .models import UploadedPDF, ChatMessage
from urllib.parse import unquote

class UploadedPDFSerializer(serializers.ModelSerializer):
    decoded_file_name = serializers.SerializerMethodField()

    class Meta:
        model = UploadedPDF
        fields = ['id', 'file', 'decoded_file_name', 'uploaded_at']

    def get_decoded_file_name(self, obj):
        return unquote(obj.file.name.split('/')[-1])
    
class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "session", "sender", "message", "created_at"]

class UploadedPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedPDF
        fields = ['id', 'file', 'uploaded_at', 'processed', 'embedding_created']