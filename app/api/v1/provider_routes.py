"""Rotas para listar e consultar providers de IA."""

import logging

from api.v1 import router as v1_router
from schemas.common import ApiResponse
from providers.router import ProviderRouter

logger = logging.getLogger("ia_api.providers")

router_provider = ProviderRouter()


@v1_router.get("/providers", response_model=ApiResponse)
def list_providers():
    """Retorna lista de providers disponíveis."""
    providers = router_provider.list_providers()
    return {
        "success": True,
        "data": providers,
        "message": "Providers retrieved successfully",
    }