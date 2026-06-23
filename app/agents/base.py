"""Classe base abstrata para agentes."""

from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Base para todos os agentes do sistema."""

    @property
    def agent_id(self) -> str:
        return "base"

    @property
    def agent_name(self) -> str:
        return "Base Agent"

    @abstractmethod
    def run(self, input_data: str, params: dict | None = None) -> dict:
        """Executa o agente com os dados de entrada.
        
        Args:
            input_data: Entrada principal do agente.
            params: Parâmetros opcionais de configuração.
        
        Returns:
            Dict contendo 'output', 'iterations_used' e 'metadata'.
        """
        ...

    def info(self) -> dict:
        """Retorna informações básicas sobre o agente."""
        return {
            "agent_id": self.agent_id,
            "name": self.agent_name,
            "description": f"Agente {self.agent_name} da API IA",
        }