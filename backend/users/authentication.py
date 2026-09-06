import jwt 

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from django.conf import settings

from .models import User

class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        parts = auth_header.split()

        if len(parts) !=2 or parts[0].lower() != "bearer":
            raise AuthenticationFailed("Invalid authorization header")

        token = parts[1]

        
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
            )

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")
        
        if payload.get("type") != "access":
            raise AuthenticationFailed("Invalid token type")

        user_id = payload.get("user_id")

        if not user_id:
            raise AuthenticationFailed("Invalid token payload")


        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")
        
        return (user, token)


    