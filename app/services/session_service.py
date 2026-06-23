"""Serviço de sessão — gerencia sessões de chat."""

import logging
from datetime import UTC, datetime

logger = logging.getLogger("ia_api.session_service")


class SessionService:
    """Gerencia sessões de conversação (em memória)."""

    def __init__(self):
        # Sessões em memória: {session_id: {"messages": [...], "created_at": str}}
        self._sessions: dict[str, dict] = {}

    def create_session(self, session_id: str | None = None) -> dict:
        """Cria uma nova sessão e retorna seus dados."""
        import uuid
        sid = session_id or f"session_{uuid.uuid4().hex[:16]}"
        self._sessions[sid] = {
            "session_id": sid,
            "messages": [],
            "created_at": datetime.now(UTC).isoformat(),
        }
        logger.info("Session created: %s", sid)
        return self._sessions[sid]

    def get_session(self, session_id: str) -> dict | None:
        """Retorna os dados de uma sessão pelo ID."""
        return self._sessions.get(session_id)

    def add_message(self, session_id: str, role: str, content: str) -> dict:
        """Adiciona uma mensagem à sessão existente.
        
        Args:
            session_id: Identificador da sessão.
            role: Papel da mensagem ("user", "assistant", "system").
            content: Conteúdo da mensagem.
        
        Returns:
            A sessão atualizada com a nova mensagem.
        
        Raises:
            ValueError: Se a sessão não existir.
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Sessão '{session_id}' não encontrada")

        message = {"role": role, "content": content, "timestamp": datetime.now(UTC).isoformat()}
        session["messages"].append(message)
        logger.debug("Message added to session %s: %s", session_id, role)
        return session

    def get_messages(self, session_id: str) -> list[dict]:
        """Retorna as mensagens de uma sessão."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Sessão '{session_id}' não encontrada")
        return session["messages"]

    def delete_session(self, session_id: str) -> bool:
        """Remove uma sessão existente."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info("Session deleted: %s", session_id)
            return True
        return False

    def list_sessions(self) -> list[str]:
        """Retorna lista de IDs das sessões ativas."""
        return list(self._sessions.keys())