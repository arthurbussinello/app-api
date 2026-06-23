"""Schemas para operações de chat."""

from typing import Optional

from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Mensagem individual do chat."""
    role: str  # "user", "assistant", "system"
    content: str


class ChatCompletionRequest(BaseModel):
    """Requisição de completions de chat."""
    messages: list[ChatMessage]
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1024


class ChatCompletionResponse(BaseModel):
    """Resposta de completions de chat."""
    id: str
    created_at: str
    provider: str
    model: str
    message: ChatMessage
    usage: dict[str, int] = {}