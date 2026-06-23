"""Schemas comuns de resposta da API."""

from typing import Any, Optional

from pydantic import BaseModel


class ResponseBase(BaseModel):
    """Resposta padrão com status e mensagem."""
    success: bool = True
    message: str = "ok"


class ErrorMessage(ResponseBase):
    """Resposta de erro para a API."""
    success: bool = False

    error: str
    detail: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Resposta com paginação simples."""
    total: int
    page: int
    per_page: int
    items: list[Any]


class ProviderInfo(BaseModel):
    """Informações sobre um provider de IA."""
    id: str
    name: str
    description: str
    enabled: bool = True

    class Config:
        from_attributes = True