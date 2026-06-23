"""Rotas de providers de IA."""

from fastapi import APIRouter, Depends, Request

router = APIRouter()


@router.get("/v1/providers")
async def list_providers(request: Request) -> dict:
    """Lista os providers de IA disponíveis.
    
    Returns:
        Dict com lista de providers e contagem total.
    """
    from app.providers.router import ProviderRouter

    router_instance = ProviderRouter(default_provider="local")
    providers = router_instance.list_providers()

    return {
        "providers": providers,
        "total": len(providers),
    }


@router.get("/v1/providers/{provider_id}")
async def get_provider(provider_id: str, request: Request) -> dict:
    """Retorna informações de um provider específico.
    
    Args:
        provider_id: Identificador do provider (ex: 'local', 'online', 'corporate').
    
    Returns:
        Dict com status e dados do provider ou erro 404 se não encontrado.
    """
    from app.providers.router import ProviderRouter

    router_instance = ProviderRouter(default_provider="local")
    try:
        prov = router_instance.get_provider(provider_id)
        return {
            "status": "ok",
            "provider": {
                "id": prov.provider_id,
                "health": prov.health_check(),
            },
        }
    except Exception:
        return {"status": "error", "detail": f"Provider '{provider_id}' não encontrado"}, 404