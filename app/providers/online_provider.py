"""Provider online mockado — simula conexão com API externa."""

import logging

from app.config import settings
from app.providers.base import BaseProvider

logger = logging.getLogger("ia_api.providers.online")


class OnlineProvider(BaseProvider):
    """Provider que se conecta a uma API de IA online (simulado)."""

    @property
    def provider_id(self) -> str:
        return "online"

    def _is_available(self) -> bool:
        """Verifica se o provider online está habilitado."""
        return settings.provider_online_enabled

    def complete(self, prompt: str, **kwargs) -> dict:
        if not self._is_available():
            raise ConnectionError("Online provider is disabled. Set PROVIDER_ONLINE_ENABLED=true")
        logger.info("OnlineProvider respondendo (mock): %s", prompt[:80])
        return {
            "message": {"role": "assistant", "content": f"(online mock) {prompt}"},
        }

    def chat(self, messages: list[dict], **kwargs) -> dict:
        if not self._is_available():
            raise ConnectionError("Online provider is disabled. Set PROVIDER_ONLINE_ENABLED=true")
        logger.info("OnlineProvider chat (mock): %d mensagens", len(messages))
        last = messages[-1].get("content", "") if messages else ""
        return {
            "message": {"role": "assistant", "content": f"(online mock) {last}"},
        }