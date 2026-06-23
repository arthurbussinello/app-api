"""Serviço de chat — orquestra chamadas ao provider."""

import logging
from datetime import UTC, datetime

from app.providers.router import ProviderRouter

logger = logging.getLogger("ia_api.chat_service")


class ChatService:
    """Orquestra operações de chat com os providers."""

    def __init__(self, router: ProviderRouter):
        self.router = router

    def complete(
        self,
        messages: list[dict],
        provider: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
    ) -> dict:
        """Envia mensagens ao provider e retorna a resposta.

        Args:
            messages: Lista de dicts com 'role' e 'content'.
            provider: Nome do provider ou None para usar o padrão.
            model: Modelo específico ou None para usar o padrão do provider.
            temperature: Temperatura de aleatoriedade (0-2).

        Returns:
            Dict contendo response_id, created_at, provider, model e message.
        """
        prov = self.router.get_provider(provider)
        logger.info(
            "ChatService calling provider '%s' with %d messages",
            prov.provider_id,
            len(messages),
        )

        result = prov.chat(messages)
        response_msg = result.get("message", {"role": "assistant", "content": ""})

        return {
            "id": f"chat_{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}",
            "created_at": datetime.now(UTC).isoformat(),
            "provider": prov.provider_id,
            "model": "mock",
            "message": response_msg,
        }

    def log_completion(self, request: dict, response: dict) -> None:
        """Registra o histórico de completions (futuro: persistir no DB)."""
        logger.info(
            "Chat completion logged: provider=%s messages=%d",
            response.get("provider"),
            len(request.get("messages", [])),
        )