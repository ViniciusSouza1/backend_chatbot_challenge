from app.domain.schemas import ChatMessage

class ChatService:
    def build_stub_reply(self, user_text: str) -> ChatMessage:
        # Aqui entrará o RAG (fase 2). Por enquanto, stub didático:
        text = f"Received: '{user_text}'. Pretty soon we are going to respond with RAG from FAQ."
        return ChatMessage(role="assistant", content=text)

chat_service = ChatService()