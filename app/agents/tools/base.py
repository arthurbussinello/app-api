"""Ferramentas base para agentes."""

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger("ia_api.agent_tools")


class BaseTool(ABC):
    """Base para todas as ferramentas de agentes."""

    @property
    def tool_name(self) -> str:
        return "base_tool"

    @property
    def tool_description(self) -> str:
        return "Ferramenta base"

    @abstractmethod
    def execute(self, arguments: dict) -> str:
        """Executa a ferramenta com os argumentos fornecidos.

        Args:
            arguments: Dict com parâmetros de entrada.

        Returns:
            String com o resultado da execução.
        """
        ...

    def __call__(self, **kwargs) -> str:
        return self.execute(kwargs)


class SQLReadOnlyTool(BaseTool):
    """Ferramenta que executa queries SELECT no banco de dados (simulado)."""

    @property
    def tool_name(self) -> str:
        return "sql_readonly"

    @property
    def tool_description(self) -> str:
        return (
            "Executa query SQL SELECT no banco de dados. "
            "Apenas consultas de leitura são permitidas."
        )

    def execute(self, arguments: dict) -> str:
        """Executa uma query SELECT simulada.

        Em produção, conectaria ao SQL Server via pyodbc.

        Args:
            arguments: Dict com chave 'query' contendo a query SQL.

        Returns:
            String formatada com os resultados (simulados).
        """
        from ...sql.validators import validate_sql

        query = arguments.get("query", "")
        if not query:
            return "Erro: query não fornecida"

        # Validação de segurança.
        try:
            validate_sql(query)
        except Exception as e:
            logger.warning("SQL validation failed: %s", str(e))
            return f"Erro SQL: {str(e)}"

        # Em produção, executaria a query real aqui via pyodbc.
        # Para demonstração, retorna um resultado simulado.
        results = [
            {"row": 1, "data": "Resultado simulado (mock) para query SELECT"},
        ]
        return f"Query executada com sucesso ({len(results)} linha(s)):\n" + "\n".join(
            str(r) for r in results
        )


# Registro de ferramentas disponíveis.
TOOL_REGISTRY: dict[str, BaseTool] = {
    "sql_readonly": SQLReadOnlyTool(),
}


def get_tool(name: str):
    """Retorna uma ferramenta pelo nome."""
    return TOOL_REGISTRY.get(name.lower())


def list_tools() -> list[dict]:
    """Retorna lista de ferramentas disponíveis."""
    return [
        {"name": t.tool_name, "description": t.tool_description}
        for t in TOOL_REGISTRY.values()
    ]