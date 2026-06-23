"""Agent Runner — executa agentes com limite de interações."""

import logging
from datetime import UTC, datetime

logger = logging.getLogger("ia_api.agent_runner")


class AgentRunner:
    """Executa um agente em loop simples com limite de iterações e timeout."""

    def __init__(self, max_iterations: int = 5):
        self.max_iterations = max_iterations

    def run(self, agent, input_data: str, params: dict | None = None) -> dict:
        """Executa o agente em loop até atingir o output final ou limite de iterações.
        
        Args:
            agent: Instância de um BaseAgent com método .run().
            input_data: Entrada inicial do agente.
            params: Parâmetros opcionais de configuração.
        
        Returns:
            Dict contendo 'output', 'iterations_used' e 'metadata'.
        """
        params = params or {}
        iterations = 0
        current_input = input_data

        logger.info(
            "Runner started for agent '%s' with max_iterations=%d",
            agent.agent_id,
            self.max_iterations,
        )

        while iterations < self.max_iterations:
            iterations += 1
            try:
                result = agent.run(current_input, params)
                output = result.get("output", str(result))
                logger.info(
                    "Agent '%s' iteration %d completed.",
                    agent.agent_id,
                    iterations,
                )

                # Verifica se o agente indicou que concluiu (chave '_done').
                if result.get("_done", False):
                    break

                # Atualiza input com resultado para próxima iteração.
                current_input = output

            except Exception as e:
                logger.error("Agent '%s' failed at iteration %d: %s", agent.agent_id, iterations, str(e))
                return {
                    "output": f"Erro no agente '{agent.agent_id}': {str(e)}",
                    "iterations_used": iterations,
                    "_done": True,
                    "error": str(e),
                }

        logger.info(
            "Agent '%s' finished after %d iteration(s).",
            agent.agent_id,
            iterations,
        )

        return {
            "output": current_input,
            "iterations_used": iterations,
            "_done": True,
            "metadata": {"completed_at": datetime.now(UTC).isoformat()},
        }