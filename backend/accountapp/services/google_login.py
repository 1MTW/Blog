from random import SystemRandom
from urllib.parse import urlencode
import requests
import jwt
from django.conf import settings

class GoogleRawLoginFlowService:
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    SCOPES = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid",
    ]

    def __init__(self):
        self.client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
        self.client_secret = settings.GOOGLE_OAUTH2_CLIENT_SECRET
        self.redirect_uri = "http://localhost:8000/api/accountapp/auth/callback/"

    def _generate_state_token(self, length=30):
        rand = SystemRandom()
        return ''.join(rand.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(length))

    def get_authorization_url(self, next_url="/"):
        state = self._generate_state_token()
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.SCOPES),
            "state": state,
        }
        return f"{self.GOOGLE_AUTH_URL}?{urlencode(params)}", state

    def get_tokens(self, code):
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        response = requests.post(self.GOOGLE_TOKEN_URL, data=data)
        response.raise_for_status()
        return response.json()

    def decode_id_token(self, id_token):
        return jwt.decode(id_token, options={"verify_signature": False})
