"""Rotas de chat (completions)."""

import logging
from typing import List

from pydantic import BaseModel, Field

from api.v1 import router as v1_router
from schemas.chat import ChatMessage, ChatResponse
from services.chat_service import chat_service


logger = logging.getLogger("ia_api.chat")


class CompletionBody(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Histórico de mensagens")
    provider: str | None = Field("local", description="Provider a ser usado")
    model: str | None = Field(None, description="Modelo específico (override)")
    temperature: float | None = Field(0.7, ge=0, le=2)


@v1_router.post("/chat/completions", response_model=ChatResponse)
def chat_completions(body: CompletionBody):
    """Endpoint de completions estilo OpenAI."""
    messages_list = [m.model_dump() for m in body.messages]

    result = chat_service.complete(
        messages=messages_list,
        provider=body.provider,
        model=body.model,
        temperature=body.temperature,
    )
    return ChatResponse(**result)