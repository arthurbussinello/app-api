"""Schemas para chat completions."""

from datetime import datetime

from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Mensagem de chat com role e content."""

    role: str = "user"
    content: str


class ChatResponse(BaseModel):
    """Resposta de um endpoint de chat/completions."""

    id: str = ""
    created_at: str = datetime.utcnow().isoformat()
    provider: str = "local"
    model: str = "mock"
    message: dict = {}
    usage: dict = {"prompt_tokens": 0, "completion_tokens": 0}