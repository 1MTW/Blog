from django.contrib import admin
from .models import UploadedPDF, PDFEmbedding, ChatSession, ChatMessage

admin.site.register(UploadedPDF)
admin.site.register(PDFEmbedding)
admin.site.register(ChatSession)
admin.site.register(ChatMessage)
