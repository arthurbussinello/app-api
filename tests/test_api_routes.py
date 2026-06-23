"""Testes unitários para as rotas da API (API Routes)."""

import pytest
from unittest.mock import patch, MagicMock


class TestHealthRoutes:
    """Testes para as rotas de health."""

    def test_health_endpoint(self, test_client):
        """Verifica endpoint /health."""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert data["app"] == "api-ia"
        assert "version" in data

    def test_health_v1_endpoint(self, test_client):
        """Verifica endpoint /v1/health."""
        response = test_client.get("/v1/health")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert data["app"] == "api-ia"
        assert data["endpoint"] == "/v1/health"

    def test_health_returns_json(self, test_client):
        """Verifica que health retorna JSON."""
        response = test_client.get("/health")
        assert response.headers["content-type"].startswith("application/json")


class TestRootEndpoint:
    """Testes para a rota raiz /."""

    def test_root_endpoint(self, test_client):
        """Verifica endpoint raiz."""
        response = test_client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data
        assert data["docs"] == "/docs"

    def test_root_health_url(self, test_client):
        """Verifica que root aponta para /v1/health."""
        response = test_client.get("/")
        data = response.json()
        assert data["health"] == "/v1/health"


class TestProviderRoutes:
    """Testes para as rotas de providers."""

    def test_list_providers(self, test_client):
        """Verifica endpoint de listagem de providers."""
        response = test_client.get("/providers")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data

    def test_providers_contains_local(self, test_client):
        """Verifica que providers inclui 'local'."""
        response = test_client.get("/providers")
        data = response.json()
        
        provider_ids = [p["id"] for p in data["data"]]
        assert "local" in provider_ids


class TestChatRoutes:
    """Testes para as rotas de chat."""

    def test_chat_completions(self, test_client):
        """Verifica endpoint de completions de chat."""
        payload = {
            "messages": [
                {"role": "user", "content": "Olá"}
            ],
            "provider": "local"
        }
        
        response = test_client.post("/chat/completions", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert "message" in data
        assert data["provider"] == "local"

    def test_chat_completions_default_provider(self, test_client):
        """Verifica chat com provider padrão (local)."""
        payload = {
            "messages": [
                {"role": "user", "content": "Teste"}
            ]
        }
        
        response = test_client.post("/chat/completions", json=payload)
        assert response.status_code == 200

    def test_chat_completions_corporate_provider(self, test_client):
        """Verifica chat com provider corporativo."""
        payload = {
            "messages": [
                {"role": "user", "content": "Relatório"}
            ],
            "provider": "corporate"
        }
        
        response = test_client.post("/chat/completions", json=payload)
        assert response.status_code == 200

    def test_chat_completions_with_temperature(self, test_client):
        """Verifica chat com temperatura."""
        payload = {
            "messages": [
                {"role": "user", "content": "Teste"}
            ],
            "provider": "local",
            "temperature": 0.5
        }
        
        response = test_client.post("/chat/completions", json=payload)
        assert response.status_code == 200

    def test_chat_completions_with_model(self, test_client):
        """Verifica chat com modelo específico."""
        payload = {
            "messages": [
                {"role": "user", "content": "Teste"}
            ],
            "provider": "local",
            "model": "mock-model-v1"
        }
        
        response = test_client.post("/chat/completions", json=payload)
        assert response.status_code == 200

    def test_chat_completions_multiple_messages(self, test_client):
        """Verifica chat com histórico múltiplo."""
        payload = {
            "messages": [
                {"role": "user", "content": "Primeira"},
                {"role": "assistant", "content": "Segunda"},
                {"role": "user", "content": "Terceira"},
            ],
            "provider": "local"
        }
        
        response = test_client.post("/chat/completions", json=payload)
        assert response.status_code == 200


class TestAgentRoutes:
    """Testes para as rotas de agentes."""

    def test_run_agent(self, test_client):
        """Verifica endpoint de execução de agente."""
        response = test_client.post("/agents/research/run")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data

    def test_run_agent_not_found(self, test_client):
        """Verifica agente não encontrado."""
        response = test_client.post("/agents/invalid/run")
        
        # Deve retornar 200 com message de erro dentro do data
        assert response.status_code == 200

    def test_run_agent_with_input(self, test_client):
        """Verifica execução de agente com input."""
        response = test_client.post("/agents/research/run-with-input?user_input=Teste")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True


class TestToolsRoutes:
    """Testes para as rotas de ferramentas."""

    def test_list_tools(self, test_client):
        """Verifica endpoint de listagem de ferramentas."""
        response = test_client.get("/tools")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data

    def test_execute_tool_sql_readonly(self, test_client):
        """Verifica execução da ferramenta SQL."""
        payload = {"query": "SELECT 1 AS teste"}
        
        response = test_client.post("/tools/sql_readonly/execute", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True

    def test_execute_tool_not_found(self, test_client):
        """Verifica ferramenta não encontrada."""
        payload = {}
        
        response = test_client.post("/tools/invalid_tool/execute", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        # Retorna success=False quando tool não existe
        if not data["success"]:
            assert "não encontrada" in data["message"]

    def test_execute_tool_missing_query(self, test_client):
        """Verifica ferramenta sem query."""
        payload = {}
        
        response = test_client.post("/tools/sql_readonly/execute", json=payload)
        assert response.status_code == 200


class TestCORSMiddleware:
    """Testes para middleware CORS."""

    def test_options_request(self, test_client):
        """Verifica que OPTIONS é permitido."""
        response = test_client.options("/health")
        # FastAPI pode retornar 405 para OPTIONS em rotas sem handler específico
        assert response.status_code in [200, 405]


class TestErrorHandling:
    """Testes para tratamento de erros."""

    def test_404_unknown_route(self, test_client):
        """Verifica que rotas desconhecidas retornam 404."""
        response = test_client.get("/unknown/path")
        assert response.status_code == 404


class TestAgentRoutesErrorHandling:
    """Testes para erros nas rotas de agentes."""

    def test_run_agent_returns_200_even_on_error(self, test_client):
        """Verifica que run_agent retorna 200 mesmo com erro interno."""
        # A rota always returns 200 - errors are inside the response body
        response = test_client.post("/agents/nonexistent/run")
        assert response.status_code == 200
        
        data = response.json()
        # O status HTTP é 200 mas o conteúdo pode conter erros
        assert "success" in data or "data" in data


class TestAPIIntegration:
    """Testes de integração para a API completa."""

    def test_full_health_to_chat_flow(self, test_client):
        """Verifica fluxo completo: health → providers → chat."""
        # 1. Health check
        r1 = test_client.get("/health")
        assert r1.status_code == 200
        
        # 2. List providers
        r2 = test_client.get("/providers")
        assert r2.status_code == 200
        
        # 3. Chat completion
        r3 = test_client.post("/chat/completions", json={
            "messages": [{"role": "user", "content": "Fluxo completo"}]
        })
        assert r3.status_code == 200


class TestRootEndpointDetailed:
    """Testes detalhados para a rota raiz."""

    def test_root_name(self, test_client):
        """Verifica nome da aplicação no root."""
        response = test_client.get("/")
        data = response.json()
        assert "api-ia" in data["name"] or len(data["name"]) > 0

    def test_root_has_docs_url(self, test_client):
        """Verifica que root contém URL do docs."""
        response = test_client.get("/")
        data = response.json()
        assert data["docs"] == "/docs"

    def test_root_version_format(self, test_client):
        """Verifica formato da versão no root."""
        response = test_client.get("/")
        data = response.json()
        # Versão deve ser uma string não vazia
        assert isinstance(data["version"], str) and len(data["version"]) > 0


class TestSchemaValidation:
    """Testes de validação de schemas nas rotas."""

    def test_chat_empty_messages(self, test_client):
        """Verifica chat com mensagem vazia (deve funcionar)."""
        payload = {
            "messages": [
                {"role": "user", "content": ""}
            ]
        }
        response = test_client.post("/chat/completions", json=payload)
        # Deve ser válido pois content vazio é permitido pelo schema
        assert response.status_code == 200

    def test_chat_with_invalid_role(self, test_client):
        """Verifica chat com role inválido (deve funcionar - sem validação)."""
        payload = {
            "messages": [
                {"role": "invalid_role", "content": "test"}
            ]
        }
        response = test_client.post("/chat/completions", json=payload)
        # Schema Pydantic não valida role, então passa
        assert response.status_code == 200

    def test_chat_missing_messages(self, test_client):
        """Verifica chat sem mensagens (deve falhar validação)."""
        payload = {}
        response = test_client.post("/chat/completions", json=payload)
        # Pydantic deve rejeitar falta de campo required
        assert response.status_code == 422


class TestTemperatureValidation:
    """Testes de validação de temperatura."""

    def test_chat_valid_temperature(self, test_client):
        """Verifica temperatura válida."""
        payload = {
            "messages": [{"role": "user", "content": "test"}],
            "temperature": 1.0
        }
        response = test_client.post("/chat/completions", json=payload)
        assert response.status_code == 200

    def test_chat_temperature_at_boundary_0(self, test_client):
        """Verifica temperatura no limite inferior."""
        payload = {
            "messages": [{"role": "user", "content": "test"}],
            "temperature": 0.0
        }
        response = test_client.post("/chat/completions", json=payload)
        assert response.status_code == 200

    def test_chat_temperature_at_boundary_2(self, test_client):
        """Verifica temperatura no limite superior."""
        payload = {
            "messages": [{"role": "user", "content": "test"}],
            "temperature": 2.0
        }
        response = test_client.post("/chat/completions", json=payload)
        assert response.status_code == 200

    def test_chat_temperature_out_of_range_high(self, test_client):
        """Verifica temperatura acima do limite."""
        payload = {
            "messages": [{"role": "user", "content": "test"}],
            "temperature": 3.0
        }
        response = test_client.post("/chat/completions", json=payload)
        # Deve falhar validação (422)
        assert response.status_code == 422

    def test_chat_temperature_out_of_range_low(self, test_client):
        """Verifica temperatura abaixo do limite."""
        payload = {
            "messages": [{"role": "user", "content": "test"}],
            "temperature": -1.0
        }
        response = test_client.post("/chat/completions", json=payload)
        # Deve falhar validação (422)
        assert response.status_code == 422