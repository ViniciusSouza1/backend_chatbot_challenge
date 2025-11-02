# app/repositories/db.py
from __future__ import annotations
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.domain.models import User, Session as ChatSession, Message

# ---------- USERS ----------
def get_user(db: Session, user_id: str) -> Optional[User]:
    return db.get(User, user_id)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.scalars(select(User).where(User.email == email)).first()

# ---------- SESSIONS ----------
def get_session(db: Session, session_id: str) -> Optional[ChatSession]:
    return db.get(ChatSession, session_id)

def list_sessions_by_user(db: Session, user_id: str) -> List[ChatSession]:
    return db.scalars(select(ChatSession).where(ChatSession.user_id == user_id)).all()

# ---------- MESSAGES ----------
def list_messages(db: Session, session_id: str) -> List[Message]:
    return db.scalars(select(Message).where(Message.session_id == session_id).order_by(Message.id)).all()

def append_message(db: Session, session_id: str, role: str, content: str) -> Message:
    msg = Message(session_id=session_id, role=role, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
