# src/app/api/deps/auth.py
from typing import Optional
from fastapi import Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select
import jwt

from app.db.dependencies import get_db
from app.core.jwt import decode_access_token
from app.core.config import settings
from app.domain.models import User

# Versão estrita (exige Authorization) → 401 se ausente
_oauth2_strict = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=True)

# Versão opcional (não 401 automático se ausente)
_oauth2_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def _resolve_user_from_token(db: Session, token: Optional[str]) -> Optional[User]:
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        uid = payload.get("sub")
        if not uid:
            return None
        return db.scalars(select(User).where(User.id == uid)).first()
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(_oauth2_strict),  # estrito
) -> User:
    user = getattr(request.state, "user", None)
    if user:
        return user
    user = _resolve_user_from_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return user

def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(_oauth2_optional),  # opcional
) -> Optional[User]:
    user = getattr(request.state, "user", None)
    if user:
        return user
    return _resolve_user_from_token(db, token)
