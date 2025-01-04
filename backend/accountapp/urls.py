from django.urls import path
from .views import GoogleLoginRedirectApi, GoogleLoginCallbackApi, CurrentUserAPIView, LogoutAPIView

urlpatterns = [
    path("auth/login/", GoogleLoginRedirectApi.as_view(), name="google-login"),
    path("auth/callback/", GoogleLoginCallbackApi.as_view(), name="google-callback"),
    path("auth/logout/", LogoutAPIView.as_view(), name="logout"),
    path("me/", CurrentUserAPIView.as_view(), name="current-user"),
    
]
