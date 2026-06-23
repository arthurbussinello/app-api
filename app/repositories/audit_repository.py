"""Repository para persistência futura de logs de auditoria."""

import logging
from datetime import UTC, datetime

logger = logging.getLogger("ia_api.audit_repository")


class AuditRepository:
    """Repositório para logs de auditoria (simulado — sem banco ainda)."""

    def __init__(self):
        self._records: list[dict] = []

    def save(self, endpoint: str, method: str, user: str, status: int, detail: str = "") -> dict:
        """Salva um registro de auditoria (simulado)."""
        record = {
            "id": len(self._records) + 1,
            "timestamp": datetime.now(UTC).isoformat(),
            "endpoint": endpoint,
            "method": method,
            "user": user,
            "status": status,
            "detail": detail,
        }
        self._records.append(record)
        logger.info("AuditRepository: saved record #%d", record["id"])
        return record

    def find_by(self, endpoint: str | None = None, user: str | None = None, limit: int = 100) -> list[dict]:
        """Filtra registros de auditoria."""
        results = self._records[:]
        if endpoint:
            results = [r for r in results if r["endpoint"] == endpoint]
        if user:
            results = [r for r in results if user in str(r.get("user", ""))]
        return results[-limit:]

    def count(self) -> int:
        """Retorna total de registros."""
        return len(self._records)