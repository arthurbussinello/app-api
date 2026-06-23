"""Serviço de auditoria — registra operações da API."""

import logging
from datetime import UTC, datetime

logger = logging.getLogger("ia_api.audit_service")


class AuditService:
    """Registra auditoria das operações realizadas na API."""

    def __init__(self):
        # Em produção, persistiria no banco de dados.
        self._records: list[dict] = []

    def log_request(self, endpoint: str, method: str, user: str | None, status: int, detail: str = "") -> None:
        """Registra uma requisição na API."""
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "endpoint": endpoint,
            "method": method,
            "user": user or "anonymous",
            "status": status,
            "detail": detail,
        }
        self._records.append(record)
        logger.info(
            "Audit: %s %s -> %d (user=%s)",
            method,
            endpoint,
            status,
            record["user"],
        )

    def get_records(self, limit: int = 100) -> list[dict]:
        """Retorna os registros de auditoria mais recentes."""
        return self._records[-limit:]

    def log_chat(self, provider: str, messages_count: int, response_time_ms: float) -> None:
        """Registra uma operação de chat."""
        logger.info(
            "Audit chat: provider=%s messages=%d time=%.1fms",
            provider,
            messages_count,
            response_time_ms,
        )

    def log_agent_run(self, agent_id: str, iterations: int, success: bool) -> None:
        """Registra uma execução de agente."""
        logger.info(
            "Audit agent: id=%s iterations=%d success=%s",
            agent_id,
            iterations,
            success,
        )

    def log_sql_query(self, query_preview: str, validated: bool, error: str = "") -> None:
        """Registra uma consulta SQL."""
        logger.info(
            "Audit SQL: query='%s' valid=%s error='%s'",
            query_preview[:50],
            validated,
            error,
        )