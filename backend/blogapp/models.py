from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Categories(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Category")
    category_name = models.CharField(max_length=255) 
    def __str__(self):
        return f"{self.category_name}"

class PostHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="PostHistory")
    title = models.CharField(max_length=255)  # 포스트 제목
    content = models.TextField()  # 포스트 내용
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)  # 카테고리 이름
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간
    updated_at = models.DateTimeField(auto_now=True)  # 업데이트 시간

    def __str__(self):
        return f"{self.title} - {self.category} by {self.user.username}"

    @property
    def category_name(self):
        return self.category.category_name
