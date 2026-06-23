"""Provider local mockado — sem conexão externa."""

import logging

from app.providers.base import BaseProvider

logger = logging.getLogger("ia_api.providers.local")


class LocalProvider(BaseProvider):
    """Provider que retorna respostas mockadas localmente."""

    @property
    def provider_id(self) -> str:
        return "local"

    def complete(self, prompt: str, **kwargs) -> dict:
        logger.info("LocalProvider respondendo (mock): %s", prompt[:80])
        return {
            "message": {"role": "assistant", "content": f"(local mock) {prompt}"},
        }

    def chat(self, messages: list[dict], **kwargs) -> dict:
        logger.info("LocalProvider chat (mock): %d mensagens", len(messages))
        last = messages[-1].get("content", "") if messages else ""
        return {
            "message": {"role": "assistant", "content": f"(local mock) {last}"},
        }