# app/domain/schemas.py
from __future__ import annotations
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

# ---------- USERS ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: Optional[str] = None

class UserRead(BaseModel):
    id: str
    email: EmailStr
    class Config:
        from_attributes = True

# ---------- SESSIONS ----------
class SessionCreate(BaseModel):
    # ✅ optional
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

# --- LOGIN ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    id: str
    email: EmailStr

class UserPublic(BaseModel):
    id: str
    email: EmailStr