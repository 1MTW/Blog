from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.google_login import GoogleRawLoginFlowService
from django.contrib.auth import login, logout
from django.contrib.auth.models import User

from rest_framework.permissions import IsAuthenticated

class GoogleLoginRedirectApi(APIView):
    def get(self, request, *args, **kwargs):
        service = GoogleRawLoginFlowService()
        authorization_url, state = service.get_authorization_url()

        next_url = request.GET.get("next", "/")
        request.session["next_url"] = next_url

        request.session["google_oauth2_state"] = state
        return redirect(authorization_url)

class GoogleLoginCallbackApi(APIView):
    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")
        state = request.GET.get("state")
        session_state = request.session.get("google_oauth2_state")

        if state != session_state:
            return Response({"error": "CSRF validation failed"}, status=status.HTTP_400_BAD_REQUEST)

        service = GoogleRawLoginFlowService()
        tokens = service.get_tokens(code)
        user_info = service.decode_id_token(tokens["id_token"])

        user, created = User.objects.get_or_create(
            username=user_info["email"], email=user_info["email"]
        )
        login(request, user)
        next_url = request.session.pop("next_url", "/")  
        return redirect(next_url)
    
class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        return Response({
            "email": user.email,
            "username": user.username,
        })
    
class LogoutAPIView(APIView):
    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({"message": "Logged out successfully."}, status=200)
