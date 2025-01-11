from django.shortcuts import render
from .serializers import PostSerializer, CategorySerializer
from .models import PostHistory, Categories
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

class FetchPostsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        posts = PostHistory.objects.filter(user=request.user)
        result = PostSerializer(posts, many=True)  # many=True 추가
        return Response(result.data)


class PostSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def get(self, request, post_id, *args, **kwargs):
        try:
            # post_id로 필터링
            post = PostHistory.objects.get(id=post_id, user=request.user)
            serializer = PostSerializer(post)
            return Response(serializer.data)
        except PostHistory.DoesNotExist:
            return Response({"error": "Post not found"}, status=404)
    def put(self, request, post_id, *args, **kwargs):
        try:
            # post_id와 사용자로 게시물 필터링
            post = PostHistory.objects.get(id=post_id, user=request.user)
        except PostHistory.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        # 요청 데이터에서 category_name 추출
        category_name = request.data.get("category_name")
        if not category_name:
            return Response({"error": "category_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # category_name으로 Categories 모델에서 카테고리 찾기
            new_category = Categories.objects.get(category_name=category_name, user=request.user)
        except Categories.DoesNotExist:
            return Response({"error": f"Category '{category_name}' not found"}, status=status.HTTP_404_NOT_FOUND)

        # category_id를 request.data에 추가
        data = request.data.copy()  # request.data는 불변 객체이므로 복사본을 생성
        data["category"] = new_category.id  # category 필드에 ID 추가

        # serializer를 통해 title, content, category 업데이트
        serializer = PostSerializer(post, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()  # 데이터 저장
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostSearchCategoryAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능
    def get(self, request, category, *args, **kwargs):
        try:
            # category로 filtering
            post = PostHistory.objects.get(category=category, user=request.user)
            serializer = PostSerializer(post)
            return Response(serializer.data)
        except PostHistory.DoesNotExist:
            return Response({"error": "Post not found"}, status=404)

class CreatePostAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        content = request.data.get("content")
        title = request.data.get("title")
        category_name = request.data.get("category_name")  # 카테고리 이름

        if not all([title, content, category_name]):
            return Response({"error": "All fields (title, content, category) are required"}, status=400)

        try:
            # 카테고리 검색 또는 생성
            category, created = Categories.objects.get_or_create(user=user, category_name=category_name)

            # 포스트 생성
            post = PostHistory.objects.create(
                user=user, content=content, title=title, category=category
            )
            result = PostSerializer(post)
            return Response(result.data, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class CreateCategoryAPIView(APIView):
    def post(self, request, *args, **kwargs):
        category_name = request.data.get("category_name")  # JSON body에서 카테고리 이름 가져오기
        if not category_name:
            return Response({"error": "Category name is required"}, status=400)

        try:
            user = request.user
            category = Categories.objects.create(
                user=user, category_name=category_name
            )
            result = CategorySerializer(category)
            return Response(result.data, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class FetchCategoryAPIView(APIView):
    def get(self,request,*args,**kwargs):
        user = request.user
        categories = Categories.objects.filter(user=request.user)
        result = CategorySerializer(categories, many=True)  # many=True 추가
        return Response(result.data)


        