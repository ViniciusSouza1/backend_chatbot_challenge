# src/app/core/jwt.py
import time
import jwt
from app.core.config import settings

def create_access_token(payload: dict, expires_minutes: int | None = None) -> str:
    to_encode = payload.copy()
    exp_secs = int((expires_minutes or settings.jwt_exp_minutes) * 60)
    to_encode["exp"] = int(time.time()) + exp_secs
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
