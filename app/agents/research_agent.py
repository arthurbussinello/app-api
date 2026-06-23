"""Research Agent — simula pesquisa usando ferramenta SQL read-only."""

import logging

from app.agents.base import BaseAgent
from app.agents.prompts import RESEARCH_AGENT_PROMPT
from app.agents.tools.base import get_tool, list_tools as _list_tools

logger = logging.getLogger("ia_api.research_agent")


class ResearchAgent(BaseAgent):
    """Agente que simula pesquisa utilizando ferramentas internas."""

    @property
    def agent_id(self) -> str:
        return "research"

    @property
    def agent_name(self) -> str:
        return "Research Agent"

    def run(self, input_data: str, params: dict | None = None) -> dict:
        """Executa a pesquisa simulada.

        1. Lista ferramentas disponíveis.
        2. Executa uma query SQL read-only simulada.
        3. Retorna resumo estruturado.

        Args:
            input_data: Texto da pergunta ou solicitação do usuário.
            params: Parâmetros opcionais (ex: {'table': 'nomes'}).

        Returns:
            Dict com output, metadata e _done=True para indicar conclusão.
        """
        params = params or {}
        tool_name = params.get("tool", "sql_readonly")

        # Passo 1: listar ferramentas disponíveis.
        available = _list_tools()
        tools_str = ", ".join(t["name"] for t in available)

        # Passo 2: executar ferramenta selecionada (simulada).
        tool = get_tool(tool_name)
        if tool is None:
            result_text = f"Ferramenta '{tool_name}' não encontrada. Disponíveis: {tools_str}"
        else:
            query = params.get("query", "SELECT 1 AS demo")
            result_text = tool.execute({"query": query})

        # Passo 3: montar resumo final.
        output = (
            f"[Research Agent]\n"
            f"Pergunta: {input_data}\n\n"
            f"Ferramentas disponíveis: {tools_str}\n"
            f"Executando: {tool_name}\n\n"
            f"Resultado:\n{result_text}"
        )

        logger.info(
            "ResearchAgent completed for input: '%s'",
            input_data[:80],
        )

        return {"output": output, "_done": True}