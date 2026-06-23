"""Provider local — respostas mockadas sem dependências externas."""

import random
from typing import Optional


class LocalProvider(BaseProvider):
    """Provider que simula respostas de IA localmente."""

    @property
    def provider_id(self) -> str:
        return "local"

    # Respostas fixas para demonstração.
    _RESPONSES = [
        "Resposta mockada do provider local: operação concluída com sucesso.",
        "Provider local ativo. Nenhum modelo de IA real foi invocado.",
        "Simulação local: o prompt foi processado internamente.",
        "Resposta gerada pelo LocalProvider — sem conexão externa.",
    ]

    def complete(self, prompt: str, **kwargs) -> str:
        """Retorna uma resposta mockada aleatória."""
        return random.choice(self._RESPONSES)

    def chat(self, messages: list[dict], **kwargs) -> dict:
        """Retorna uma mensagem mockada baseada nas entradas."""
        last = messages[-1] if messages else {}
        content = (
            f"Resposta local ao prompt: '{last.get('content', '')}'"
        )
        return {"message": {"role": "assistant", "content": content}}

    def health_check(self) -> dict:
        """Sempre saudável — não depende de rede."""
        return {"status": "ok", "provider": self.provider_id}