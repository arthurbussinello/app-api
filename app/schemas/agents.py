"""Schemas para operações de agentes."""

from typing import Optional

from pydantic import BaseModel


class AgentRunRequest(BaseModel):
    """Requisição para executar um agente."""
    input: str
    params: dict = {}


class AgentRunResponse(BaseModel):
    """Resposta após execução de um agente."""
    agent_id: str
    agent_name: str
    input: str
    output: str
    iterations_used: int
    success: bool
    metadata: dict = {}