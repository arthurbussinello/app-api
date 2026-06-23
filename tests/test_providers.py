"""Testes unitários para o módulo de providers."""

import pytest
from unittest.mock import patch, MagicMock


class TestBaseProvider:
    """Testes para a classe base BaseProvider (ABC)."""

    def test_provider_id_returns_base(self):
        """Verifica que provider_id retorna 'base' por padrão."""
        from app.providers.base import BaseProvider
        
        # Uma classe concreta deve ser criada para teste
        class TestProvider(BaseProvider):
            def complete(self, prompt: str, **kwargs) -> dict:
                return {"message": {"role": "assistant", "content": prompt}}
            
            def chat(self, messages: list[dict], **kwargs) -> dict:
                return {"message": {"role": "assistant", "content": ""}}
        
        provider = TestProvider()
        assert provider.provider_id == "base"

    def test_health_check_default(self):
        """Verifica que health_check retorna status 'ok' por padrão."""
        from app.providers.base import BaseProvider
        
        class TestProvider(BaseProvider):
            def complete(self, prompt: str, **kwargs) -> dict:
                return {"message": {"role": "assistant", "content": prompt}}
            
            def chat(self, messages: list[dict], **kwargs) -> dict:
                return {"message": {"role": "assistant", "content": ""}}
        
        provider = TestProvider()
        health = provider.health_check()
        assert health["status"] == "ok"
        assert health["provider"] == "base"

    def test_abstract_methods_not_implemented(self):
        """Verifica que complete e chat são métodos abstratos."""
        from app.providers.base import BaseProvider
        
        # Tentar instanciar diretamente deve falhar
        with pytest.raises(TypeError):
            BaseProvider()


class TestLocalProvider:
    """Testes para LocalProvider."""

    def test_provider_id(self, local_provider):
        """Verifica provider_id é 'local'."""
        assert local_provider.provider_id == "local"

    def test_complete_returns_mock_response(self, local_provider):
        """Verifica que complete retorna resposta mockada correta."""
        result = local_provider.complete("Olá mundo")
        assert "message" in result
        assert result["message"]["role"] == "assistant"
        assert "(local mock)" in result["message"]["content"]
        assert "Olá mundo" in result["message"]["content"]

    def test_complete_with_long_prompt(self, local_provider):
        """Verifica complete com prompts longos."""
        long_prompt = "Palavra " * 100
        result = local_provider.complete(long_prompt)
        assert "(local mock)" in result["message"]["content"]

    def test_chat_with_messages(self, local_provider):
        """Verifica que chat processa lista de mensagens."""
        messages = [
            {"role": "user", "content": "Olá"},
            {"role": "assistant", "content": "Oi!"},
            {"role": "user", "content": "Tudo bem?"},
        ]
        result = local_provider.chat(messages)
        assert "message" in result
        assert "(local mock)" in result["message"]["content"]

    def test_chat_with_empty_messages(self, local_provider):
        """Verifica chat com lista vazia de mensagens."""
        result = local_provider.chat([])
        assert "message" in result
        assert result["message"]["role"] == "assistant"

    def test_chat_with_single_message(self, local_provider):
        """Verifica chat com uma única mensagem."""
        messages = [{"role": "user", "content": "Teste"}]
        result = local_provider.chat(messages)
        assert "(local mock)" in result["message"]["content"]

    def test_health_check(self, local_provider):
        """Verifica health_check do LocalProvider."""
        health = local_provider.health_check()
        assert health["status"] == "ok"
        assert health["provider"] == "local"


class TestOnlineProvider:
    """Testes para OnlineProvider."""

    def test_provider_id(self):
        """Verifica provider_id é 'online'."""
        from app.providers.online_provider import OnlineProvider
        provider = OnlineProvider()
        assert provider.provider_id == "online"

    def test_complete_returns_mock_response(self):
        """Verifica complete retorna resposta mockada."""
        from app.providers import online_provider as online_module
        
        # Patcha settings no namespace do módulo para habilitar o online provider
        class FakeSettings:
            provider_online_enabled = True
            
        fake = FakeSettings()
        with patch.object(online_module, 'settings', fake):
            provider = online_module.OnlineProvider()
            result = provider.complete("Pergunta online")
            assert "message" in result
            assert "(online mock)" in result["message"]["content"]

    def test_chat_with_messages(self):
        """Verifica chat processa mensagens."""
        from app.providers import online_provider as online_module
        
        class FakeSettings:
            provider_online_enabled = True
            
        fake = FakeSettings()
        with patch.object(online_module, 'settings', fake):
            provider = online_module.OnlineProvider()
            messages = [
                {"role": "user", "content": "Pergunta"},
                {"role": "assistant", "content": "Resposta"},
            ]
            result = provider.chat(messages)
            assert "(online mock)" in result["message"]["content"]

    def test_complete_raises_when_disabled(self):
        """Verifica que complete levanta ConnectionError quando disabled."""
        from app.providers.online_provider import OnlineProvider
        
        with patch.object(OnlineProvider, '_is_available', return_value=False):
            provider = OnlineProvider()
            with pytest.raises(ConnectionError) as exc_info:
                provider.complete("test")
            assert "Online provider is disabled" in str(exc_info.value)

    def test_chat_raises_when_disabled(self):
        """Verifica que chat levanta ConnectionError quando disabled."""
        from app.providers.online_provider import OnlineProvider
        
        with patch.object(OnlineProvider, '_is_available', return_value=False):
            provider = OnlineProvider()
            with pytest.raises(ConnectionError) as exc_info:
                provider.chat([{"role": "user", "content": "test"}])
            assert "Online provider is disabled" in str(exc_info.value)


class TestCorporateProvider:
    """Testes para CorporateProvider."""

    def test_provider_id(self):
        """Verifica provider_id é 'corporate'."""
        from app.providers.corporate_provider import CorporateProvider
        provider = CorporateProvider()
        assert provider.provider_id == "corporate"

    def test_complete_returns_mock_response(self, corporate_provider):
        """Verifica complete retorna resposta mockada."""
        result = corporate_provider.complete("Pergunta corporativa")
        assert "message" in result
        assert "(corporate mock)" in result["message"]["content"]

    def test_chat_with_messages(self, corporate_provider):
        """Verifica chat processa mensagens."""
        messages = [
            {"role": "user", "content": "Relatório"},
        ]
        result = corporate_provider.chat(messages)
        assert "(corporate mock)" in result["message"]["content"]

    def test_complete_raises_when_unavailable(self):
        """Verifica que complete levanta ConnectionError quando unavailable."""
        from app.providers.corporate_provider import CorporateProvider
        
        with patch.object(CorporateProvider, '_is_available', return_value=False):
            provider = CorporateProvider()
            with pytest.raises(ConnectionError) as exc_info:
                provider.complete("test")
            assert "Corporate provider is unavailable" in str(exc_info.value)


class TestProviderRouter:
    """Testes para ProviderRouter."""

    def test_default_provider_is_local(self, provider_router):
        """Verifica provider padrão é 'local'."""
        default = provider_router.get_provider()
        assert default.provider_id == "local"

    def test_get_local_provider(self, provider_router):
        """Verifica obtenção do provider local."""
        prov = provider_router.get_provider("local")
        assert prov.provider_id == "local"

    def test_get_online_provider(self, provider_router):
        """Verifica obtenção do provider online."""
        # Patcha _is_available para online provider
        with patch('app.providers.online_provider.OnlineProvider._is_available', return_value=True):
            prov = provider_router.get_provider("online")
            assert prov.provider_id == "online"

    def test_get_corporate_provider(self, provider_router):
        """Verifica obtenção do provider corporativo."""
        prov = provider_router.get_provider("corporate")
        assert prov.provider_id == "corporate"

    def test_get_unknown_provider_returns_default(self, provider_router):
        """Verifica que provider desconhecido retorna o padrão."""
        with patch("app.providers.router.logger"):
            prov = provider_router.get_provider("inexistente")
            assert prov.provider_id == "local"

    def test_list_providers(self, provider_router):
        """Verifica list_providers retorna lista de dicts."""
        providers = provider_router.list_providers()
        assert isinstance(providers, list)
        assert len(providers) >= 3
        
        # Verifica estrutura dos dados
        local_ids = [p["id"] for p in providers]
        assert "local" in local_ids
        assert "online" in local_ids
        assert "corporate" in local_ids

    def test_register_new_provider(self, provider_router):
        """Verifica registro manual de novo provider."""
        from app.providers.base import BaseProvider
        
        class CustomProvider(BaseProvider):
            @property
            def provider_id(self) -> str:
                return "custom"
            
            def complete(self, prompt: str, **kwargs) -> dict:
                return {"message": {"role": "assistant", "content": f"(custom) {prompt}"}}
            
            def chat(self, messages: list[dict], **kwargs) -> dict:
                return {"message": {"role": "assistant", "content": "(custom chat)"}}
        
        provider_router.register("custom", CustomProvider())
        prov = provider_router.get_provider("custom")
        assert prov.provider_id == "custom"

    def test_register_case_insensitive(self, provider_router):
        """Verifica que o nome do provider é case-insensitive."""
        prov = provider_router.get_provider("LOCAL")
        assert prov.provider_id == "local"


class TestProviderIntegration:
    """Testes de integração para providers com router."""

    def test_chat_flow_via_router(self, provider_router):
        """Verifica fluxo completo de chat via router."""
        messages = [
            {"role": "user", "content": "Qual é o resultado?"},
        ]
        
        # Usa o router para obter provider e executar chat
        prov = provider_router.get_provider("local")
        result = prov.chat(messages)
        
        assert "message" in result
        assert "(local mock)" in result["message"]["content"]

    def test_health_check_all_providers(self, provider_router):
        """Verifica health check de todos os providers registrados."""
        for pid in ["local", "online", "corporate"]:
            prov = provider_router.get_provider(pid)
            health = prov.health_check()
            assert health["status"] == "ok"
            assert health["provider"] == pid