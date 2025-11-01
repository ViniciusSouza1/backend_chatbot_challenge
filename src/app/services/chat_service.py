import time
from app.domain.schemas import ChatMessage
from app.services.vector_client import search, build_context
from app.core.logging import get_logger

log = get_logger("rag.chat")

class ChatService:
    def answer_with_rag(self, user_text: str) -> ChatMessage:
        """
        Retrieve relevant FAQ entries from Pinecone and build a grounded answer.
        (No LLM yet; this keeps the project functional even without external keys.)
        """
        t0 = time.perf_counter()
        log.info(f"/api/chat | q='{user_text[:120]}'")

        matches = search(user_text, top_k=3)

        total_ms = (time.perf_counter() - t0) * 1000
        log.info(f"/api/chat | matches={len(matches)} | total_ms={total_ms:.1f}")

        if not matches:
            return ChatMessage(
                role="assistant",
                content=("I couldn't find relevant information in the FAQ for this question. "
                         "Try rephrasing or ask about account setup, payments, security, "
                         "compliance, or technical support.")
            )

        # Small, structured summary for debugging (no PII)
        summary = [{"id": m["id"], "score": round(m["score"], 4)} for m in matches[:3]]
        log.debug(f"/api/chat | top_matches={summary}")

        context = build_context(matches)
        answer = (
            "Here are the most relevant answers found in the FAQ:\n\n"
            f"{context}\n\n"
            "Let me know if you’d like me to expand on any of the points above."
        )
        return ChatMessage(role="assistant", content=answer)

chat_service = ChatService()