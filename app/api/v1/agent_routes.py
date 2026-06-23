"""Rotas de agentes."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class AgentRunRequest(BaseModel):
    """Requisição para executar um agente."""
    input: str
    params: dict = {}


@router.post("/v1/agents/{agent_id}/run")
async def run_agent(
    agent_id: str,
    req: AgentRunRequest,
    request: Request,
) -> dict:
    """Executa um agente com a entrada fornecida.
    
    Args:
        agent_id: Identificador do agente (ex: 'research').
        req: Requisição contendo input e params opcionais.
        request: Objeto da FastAPI com contexto da requisição.
    
    Returns:
        Dict com output, iterations_used e metadata do agente.
    """
    from app.services.agent_service import AgentService
    from app.core.logging_config import setup_logger

    logger = setup_logger("ia_api.agent_routes")

    agent_service = AgentService()

    try:
        result = agent_service.run_agent(agent_id, req.input, req.params)
        response = {
            "agent_id": agent_id,
            "input": req.input,
            "output": result.get("output", ""),
            "iterations_used": result.get("iterations_used", 0),
            "success": True,
            "metadata": result.get("metadata", {}),
        }
        logger.info("Agent '%s' run completed: %d iterations", agent_id, result.get("iterations_used", 0))
        return response

    except ValueError as e:
        return {"status": "error", "detail": str(e)}, 404


@router.get("/v1/agents")
async def list_agents() -> dict:
    """Lista os agentes disponíveis."""
    from app.services.agent_service import AgentService

    agent_service = AgentService()
    agents = agent_service.list_agents_info()

    return {
        "agents": agents,
        "total": len(agents),
    }


@router.get("/v1/agents/{agent_id}")
async def get_agent(agent_id: str) -> dict:
    """Retorna informações sobre um agente específico."""
    from app.services.agent_service import AgentService

    agent_service = AgentService()
    agent = agent_service.get_agent(agent_id)

    if agent is None:
        return {"status": "error", "detail": f"Agente '{agent_id}' não encontrado"}, 404

    info = agent.info() if hasattr(agent, "info") else {}
    info["agent_id"] = agent_id
    return {
        "status": "ok",
        "agent": info,
    }