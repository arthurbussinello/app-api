"""Rotas de ferramentas."""

import logging

from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.agents.tools.base import get_tool, list_tools

router = APIRouter()

logger = logging.getLogger("ia_api.tools")


@router.get("/tools", response_model=ApiResponse)
def tools_list():
    """Retorna lista de ferramentas disponíveis."""
    tools = list_tools()
    return {
        "success": True,
        "data": tools,
        "message": "Tools retrieved successfully",
    }


@router.post("/tools/{name}/execute", response_model=ApiResponse)
def execute_tool(name: str, params: dict | None = None):
    """Executa uma ferramenta pelo nome."""
    tool = get_tool(name)

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
            "data": {"result": result},
            "message": f"Ferramenta '{name}' executada com sucesso",
        }
    except Exception as exc:
        logger.error("Tool error → %s: %s", name, exc)
        return {
            "success": False,
            "data": None,
            "message": f"Erro ao executar ferramenta '{name}': {exc}",
        }