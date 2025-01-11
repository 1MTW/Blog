from rest_framework import serializers
from .models import PostHistory, Categories

class PostSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.category_name", read_only=True)

    class Meta:
        model = PostHistory
        fields = ['id', 'user', 'title', 'content', 'category', 'category_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ['id', 'user', 'category_name']
