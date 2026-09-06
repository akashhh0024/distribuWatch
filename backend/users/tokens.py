import jwt 

from datetime import datetime, timezone
from django.conf import settings

def create_access_token(user):

    now = datetime.now(timezone.utc)

    payload = {
        "user_id":user.id,
        "type":"access",
        "iat":now,
        "exp":now + settings.JWT_ACCESS_TOKEN_LIFETIME
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm="HS256"
    )


def create_refresh_token(user):
    now = datetime.now(timezone.utc)

    payload = {
        "user_id":user.id,
        "type":"refresh",
        "iat":now,
        "exp":now + settings.JWT_REFRESH_TOKEN_LIFETIME
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm="HS256",
    )