"""Rotas de ferramentas."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class ToolExecuteRequest(BaseModel):
    """Requisição para executar uma ferramenta."""
    tool_name: str
    arguments: dict = {}


@router.post("/v1/tools/{tool_name}/execute")
async def execute_tool(
    tool_name: str,
    req: ToolExecuteRequest | None = None,
) -> dict:
    """Executa uma ferramenta com os argumentos fornecidos.
    
    Args:
        tool_name: Nome da ferramenta (ex: 'sql_readonly').
        req: Requisição contendo arguments opcionais.
    
    Returns:
        Dict com resultado da execução da ferramenta.
    """
    from app.agents.tools.base import get_tool, list_tools as _list_tools

    if not tool_name or not get_tool(tool_name):
        available = ", ".join(_list_tools())
        return {
            "status": "error",
            "detail": f"Ferramenta '{tool_name}' não encontrada. Disponíveis: {available}",
        }, 404

    tool = get_tool(tool_name)
    arguments = (req.arguments if req else {}).get("arguments", {})
    result = tool.execute(arguments)

    return {
        "status": "ok",
        "tool": tool.tool_name,
        "arguments": arguments,
        "result": result,
    }


@router.get("/v1/tools")
async def list_tools() -> dict:
    """Lista as ferramentas disponíveis."""
    from app.agents.tools.base import list_tools

    tools = list_tools()
    return {
        "tools": tools,
        "total": len(tools),
    }


@router.get("/v1/tools/{tool_name}")
async def get_tool(tool_name: str) -> dict:
    """Retorna informações sobre uma ferramenta específica."""
    from app.agents.tools.base import get_tool

    t = get_tool(tool_name)
    if t is None:
        return {"status": "error", "detail": f"Ferramenta '{tool_name}' não encontrada"}, 404

    return {
        "status": "ok",
        "tool": {
            "name": t.tool_name,
            "description": t.tool_description,
        },
    }