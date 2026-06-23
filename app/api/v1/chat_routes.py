"""Rotas de chat (completions)."""

import logging
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.schemas.chat import ChatMessage, ChatResponse
from app.services.chat_service import ChatService
from app.providers.router import ProviderRouter

router = APIRouter()

logger = logging.getLogger("ia_api.chat")


class CompletionBody(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Histórico de mensagens")
    provider: str | None = Field("local", description="Provider a ser usado")
    model: str | None = Field(None, description="Modelo específico (override)")
    temperature: float | None = Field(0.7, ge=0, le=2)


chat_service = ChatService(router=ProviderRouter())


@router.post("/chat/completions", response_model=ChatResponse)
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