"""Rotas de ferramentas."""

import logging

from api.v1 import router as v1_router
from schemas.common import ApiResponse


logger = logging.getLogger("ia_api.tools")


@v1_router.get("/tools", response_model=ApiResponse)
def list_tools():
    """Retorna lista de ferramentas disponíveis."""
    from agents.tools.base import ToolRegistry

    registry = ToolRegistry()
    tools = registry.list_tools()
    return {
        "success": True,
        "data": tools,
        "message": "Tools retrieved successfully",
    }


@v1_router.post("/tools/{name}/execute", response_model=ApiResponse)
def execute_tool(name: str, params: dict = None):
    """Executa uma ferramenta pelo nome."""
    from agents.tools.base import ToolRegistry

    registry = ToolRegistry()
    tool = registry.get_tool(name)

    if not tool:
        return {
            "success": False,
            "data": None,
            "message": f"Tool '{name}' não encontrada",
        }

    try:
        result = tool.execute(params or {})
        logger.info("Tool execute → %s", name)
        return {
            "success": True,
            "data": result,
            "message": f"Ferramenta '{name}' executada com sucesso",
        }
    except Exception as exc:
        logger.error("Tool error → %s: %s", name, exc)
        return {
            "success": False,
            "data": None,
            "message": f"Erro ao executar ferramenta '{name}': {exc}",
        }