"""Pytest configuration e fixtures para os testes unitários."""

import sys
import pytest
from unittest.mock import MagicMock, patch, Mock
from pathlib import Path

# Adiciona o diretório raiz ao Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


# --- Fixture: LocalProvider mockado ---
@pytest.fixture
def local_provider():
    """Retorna uma instância do LocalProvider."""
    from app.providers.local_provider import LocalProvider
    return LocalProvider()


# --- Fixture: OnlineProvider mockado ---
@pytest.fixture
def online_provider():
    """Retorna uma instância do OnlineProvider com _is_available=True."""
    from app.providers.online_provider import OnlineProvider
    
    # Patcha o settings diretamente para permitir o provider online
    with patch('app.config.settings') as mock_settings:
        mock_settings.provider_online_enabled = True
        
        class FakeSettingsOnline:
            app_host = "0.0.0.0"
            app_port = 8000
            app_debug = True
            app_name = "api-ia-test"
            version = "0.1.0-test"
            provider_default = "local"
            provider_local_enabled = True
            provider_online_enabled = True
            provider_corporate_enabled = True
            provider_online_base_url = "https://api.example.com/v1"
            provider_online_api_key = "sk-test-online"
            provider_corporate_base_url = "https://ia.corporate.internal/api/v1"
            provider_corporate_api_key = "corporate-api-key-test"
            sql_server = "localhost"
            sql_database = "test_db"
            sql_port = 1433
            sql_user = "db_reader"
            sql_password = "db_test_pass"
            agent_max_iterations = 5
            agent_timeout_seconds = 60
        
        with patch('app.providers.online_provider.settings', FakeSettingsOnline()):
            provider = OnlineProvider()
            return provider


# --- Fixture: CorporateProvider mockado ---
@pytest.fixture
def corporate_provider():
    """Retorna uma instância do CorporateProvider."""
    from app.providers.corporate_provider import CorporateProvider
    
    class FakeSettingsCorporate:
        app_host = "0.0.0.0"
        app_port = 8000
        app_debug = True
        app_name = "api-ia-test"
        version = "0.1.0-test"
        provider_default = "local"
        provider_local_enabled = True
        provider_online_enabled = False
        provider_corporate_enabled = True
        provider_online_base_url = "https://api.example.com/v1"
        provider_online_api_key = "sk-test-online"
        provider_corporate_base_url = "https://ia.corporate.internal/api/v1"
        provider_corporate_api_key = "corporate-api-key-test"
        sql_server = "localhost"
        sql_database = "test_db"
        sql_port = 1433
        sql_user = "db_reader"
        sql_password = "db_test_pass"
        agent_max_iterations = 5
        agent_timeout_seconds = 60
    
    with patch('app.providers.corporate_provider.settings', FakeSettingsCorporate()):
        provider = CorporateProvider()
        return provider


# --- Fixture: ProviderRouter ---
@pytest.fixture
def provider_router():
    """Retorna uma instância do ProviderRouter."""
    from app.providers.router import ProviderRouter
    return ProviderRouter(default_provider="local")


# --- Fixture: ChatService mockado ---
@pytest.fixture
def chat_service(provider_router):
    """Retorna uma instância do ChatService."""
    from app.services.chat_service import ChatService
    return ChatService(router=provider_router)


# --- Fixture: AgentRunner ---
@pytest.fixture
def agent_runner():
    """Retorna uma instância do AgentRunner."""
    from app.agents.runner import AgentRunner
    return AgentRunner(max_iterations=5)


# --- Fixture: AgentService mockado ---
@pytest.fixture
def agent_service(agent_runner):
    """Retorna uma instância do AgentService."""
    from app.services.agent_service import AgentService
    return AgentService(runner=agent_runner)


# --- Fixture: FastAPI Test Client para rotas ---
@pytest.fixture
def test_client():
    """Retorna um client de teste FastAPI para testar as rotas HTTP."""
    from fastapi.testclient import TestClient
    
    # Mock settings ANTES de importar app
    with patch('app.config.settings') as mock:
        mock.app_host = "0.0.0.0"
        mock.app_port = 8000
        mock.app_debug = True
        mock.app_name = "api-ia-test"
        mock.version = "0.1.0-test"
        mock.provider_default = "local"
        mock.provider_local_enabled = True
        mock.provider_online_enabled = False
        mock.provider_corporate_enabled = True
        mock.provider_online_base_url = "https://api.example.com/v1"
        mock.provider_online_api_key = "sk-test-online"
        mock.provider_corporate_base_url = "https://ia.corporate.internal/api/v1"
        mock.provider_corporate_api_key = "corporate-api-key-test"
        mock.sql_server = "localhost"
        mock.sql_database = "test_db"
        mock.sql_port = 1433
        mock.sql_user = "db_reader"
        mock.sql_password = "db_test_pass"
        mock.agent_max_iterations = 5
        mock.agent_timeout_seconds = 60
        
        from app.main import app as fastapi_app
        with TestClient(app=fastapi_app) as client:
            yield client


# --- Fixture: ResearchAgent mockado ---
@pytest.fixture
def research_agent():
    """Retorna uma instância do ResearchAgent."""
    from app.agents.research_agent import ResearchAgent
    return ResearchAgent()


# --- Fixture: SQLReadOnlyTool ---
@pytest.fixture
def sql_readonly_tool():
    """Retorna uma instância da ferramenta SQL read-only."""
    from app.agents.tools.base import SQLReadOnlyTool
    return SQLReadOnlyTool()


# --- Fixture: BaseTool mockado ---
class MockTool:
    """Ferramenta mockada para testes."""
    
    @property
    def tool_name(self) -> str:
        return "mock_tool"
    
    @property
    def tool_description(self) -> str:
        return "Ferramenta mockada para testes"
    
    def execute(self, arguments: dict) -> str:
        return "Resultado mockado da ferramenta"


@pytest.fixture
def mock_tool():
    """Retorna uma instância de MockTool."""
    return MockTool()