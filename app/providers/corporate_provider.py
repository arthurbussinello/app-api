"""Provider corporativo mockado — simula gateway interno da empresa."""

import logging

from ..config import settings
from .base import BaseProvider

logger = logging.getLogger("ia_api.providers.corporate")


class CorporateProvider(BaseProvider):
    """Provider que se conecta ao gateway de IA corporativo (simulado)."""

    @property
    def provider_id(self) -> str:
        return "corporate"

    def _is_available(self) -> bool:
        """Verifica se o provider corporativo está disponível."""
        # TODO: integrar com gateway interno da empresa
        return True

    def complete(self, prompt: str, **kwargs) -> dict:
        if not self._is_available():
            raise ConnectionError("Corporate provider is unavailable")
        logger.info(
            "CorporateProvider respondendo (mock): %s",
            prompt[:80],
        )
        return {
            "message": {
                "role": "assistant",
                "content": f"(corporate mock) {prompt}",
            },
        }

    def chat(self, messages: list[dict], **kwargs) -> dict:
        if not self._is_available():
            raise ConnectionError("Corporate provider is unavailable")
        logger.info(
            "CorporateProvider chat (mock): %d mensagens",
            len(messages),
        )
        last = messages[-1].get("content", "") if messages else ""
        return {
            "message": {
                "role": "assistant",
                "content": f"(corporate mock) {last}",
            },
        }