"""Configuração de logging estruturado com JSON."""

import json
import logging
import time
from datetime import UTC, datetime


class StructuredFormatter(logging.Formatter):
    """Formatador que emite logs em JSON para fácil ingestão."""

    def format(self, record: logging.LogRecord) -> str:
        # Tenta serializar o log como JSON.
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        # Captura exceções quando presentes.
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, default=str, ensure_ascii=False)


def setup_logger(name: str | None = None) -> logging.Logger:
    """Configura e retorna um logger com formatter JSON."""
    logger = logging.getLogger(name or "ia_api")
    logger.setLevel(logging.DEBUG)

    # Remove handlers anteriores para evitar duplicação.
    logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(StructuredFormatter())
    logger.addHandler(handler)

    return logger