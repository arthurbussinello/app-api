"""Repository para persistência futura de requests da API."""

import logging
from datetime import UTC, datetime

logger = logging.getLogger("ia_api.request_repository")


class RequestRepository:
    """Repositório de logs de requisição (simulado — sem banco ainda)."""

    def __init__(self):
        self._requests: list[dict] = []

    def save(self, path: str, method: str, status: int, duration_ms: float, user_agent: str = "") -> dict:
        """Salva um log de requisição (simulado)."""
        req = {
            "id": len(self._requests) + 1,
            "path": path,
            "method": method,
            "status": status,
            "duration_ms": duration_ms,
            "user_agent": user_agent,
            "created_at": datetime.now(UTC).isoformat(),
        }
        self._requests.append(req)
        logger.info("RequestRepository: saved request #%d %s %s", req["id"], method, path)
        return req

    def find_by_path(self, path: str, limit: int = 100) -> list[dict]:
        """Retorna requisições filtradas por caminho."""
        results = [r for r in self._requests if path in r["path"]]
        return results[-limit:]

    def count(self) -> int:
        """Retorna total de requests logados."""
        return len(self._requests)