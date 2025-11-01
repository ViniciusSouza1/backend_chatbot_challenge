from fastapi import APIRouter
from app.domain.schemas import ChatRequest, ChatHistoryResponse, ChatMessage
from app.repositories.memory import store
from app.services.chat_service import chat_service

router = APIRouter(prefix="/api")

@router.get("/history", response_model=ChatHistoryResponse)
def get_history(sessionId: str):
    messages = store.get_history(sessionId)
    return ChatHistoryResponse(sessionId=sessionId, messages=messages)

@router.post("/chat", response_model=ChatHistoryResponse)
def chat(req: ChatRequest):
    store.append_message(req.sessionId, ChatMessage(role="user", content=req.message))
    reply = chat_service.answer_with_rag(req.message)
    store.append_message(req.sessionId, reply)
    return ChatHistoryResponse(sessionId=req.sessionId, messages=store.get_history(req.sessionId))
