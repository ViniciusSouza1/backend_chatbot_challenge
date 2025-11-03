# src/app/api/deps/auth.py
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select
import jwt

from app.db.dependencies import get_db
from app.core.config import settings
from app.core.jwt import decode_access_token
from app.domain.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    If the middleware has already populated request.state.user, it uses it directly (avoids re-decoding).
    Otherwise, it decodes the token and loads the user.
    """
    if getattr(request.state, "user", None):
        return request.state.user

    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(
            token,
            secret=settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    except jwt.InvalidTokenError:
        raise credentials_exc

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exc

    user = db.scalars(select(User).where(User.id == user_id)).first()
    if not user:
        raise credentials_exc
    return user


def get_optional_user(request: Request) -> Optional[User]:
    """
    Useful in routes that accept anonymous access but require the user if present.
    NEVER throws an exception — only returns None if not authenticated.
    """
    return getattr(request.state, "user", None)


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Simple admin via emails in .env (ADMIN_EMAILS=mail1,mail2).
    """
    admin_list = {e.strip().lower() for e in (settings.admin_emails or [])}
    if not current_user.email.lower() in admin_list:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only.")
    return current_user
