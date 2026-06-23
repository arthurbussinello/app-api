"""Repository para persistência futura de mensagens de chat."""

import logging
from datetime import UTC, datetime

logger = logging.getLogger("ia_api.message_repository")


class MessageRepository:
    """Repositório de mensagens (simulado — sem banco ainda)."""

    def __init__(self):
        self._messages: list[dict] = []

    def save(self, session_id: str, role: str, content: str) -> dict:
        """Salva uma mensagem no chat (simulado)."""
        msg = {
            "id": len(self._messages) + 1,
            "session_id": session_id,
            "role": role,
            "content": content,
            "created_at": datetime.now(UTC).isoformat(),
        }
        self._messages.append(msg)
        logger.info("MessageRepository: saved message #%d for session %s", msg["id"], session_id)
        return msg

    def find_by_session(self, session_id: str, limit: int = 100) -> list[dict]:
        """Retorna mensagens de uma sessão específica."""
        results = [m for m in self._messages if m.get("session_id") == session_id]
        return results[-limit:]

    def count(self) -> int:
        """Retorna total de mensagens salvas."""
        return len(self._messages)