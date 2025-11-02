# app/domain/schemas.py
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional

# ---------- USERS ----------
class UserCreate(BaseModel):
    email: str
    password: Optional[str] = None

class UserRead(BaseModel):
    id: str
    email: str
    class Config:
        from_attributes = True

# ---------- SESSIONS ----------
class SessionCreate(BaseModel):
    # ✅ opcional
    user_id: Optional[str] = None
    title: Optional[str] = None

class SessionRead(BaseModel):
    id: str
    user_id: Optional[str] = None
    title: Optional[str] = None
    class Config:
        from_attributes = True

# ---------- MESSAGES ----------
class MessageCreate(BaseModel):
    session_id: str
    role: str = Field("user", description="user|assistant|system")
    content: str

class MessageRead(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    class Config:
        from_attributes = True

# ---------- CHAT (RAG) ----------
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatHistoryResponse(BaseModel):
    sessionId: str
    messages: List[ChatMessage]

class ChatRequest(BaseModel):
    sessionId: str
    message: str
