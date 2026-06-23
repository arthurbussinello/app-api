"""Serviço de agentes — orquestra execução de agentes via runner."""

import logging
from datetime import UTC, datetime

from app.agents.research_agent import ResearchAgent
from app.agents.runner import AgentRunner

logger = logging.getLogger("ia_api.agent_service")


class AgentService:
    """Orquestra operações de agentes."""

    def __init__(self, runner: AgentRunner | None = None):
        self.runner = runner or AgentRunner(max_iterations=5)
        # Registra os agents disponíveis.
        self._agents: dict[str, object] = {
            "research": ResearchAgent(),
        }

    def get_agent(self, agent_id: str):
        """Retorna um agente pelo ID ou None."""
        return self._agents.get(agent_id)

    def list_agents_info(self) -> list[dict]:
        """Retorna informações sobre todos os agents registrados."""
        result = []
        for aid, agent in self._agents.items():
            info = agent.info() if hasattr(agent, "info") else {}
            info["agent_id"] = aid
            result.append(info)
        return result

    def run_agent(self, agent_id: str, input_data: str, params: dict | None = None) -> dict:
        """Executa um agente e retorna o resultado.
        
        Args:
            agent_id: Identificador do agente (ex: 'research').
            input_data: Entrada principal para o agente.
            params: Parâmetros opcionais de configuração.
        
        Returns:
            Dict com output, iterations_used e metadata.
        
        Raises:
            ValueError: Se o agent não for encontrado.
        """
        agent = self.get_agent(agent_id)
        if agent is None:
            available = ", ".join(self._agents.keys())
            raise ValueError(f"Agente '{agent_id}' não encontrado. Disponíveis: {available}")

        result = self.runner.run(agent, input_data, params or {})
        logger.info(
            "Agent '%s' run completed in %d iterations",
            agent_id,
            result.get("iterations_used", 0),
        )
        return result