"""Schemas comuns de resposta."""

from datetime import datetime

from pydantic import BaseModel


class ApiResponse(BaseModel):
    """Padroniza respostas da API."""

    success: bool = True
    data: dict | list | None = None
    message: str = ""
    timestamp: str = datetime.utcnow().isoformat()


class ErrorResponse(BaseModel):
    """Resposta de erro padronizada."""

    success: bool = False
    error: str
    detail: str | None = None