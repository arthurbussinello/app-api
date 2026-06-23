"""Rotas de chat completions."""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

router = APIRouter()


class ChatCompletionRequest(BaseModel):
    """Requisição de completions de chat."""
    messages: list[dict] = []
    provider: str | None = None
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int = 1024


class ChatCompletionResponse(BaseModel):
    """Resposta de completions de chat."""
    id: str
    created_at: str
    provider: str
    model: str
    message: dict
    usage: dict = {}


@router.post("/v1/chat/completions")
async def chat_completions(
    req: ChatCompletionRequest,
    request: Request,
) -> dict:
    """Envia mensagens ao provider e retorna a resposta.
    
    Args:
        req: Requisição contendo messages, provider, model, etc.
        request: Objeto da FastAPI com contexto da requisição.
    
    Returns:
        ChatCompletionResponse com a mensagem do assistente.
    """
    from app.providers.router import ProviderRouter
    from app.core.logging_config import setup_logger

    logger = setup_logger("ia_api.chat_routes")

    router_instance = ProviderRouter(default_provider="local")
    provider = router_instance.get_provider(req.provider)

    result = provider.chat(req.messages)
    message = result.get("message", {"role": "assistant", "content": ""})

    response = {
        "id": f"chat_{req.model or 'default'}_{len(req.messages)}",
        "created_at": "2026-01-01T00:00:00Z",
        "provider": provider.provider_id,
        "model": req.model or "mock",
        "message": message,
        "usage": {"prompt_tokens": len(req.messages), "completion_tokens": 1},
    }

    logger.info(
        "Chat completion: provider=%s messages=%d",
        provider.provider_id,
        len(req.messages),
    )

    return response


@router.get("/v1/chat/models")
async def list_chat_models() -> dict:
    """Lista os modelos de chat disponíveis (simulado)."""
    return {
        "models": [
            {"id": "mock-local", "name": "Local Mock v0.1", "provider": "local"},
            {"id": "mock-online", "name": "Online Mock v0.1", "provider": "online"},
            {"id": "mock-corporate", "name": "Corporate Mock v0.1", "provider": "corporate"},
        ],
    }