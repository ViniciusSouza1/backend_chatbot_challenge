import time
from app.domain.schemas import ChatMessage
from app.services.vector_client import search, build_context
from app.core.logging import get_logger
import os
CONFIDENCE_THRESHOLD = float(os.getenv("RAG_CONFIDENCE_THRESHOLD", "0.25"))

log = get_logger("rag.chat")

class ChatService:
    def answer_with_rag(self, user_text: str) -> ChatMessage:
        """
        Retrieve relevant FAQ entries from Pinecone and build a grounded answer.
        Filters low-confidence matches based on similarity score.
        """
        t0 = time.perf_counter()
        log.info(f"/api/chat | q='{user_text[:120]}'")

        matches = search(user_text, top_k=5)
        total_ms = (time.perf_counter() - t0) * 1000

        log.info(f"/api/chat | matches={len(matches)} | total_ms={total_ms:.1f}")

        # ✅ Confidence filter
        strong_matches = [m for m in matches if m.get("score", 0) >= CONFIDENCE_THRESHOLD]

        if not strong_matches:
            log.info(f"/api/chat | no strong matches (threshold={CONFIDENCE_THRESHOLD})")
            return ChatMessage(
                role="assistant",
                content=("I couldn't find a sufficiently relevant answer in the FAQ. "
                         "Try rephrasing or ask about account setup, payments, "
                         "security, compliance, or technical support.")
            )

        # Small, structured summary for debugging (no PII)
        summary = [{"id": m["id"], "score": round(m["score"], 4)} for m in strong_matches[:3]]
        log.debug(f"/api/chat | top_matches={summary}")

        context = build_context(strong_matches)
        answer = (
            "Here are the most relevant answers found in the FAQ:\n\n"
            f"{context}\n\n"
            "Let me know if you’d like me to expand on any of the points above."
        )
        return ChatMessage(role="assistant", content=answer)


chat_service = ChatService()