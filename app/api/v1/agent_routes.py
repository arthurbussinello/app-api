"""Rotas de agentes."""

import logging

from fastapi import Depends

from api.v1 import router as v1_router
from schemas.common import ApiResponse
from services.agent_service import agent_service


logger = logging.getLogger("ia_api.agents")


@v1_router.post("/agents/{agent_id}/run", response_model=ApiResponse)
def run_agent(agent_id: str):
    """Executa um agente pelo ID."""
    result = agent_service.run(agent_id)
    return {
        "success": True,
        "data": result,
        "message": f"Agente '{agent_id}' executado com sucesso",
    }


@v1_router.post("/agents/{agent_id}/run-with-input", response_model=ApiResponse)
def run_agent_with_input(agent_id: str, user_input: str = ""):
    """Executa um agente com input do usuário."""
    result = agent_service.run(agent_id, user_input=user_input)
    return {
        "success": True,
        "data": result,
        "message": f"Agente '{agent_id}' executado com sucesso",
    }