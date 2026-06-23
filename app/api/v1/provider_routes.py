"""Rotas para listar e consultar providers de IA."""

import logging

from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.providers.router import ProviderRouter

router = APIRouter()

logger = logging.getLogger("ia_api.providers")

router_provider = ProviderRouter()


@router.get("/providers", response_model=ApiResponse)
def list_providers():
    """Retorna lista de providers disponíveis."""
    providers = router_provider.list_providers()
    return {
        "success": True,
        "data": providers,
        "message": "Providers retrieved successfully",
    }