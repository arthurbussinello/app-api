"""Rotas de saúde e monitoramento."""

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health(request: Request) -> dict:
    """Health check básico da aplicação.
    
    Returns:
        Dict com status "ok" e versão da aplicação.
    """
    return {
        "status": "ok",
        "app": "api-ia",
        "version": "0.1.0",
    }


@router.get("/v1/health")
async def health_v1(request: Request) -> dict:
    """Health check versão v1."""
    return {
        "status": "ok",
        "app": "api-ia",
        "version": "0.1.0",
        "endpoint": "/v1/health",
    }