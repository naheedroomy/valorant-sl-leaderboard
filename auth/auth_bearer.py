from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth.auth_handler import decode_jwt


def verify_jwt(token_jwt: str) -> bool:
    is_token_valid: bool = False

    try:
        payload = decode_jwt(token_jwt)
    except Exception:
        payload = None
    if payload:
        is_token_valid = True
    return is_token_valid


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer,
            self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403,
                                    detail="Invalid authentication scheme.")
            if not verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403,
                                    detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403,
                                detail="Invalid authorization code.")


async def get_user(token: str = Depends(JWTBearer())) -> dict:
    payload = decode_jwt(token)
    return {
        "email": payload.get("user_id")
    }