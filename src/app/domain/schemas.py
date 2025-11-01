from pydantic import BaseModel, Field
from typing import Literal, List

Role = Literal["user", "assistant"]

class ChatMessage(BaseModel):
    role: Role = Field(..., description="'user' or 'assistant'")
    content: str

class ChatRequest(BaseModel):
    sessionId: str
    message: str

class ChatHistoryResponse(BaseModel):
    sessionId: str
    messages: List[ChatMessage]
