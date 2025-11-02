# app/api/routes/messages.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.domain.models import Message, Session as SessionModel
from app.domain.schemas import MessageCreate, MessageRead

router = APIRouter(prefix="/api/messages", tags=["messages"])

@router.get("", response_model=list[MessageRead])
def list_messages(db: Session = Depends(get_db)) -> list[Message]:
    return db.scalars(select(Message)).all()

@router.get("/by-session/{session_id}", response_model=list[MessageRead])
def list_messages_by_session(session_id: str, db: Session = Depends(get_db)) -> list[Message]:
    return db.scalars(select(Message).where(Message.session_id == session_id)).all()

@router.post("", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
def create_message(payload: MessageCreate, db: Session = Depends(get_db)) -> Message:
    session = db.get(SessionModel, payload.session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

    message = Message(session_id=payload.session_id, role=payload.role, content=payload.content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message