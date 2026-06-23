"""Schemas para ferramentas e tool registry."""

from pydantic import BaseModel


class ToolInfo(BaseModel):
    """Informações sobre uma ferramenta."""
    name: str
    description: str
    parameters: dict = {}


class ToolCallRequest(BaseModel):
    """Requisição para chamar uma ferramenta."""
    tool_name: str
    arguments: dict = {}


class ToolCallResponse(BaseModel):
    """Resposta após chamada de ferramenta."""
    tool_name: str
    result: str
    success: bool