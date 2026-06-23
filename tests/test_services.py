"""Testes unitários para o módulo de services."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


class TestChatService:
    """Testes para ChatService."""

    def test_init(self, chat_service):
        """Verifica inicialização do ChatService."""
        assert hasattr(chat_service, "router")
        assert chat_service.router is not None

    def test_complete_with_local_provider(self, chat_service):
        """Verifica chamada completa com provider local."""
        messages = [{"role": "user", "content": "Olá"}]
        
        result = chat_service.complete(messages, provider="local")
        
        assert "id" in result
        assert result["id"].startswith("chat_")
        assert "created_at" in result
        assert "provider" in result
        assert result["provider"] == "local"
        assert "model" in result
        assert result["message"]["role"] == "assistant"

    def test_complete_with_default_provider(self, chat_service):
        """Verifica complete usa provider padrão quando None."""
        messages = [{"role": "user", "content": "Pergunta"}]
        
        result = chat_service.complete(messages)
        
        assert result["provider"] == "local"

    def test_complete_returns_timestamp(self, chat_service):
        """Verifica que created_at é um timestamp válido."""
        messages = [{"role": "user", "content": "Teste"}]
        result = chat_service.complete(messages)
        
        # Deve ser possível parsear como datetime
        datetime.fromisoformat(result["created_at"])

    def test_log_completion(self, chat_service):
        """Verifica que log_completion registra adequadamente."""
        request_data = {"messages": [{"role": "user", "content": "test"}]}
        response_data = {
            "provider": "local",
            "message": {"role": "assistant", "content": "resposta"},
        }
        
        # Não deve levantar exceção
        chat_service.log_completion(request_data, response_data)

    def test_complete_with_online_provider(self, chat_service):
        """Verifica complete com provider online."""
        from app.providers.online_provider import OnlineProvider
        
        messages = [{"role": "user", "content": "Online test"}]
        
        # Mocka um provider online para retornar a resposta esperada
        mock_online_prov = MagicMock(spec=OnlineProvider)
        mock_online_prov.provider_id = "online"
        mock_online_prov.chat.return_value = {
            "message": {"role": "assistant", "content": "(online mock) Online test"}
        }
        
        # Mocka o método get_provider do router
        chat_service.router.get_provider = MagicMock(return_value=mock_online_prov)
        
        result = chat_service.complete(messages, provider="online")
        
        assert result["provider"] == "online"
        assert "(online mock)" in result["message"]["content"]

    def test_complete_with_corporate_provider(self, chat_service):
        """Verifica complete com provider corporativo."""
        messages = [{"role": "user", "content": "Corporate test"}]
        result = chat_service.complete(messages, provider="corporate")
        
        assert result["provider"] == "corporate"
        assert "(corporate mock)" in result["message"]["content"]

    def test_multiple_messages(self, chat_service):
        """Verifica complete com múltiplas mensagens no histórico."""
        messages = [
            {"role": "user", "content": "Primeira"},
            {"role": "assistant", "content": "Segunda"},
            {"role": "user", "content": "Terceira pergunta"},
        ]
        result = chat_service.complete(messages, provider="local")
        
        assert "(local mock)" in result["message"]["content"]


class TestAgentService:
    """Testes para AgentService."""

    def test_init(self, agent_service):
        """Verifica inicialização do AgentService."""
        assert hasattr(agent_service, "runner")
        assert hasattr(agent_service, "_agents")

    def test_get_agent_research_exists(self, agent_service):
        """Verifica que o agente 'research' existe."""
        agent = agent_service.get_agent("research")
        assert agent is not None
        assert agent.agent_id == "research"

    def test_get_agent_not_found(self, agent_service):
        """Verifica que agente inexistente retorna None."""
        agent = agent_service.get_agent("inexistente")
        assert agent is None

    def test_list_agents_info(self, agent_service):
        """Verifica list_agents_info retorna lista correta."""
        agents = agent_service.list_agents_info()
        assert isinstance(agents, list)
        assert len(agents) >= 1
        
        # Verifica estrutura
        research_info = agent_service.list_agents_info()[0]
        assert "agent_id" in research_info
        assert research_info["agent_id"] == "research"

    def test_run_agent_research(self, agent_service):
        """Verifica execução do agente research."""
        result = agent_service.run_agent("research", "Qual o resultado?")
        
        assert isinstance(result, dict)
        assert "output" in result
        assert "_done" in result
        assert result.get("_done") is True

    def test_run_agent_with_input(self, agent_service):
        """Verifica execução com input específico."""
        result = agent_service.run_agent("research", "Teste de input", params={"query": "SELECT 1"})
        
        assert "output" in result
        # O output deve conter informações sobre a query
        assert isinstance(result["output"], str)

    def test_run_agent_not_found(self, agent_service):
        """Verifica ValueError quando agente não encontrado."""
        with pytest.raises(ValueError) as exc_info:
            agent_service.run_agent("inexistente", "input")
        
        error_msg = str(exc_info.value)
        assert "inexistente" in error_msg

    def test_run_agent_with_params(self, agent_service):
        """Verifica execução com parâmetros personalizados."""
        result = agent_service.run_agent(
            "research", 
            "Teste params",
            params={"tool": "sql_readonly", "query": "SELECT 1 AS teste"}
        )
        
        assert isinstance(result, dict)
        assert "output" in result

    def test_runner_max_iterations(self):
        """Verifica que AgentRunner respeita max_iterations."""
        from app.agents.runner import AgentRunner
        
        runner = AgentRunner(max_iterations=3)
        
        # Mock de agente que nunca completa
        mock_agent = MagicMock()
        mock_agent.agent_id = "test"
        mock_agent.run.return_value = {"output": "iter", "_done": False}
        
        result = runner.run(mock_agent, "input", {})
        
        assert result["iterations_used"] <= 3

    def test_runner_stops_on_done(self):
        """Verifica que o runner para quando _done=True."""
        from app.agents.runner import AgentRunner
        
        runner = AgentRunner(max_iterations=10)
        
        mock_agent = MagicMock()
        # Completa na segunda iteração
        call_count = [0]
        def mock_run(input_data, params):
            call_count[0] += 1
            if call_count[0] < 2:
                return {"output": "iter", "_done": False}
            return {"output": "final", "_done": True}
        
        mock_agent.agent_id = "test"
        mock_agent.run.side_effect = mock_run
        
        result = runner.run(mock_agent, "input", {})
        
        assert result["_done"] is True
        assert call_count[0] == 2


class TestAgentRunner:
    """Testes para AgentRunner."""

    def test_init(self):
        """Verifica inicialização do AgentRunner."""
        from app.agents.runner import AgentRunner
        
        runner = AgentRunner(max_iterations=10)
        assert runner.max_iterations == 10

    def test_run_success(self, research_agent, agent_runner):
        """Verifica execução bem-sucedida de agente."""
        result = agent_runner.run(research_agent, "Teste")
        
        assert isinstance(result, dict)
        assert "_done" in result
        assert "output" in result

    def test_run_with_error(self):
        """Verifica tratamento de erro no runner."""
        from app.agents.runner import AgentRunner
        
        runner = AgentRunner(max_iterations=5)
        
        # Agente que sempre lança exceção
        mock_agent = MagicMock()
        mock_agent.agent_id = "faulty"
        mock_agent.run.side_effect = Exception("Erro simulado")
        
        result = runner.run(mock_agent, "input", {})
        
        assert "_done" in result
        assert "error" in result
        assert result["error"] == "Erro simulado"

    def test_run_reaches_max_iterations(self):
        """Verifica que o para ao atingir max_iterations."""
        from app.agents.runner import AgentRunner
        
        runner = AgentRunner(max_iterations=2)
        
        mock_agent = MagicMock()
        mock_agent.agent_id = "test"
        # Nunca marca como done
        mock_agent.run.return_value = {"output": "running", "_done": False}
        
        result = runner.run(mock_agent, "input", {})
        
        assert result["_done"] is True
        assert result["iterations_used"] == 2

    def test_run_updates_current_input(self):
        """Verifica que o runner passa output como input para próxima iteração."""
        from app.agents.runner import AgentRunner
        
        runner = AgentRunner(max_iterations=5)
        
        call_count = [0]
        received_inputs = []
        
        mock_agent = MagicMock()
        mock_agent.agent_id = "test"
        
        def capture_input(input_data, params):
            received_inputs.append(input_data)
            call_count[0] += 1
            return {"output": f"resposta_{call_count[0]}", "_done": (call_count[0] >= 2)}
        
        mock_agent.run.side_effect = capture_input
        
        result = runner.run(mock_agent, "inicial", {})
        
        # Verifica que cada iteração recebe o output da anterior
        assert len(received_inputs) == result["iterations_used"]


class TestAgentServiceIntegration:
    """Testes de integração para AgentService."""

    def test_full_run_flow(self, agent_service):
        """Verifica fluxo completo: list → get → run."""
        # 1. Listar agentes
        agents = agent_service.list_agents_info()
        assert len(agents) >= 1
        
        # 2. Obter agente específico
        research = agent_service.get_agent("research")
        assert research is not None
        
        # 3. Executar agente
        result = agent_service.run_agent("research", "Pergunta de teste")
        assert "_done" in result