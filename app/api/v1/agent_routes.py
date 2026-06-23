"""Rotas de agentes."""

import logging

from fastapi import APIRouter, Depends

from app.schemas.common import ApiResponse
from app.services.agent_service import AgentService, AgentRunner

router = APIRouter()

logger = logging.getLogger("ia_api.agents")


agent_service = AgentService(runner=AgentRunner(max_iterations=5))


@router.post("/agents/{agent_id}/run", response_model=ApiResponse)
def run_agent(agent_id: str):
    """Executa um agente pelo ID."""
    result = agent_service.run(agent_id)
    return {
        "success": True,
        "data": result,
        "message": f"Agente '{agent_id}' executado com sucesso",
    }


@router.post("/agents/{agent_id}/run-with-input", response_model=ApiResponse)
def run_agent_with_input(agent_id: str, user_input: str = ""):
    """Executa um agente com input do usuário."""
    result = agent_service.run(agent_id, user_input=user_input)
    return {
        "success": True,
        "data": result,
        "message": f"Agente '{agent_id}' executado com sucesso",
    }