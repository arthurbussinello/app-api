"""Classe base abstrata para providers de IA."""

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Base para todos os providers de IA."""

    @property
    def provider_id(self) -> str:
        return "base"

    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        """Retorna uma resposta simples a partir de um prompt."""
        ...

    @abstractmethod
    def chat(self, messages: list[dict], **kwargs) -> dict:
        """Retorna uma resposta de chat a partir de mensagens.
        
        Args:
            messages: Lista de dicts com 'role' e 'content'.
        
        Returns:
            Dict com chave 'message' contendo {'role': str, 'content': str}.
        """
        ...

    def health_check(self) -> dict:
        """Retorna status do provider."""
        return {"status": "ok", "provider": self.provider_id}