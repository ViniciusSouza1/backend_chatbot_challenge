# src/app/api/deps/permissions.py
from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.domain.schemas import ChatRequest

from app.api.deps.auth import get_current_user, get_current_user_optional
from app.db.dependencies import get_db
from app.domain.models import User, Session as SessionModel
from app.core.config import settings

def _is_admin(user: Optional[User]) -> bool:
    if not user:
        return False
    admins = {a.strip().lower() for a in (settings.admin_emails or []) if a.strip()}
    return user.email.lower() in admins

def require_user(user: User = Depends(get_current_user)) -> User:
    # estrito
    return user

def require_admin(user: User = Depends(require_user)) -> User:
    if not _is_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return user

def require_self_or_admin_for_user(
    user_id: str,
    user: User = Depends(get_current_user),  # estrito
) -> User:
    if user.id == user_id or _is_admin(user):
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

def get_session_or_404(session_id: str, db: Session = Depends(get_db)) -> SessionModel:
    sess = db.get(SessionModel, session_id)
    if not sess:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    return sess

def ensure_session_access_owner_or_anon(
    sess: SessionModel = Depends(get_session_or_404),
    maybe_user: Optional[User] = Depends(get_current_user_optional),  # opcional
) -> SessionModel:
    if sess.user_id is None:
        return sess
    if not maybe_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    if maybe_user.id == sess.user_id or _is_admin(maybe_user):
        return sess
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

def verify_chat_access(
    req: ChatRequest,                                # <-- lê o BODY (sessionId)
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
) -> SessionModel:
    sess = db.get(SessionModel, req.sessionId)
    if not sess:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

    # sessão anônima => posse por segredo, não exige login
    if sess.user_id is None:
        return sess

    # sessão com dono => exige dono ou admin
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    if user.id != sess.user_id and not _is_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return sess

def verify_session_access_by_query(
    sessionId: str,                                  # <-- lê QUERY param
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
) -> SessionModel:
    sess = db.get(SessionModel, sessionId)
    if not sess:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    if sess.user_id is None:
        return sess
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    if user.id != sess.user_id and not _is_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return sess