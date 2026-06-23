"""Provider Router — centraliza a escolha e roteamento de providers."""

import logging

from app.providers.base import BaseProvider
from app.providers.corporate_provider import CorporateProvider
from app.providers.local_provider import LocalProvider
from app.providers.online_provider import OnlineProvider

logger = logging.getLogger("ia_api.provider_router")


class ProviderRouter:
    """Roteador que seleciona e instância o provider correto."""

    def __init__(self, default_provider: str = "local"):
        self._providers: dict[str, BaseProvider] = {}
        self.default_provider = default_provider
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Registra os providers disponíveis por padrão."""
        local = LocalProvider()
        self._providers[local.provider_id] = local
        logger.info("Registered provider: %s", local.provider_id)

        online = OnlineProvider()
        self._providers[online.provider_id] = online
        logger.info("Registered provider: %s", online.provider_id)

        corporate = CorporateProvider()
        self._providers[corporate.provider_id] = corporate
        logger.info("Registered provider: %s", corporate.provider_id)

    def register(self, name: str, provider: BaseProvider) -> None:
        """Registra um novo provider manualmente."""
        self._providers[name] = provider
        logger.info("Manually registered provider: %s", name)

    def get_provider(self, name: str | None = None) -> BaseProvider:
        """Retorna o provider pelo nome ou o padrão."""
        provider_name = (name or self.default_provider).lower()
        if provider_name not in self._providers:
            logger.warning(
                "Provider '%s' não encontrado, usando default '%s'",
                provider_name,
                self.default_provider,
            )
            provider_name = self.default_provider
        return self._providers[provider_name]

    def list_providers(self) -> list[dict]:
        """Retorna lista de providers disponíveis."""
        result = []
        for pid, prov in self._providers.items():
            hc = prov.health_check()
            result.append({
                "id": pid,
                "name": pid,
                "description": f"Provider {pid} da API IA",
                "enabled": hc.get("status") == "ok",
            })
        return result