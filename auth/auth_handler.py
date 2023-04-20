import datetime
import hashlib
import jwt
import time

from models.user import MongoUser
from typing import Dict

JWT_SECRET = 'ABCD'
JWT_ALGORITHM = 'HS256'


def token_response(token: str):
    return {
        "access_token": token
    }


def sign_jwt(user_id: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=120)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token,
                                   JWT_SECRET,
                                   algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["exp"] >= \
                                time.time() else None
    except Exception:
        return {}


def authenticate_user(email, password):
    hashed = hashlib.sha256(password.encode('utf-8'))
    hashed_password = hashed.hexdigest()
    verification = MongoUser.objects.filter(
        email=email,
        password=hashed_password,
        is_verified=True)
    if verification:
        return verification