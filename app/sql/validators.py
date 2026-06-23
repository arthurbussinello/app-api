"""Validador de queries SQL — bloqueia comandos perigosos, permite apenas SELECT."""

import logging
import re

from app.core.exceptions import SQLValidationError

logger = logging.getLogger("ia_api.sql_validator")


# Padrões que indicam tentativas de injeção ou escrita.
_DANGEROUS_PATTERNS = [
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bDROP\b",
    r"\bALTER\b",
    r"\bCREATE\b",
    r"\bEXEC\b",
    r"\bEXECUTE\b",
    r"\bTRUNCATE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"--",           # comentario de linha
    r"/\*",           # comentario bloco
    r";\s*DROP",      # chained commands
    r"xp_",          # stored procedures estendidas
    r"sp_executesql",
]

# Regex combinada para performance.
_DANGEROUS_REGEX = re.compile("|".join(_DANGEROUS_PATTERNS), re.IGNORECASE)


def validate_sql(query: str) -> bool:
    """Valida se a query SQL é segura (apenas SELECT).

    Args:
        query: String contendo a query SQL.

    Returns:
        True se a query for segura.

    Raises:
        SQLValidationError: Se a query contiver comandos perigosos.
    """
    if not query or not isinstance(query, str):
        raise SQLValidationError("Query vazia ou inválida")

    stripped = query.strip().upper()

    # Verifica se começa com SELECT (único comando permitido).
    if not stripped.startswith("SELECT"):
        raise SQLValidationError(
            f"Comando não permitido. Apenas SELECT é autorizado. Recebido: '{stripped[:30]}'"
        )

    # Verifica padrões perigosos dentro da query.
    match = _DANGEROUS_REGEX.search(query)
    if match:
        raise SQLValidationError(
            f"Padrão perigoso detectado na query: '{match.group()}'"
        )

    logger.debug("SQL validation passed for query: %s", query[:100])
    return True


def is_select_only(query: str) -> bool:
    """Retorna True se a query contém apenas comandos SELECT."""
    try:
        return validate_sql(query)
    except SQLValidationError:
        return False