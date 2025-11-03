# src/app/api/routes/messages.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional

from app.db.dependencies import get_db
from app.domain.models import Message, Session as SessionModel, User
from app.domain.schemas import MessageCreate, MessageRead
from app.api.deps.auth import get_current_user, get_current_user_optional
from app.api.deps.permissions import require_admin
from app.core.config import settings

router = APIRouter(prefix="/api/messages", tags=["messages"])

def _is_admin(user: Optional[User]) -> bool:
    if not user:
        return False
    admins = {a.strip().lower() for a in (settings.admin_emails or []) if a.strip()}
    return user.email.lower() in admins

@router.get("", response_model=list[MessageRead])
def list_messages(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),   # admin-only (como definido na sua matriz)
) -> list[Message]:
    return db.scalars(select(Message)).all()

@router.get("/by-session/{session_id}", response_model=list[MessageRead])
def list_messages_by_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),  # ✅ opcional (guest permitido)
) -> list[Message]:
    sess = db.get(SessionModel, session_id)
    if not sess:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

    # Sessão anônima → libera por segredo (só saber o session_id)
    if sess.user_id is None:
        return db.scalars(select(Message).where(Message.session_id == session_id)).all()

    # Sessão com dono → exige dono ou admin
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    if current_user.id != sess.user_id and not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return db.scalars(select(Message).where(Message.session_id == session_id)).all()

@router.post("", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
def create_message(
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),  # ✅ opcional (guest permitido)
) -> Message:
    sess = db.get(SessionModel, payload.session_id)
    if not sess:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

    if sess.user_id is None:
        message = Message(session_id=payload.session_id, role=payload.role, content=payload.content)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    if current_user.id != sess.user_id and not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    message = Message(session_id=payload.session_id, role=payload.role, content=payload.content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message