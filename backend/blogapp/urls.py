from django.urls import path
from .views import (
    FetchPostsAPIView,
    PostSearchAPIView,
    PostSearchCategoryAPIView,
    CreatePostAPIView,
    CreateCategoryAPIView,
    FetchCategoryAPIView,
)

urlpatterns = [
    path("history/", FetchPostsAPIView.as_view(), name="api_history"),
    path("search/<int:post_id>/", PostSearchAPIView.as_view(), name="api_particular_post"),
    path("search/category/<str:category>/",PostSearchCategoryAPIView.as_view(),name="post_by_category"),
    path("post/",CreatePostAPIView.as_view(),name="post"),
    path("category/create/", CreateCategoryAPIView.as_view(), name="create-category"),
    path("category/",FetchCategoryAPIView.as_view(),name="FetchCategory"),
]
