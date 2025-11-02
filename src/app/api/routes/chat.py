# app/api/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.repositories import db as repo
from app.domain.schemas import ChatRequest, ChatHistoryResponse, ChatMessage
from app.services.chat_service import chat_service

router = APIRouter(prefix="/api")

@router.post("/chat", response_model=ChatHistoryResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    sess = repo.get_session(db, req.sessionId)
    if not sess:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

    repo.append_message(db, session_id=req.sessionId, role="user", content=req.message)

    reply_msg = chat_service.answer_with_rag(req.message)

    repo.append_message(db, session_id=req.sessionId, role="assistant", content=reply_msg.content)

    rows = repo.list_messages(db, session_id=req.sessionId)
    history = [ChatMessage(role=m.role, content=m.content) for m in rows]
    return ChatHistoryResponse(sessionId=req.sessionId, messages=history)

@router.get("/history", response_model=ChatHistoryResponse)
def get_history(sessionId: str, db: Session = Depends(get_db)):
    sess = repo.get_session(db, sessionId)
    if not sess:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    rows = repo.list_messages(db, session_id=sessionId)
    history = [ChatMessage(role=m.role, content=m.content) for m in rows]
    return ChatHistoryResponse(sessionId=sessionId, messages=history)
