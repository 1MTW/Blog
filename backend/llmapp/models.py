from django.db import models
from django.contrib.auth.models import User

class UploadedPDF(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="uploaded_pdfs")
    file = models.FileField(upload_to="uploads/pdfs/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    embedding_created = models.BooleanField(default=False)

    def __str__(self):
        return self.file.name

class PDFEmbedding(models.Model):
    pdf = models.OneToOneField(UploadedPDF, on_delete=models.CASCADE, related_name="embedding")
    embedding_data = models.BinaryField()  # 임베딩 데이터 (FAISS에 저장될 바이너리 형태)
    metadata = models.JSONField()  # 페이지 메타데이터
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Embedding for {self.pdf.file.name}"

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_sessions")
    pdf = models.ForeignKey(UploadedPDF, on_delete=models.CASCADE, related_name="chat_sessions")
    started_at = models.DateTimeField(auto_now_add=True)
    last_interaction = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chat Session {self.id} for {self.user.username}"

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=50, choices=[("user", "User"), ("system", "System")])
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message in Session {self.session.id} by {self.sender}"
