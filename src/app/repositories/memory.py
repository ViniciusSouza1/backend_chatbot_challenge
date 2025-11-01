from typing import Dict, List
from app.domain.schemas import ChatMessage

class InMemoryStore:
    def __init__(self) -> None:
        self._data: Dict[str, List[ChatMessage]] = {}

    def get_history(self, session_id: str) -> List[ChatMessage]:
        return self._data.get(session_id, [])

    def append_message(self, session_id: str, message: ChatMessage) -> List[ChatMessage]:
        history = self._data.setdefault(session_id, [])
        history.append(message)
        return history

# instância única para o app (simples p/ teste)
store = InMemoryStore()
