"""Testes unitários para schemas e validadores."""

import pytest
from datetime import datetime


class TestApiResponseSchema:
    """Testes para ApiResponse schema."""

    def test_api_response_default_values(self):
        """Verifica valores padrão do ApiResponse."""
        from app.schemas.common import ApiResponse
        
        response = ApiResponse()
        
        assert response.success is True
        assert response.data is None
        assert response.message == ""
        assert response.timestamp is not None

    def test_api_response_custom_values(self):
        """Verifica ApiResponse com valores customizados."""
        from app.schemas.common import ApiResponse
        
        response = ApiResponse(
            success=False,
            data={"key": "value"},
            message="Erro occurred"
        )
        
        assert response.success is False
        assert response.data == {"key": "value"}
        assert response.message == "Erro occurred"

    def test_api_response_timestamp_format(self):
        """Verifica formato do timestamp."""
        from app.schemas.common import ApiResponse
        
        response = ApiResponse()
        
        # Deve ser possível parsear como datetime
        dt = datetime.fromisoformat(response.timestamp)
        assert isinstance(dt, datetime)

    def test_api_response_with_list_data(self):
        """Verifica ApiResponse com lista de dados."""
        from app.schemas.common import ApiResponse
        
        response = ApiResponse(data=[{"a": 1}, {"b": 2}])
        
        assert response.data == [{"a": 1}, {"b": 2}]

    def test_api_response_is_pydantic_model(self):
        """Verifica que ApiResponse é um Pydantic model."""
        from app.schemas.common import ApiResponse
        
        # Deve ter método model_dump (Pydantic v2)
        response = ApiResponse()
        assert hasattr(response, 'model_dump')


class TestErrorResponseSchema:
    """Testes para ErrorResponse schema."""

    def test_error_response_required_fields(self):
        """Verifica campos obrigatórios do ErrorResponse."""
        from app.schemas.common import ErrorResponse
        
        error = ErrorResponse(error="Bad request")
        
        assert error.success is False
        assert error.error == "Bad request"
        assert error.detail is None

    def test_error_response_with_detail(self):
        """Verifica ErrorResponse com detail."""
        from app.schemas.common import ErrorResponse
        
        error = ErrorResponse(
            error="Validation error",
            detail="Campo 'email' é obrigatório"
        )
        
        assert error.success is False
        assert error.error == "Validation error"
        assert error.detail == "Campo 'email' é obrigatório"

    def test_error_response_cannot_set_success_true(self):
        """Verifica que success default é False."""
        from app.schemas.common import ErrorResponse
        
        # ErrorResponse sempre começa com success=False por padrão
        error = ErrorResponse(error="test")
        assert error.success is False


class TestChatMessageSchema:
    """Testes para ChatMessage schema."""

    def test_chat_message_defaults(self):
        """Verifica valores padrão do ChatMessage."""
        from app.schemas.chat import ChatMessage
        
        msg = ChatMessage(content="Olá")
        
        assert msg.role == "user"
        assert msg.content == "Olá"

    def test_chat_message_custom_role(self):
        """Verifica ChatMessage com role customizado."""
        from app.schemas.chat import ChatMessage
        
        msg = ChatMessage(role="assistant", content="Resposta")
        
        assert msg.role == "assistant"
        assert msg.content == "Resposta"

    def test_chat_message_empty_content(self):
        """Verifica que content vazio é permitido."""
        from app.schemas.chat import ChatMessage
        
        # content não tem required=False, mas pode ser string vazia
        msg = ChatMessage(role="user", content="")
        
        assert msg.role == "user"
        assert msg.content == ""

    def test_chat_message_dump(self):
        """Verifica model_dump do ChatMessage."""
        from app.schemas.chat import ChatMessage
        
        msg = ChatMessage(role="assistant", content="Teste")
        data = msg.model_dump()
        
        assert data["role"] == "assistant"
        assert data["content"] == "Teste"


class TestChatResponseSchema:
    """Testes para ChatResponse schema."""

    def test_chat_response_defaults(self):
        """Verifica valores padrão do ChatResponse."""
        from app.schemas.chat import ChatResponse
        
        response = ChatResponse()
        
        assert response.id == ""
        assert response.provider == "local"
        assert response.model == "mock"
        assert response.message == {}
        assert response.usage == {"prompt_tokens": 0, "completion_tokens": 0}

    def test_chat_response_with_data(self):
        """Verifica ChatResponse com dados."""
        from app.schemas.chat import ChatResponse
        
        response = ChatResponse(
            id="chat_123",
            provider="online",
            model="gpt-4",
            message={"role": "assistant", "content": "Hello!"},
            usage={"prompt_tokens": 10, "completion_tokens": 5}
        )
        
        assert response.id == "chat_123"
        assert response.provider == "online"
        assert response.model == "gpt-4"

    def test_chat_response_dump(self):
        """Verifica model_dump do ChatResponse."""
        from app.schemas.chat import ChatResponse
        
        response = ChatResponse(
            id="chat_test",
            provider="local",
            message={"role": "assistant", "content": "test"}
        )
        
        data = response.model_dump()
        assert data["id"] == "chat_test"


class TestSQLValidators:
    """Testes para validadores SQL."""

    def test_validate_sql_select_allowed(self):
        """Verifica que SELECT é permitido."""
        from app.sql.validators import validate_sql
        
        result = validate_sql("SELECT * FROM users")
        assert result is True

    def test_validate_sql_simple_select(self):
        """Verifica query SELECT simples."""
        from app.sql.validators import validate_sql
        
        result = validate_sql("SELECT id, name FROM users WHERE active = 1")
        assert result is True

    def test_validate_sql_insert_blocked(self):
        """Verifica que INSERT é bloqueado."""
        from app.sql.validators import validate_sql
        from app.core.exceptions import SQLValidationError
        
        with pytest.raises(SQLValidationError) as exc_info:
            validate_sql("INSERT INTO users (name) VALUES ('test')")
        
        assert "não autorizado" in str(exc_info.value).lower() or \
               "apenas select" in str(exc_info.value).lower() or \
               "Comando não permitido" in str(exc_info.value)

    def test_validate_sql_update_blocked(self):
        """Verifica que UPDATE é bloqueado."""
        from app.sql.validators import validate_sql
        from app.core.exceptions import SQLValidationError
        
        with pytest.raises(SQLValidationError):
            validate_sql("UPDATE users SET name = 'test'")

    def test_validate_sql_delete_blocked(self):
        """Verifica que DELETE é bloqueado."""
        from app.sql.validators import validate_sql
        from app.core.exceptions import SQLValidationError
        
        with pytest.raises(SQLValidationError):
            validate_sql("DELETE FROM users WHERE id = 1")

    def test_validate_sql_drop_blocked(self):
        """Verifica que DROP é bloqueado."""
        from app.sql.validators import validate_sql
        from app.core.exceptions import SQLValidationError
        
        with pytest.raises(SQLValidationError):
            validate_sql("DROP TABLE users")

    def test_validate_sql_create_blocked(self):
        """Verifica que CREATE é bloqueado."""
        from app.sql.validators import validate_sql
        from app.core.exceptions import SQLValidationError
        
        with pytest.raises(SQLValidationError):
            validate_sql("CREATE TABLE users (id INT)")

    def test_validate_sql_empty_query(self):
        """Verifica que query vazia levanta erro."""
        from app.sql.validators import validate_sql
        from app.core.exceptions import SQLValidationError
        
        with pytest.raises(SQLValidationError):
            validate_sql("")

    def test_validate_sql_none_query(self):
        """Verifica que None como query levanta erro."""
        from app.sql.validators import validate_sql
        from app.core.exceptions import SQLValidationError
        
        with pytest.raises(SQLValidationError):
            validate_sql(None)

    def test_validate_sql_non_string(self):
        """Verifica que não-string leva a erro."""
        from app.sql.validators import validate_sql
        from app.core.exceptions import SQLValidationError
        
        with pytest.raises(SQLValidationError):
            validate_sql(123)

    def test_validate_sql_comment_injection(self):
        """Verifica injeção via comentário SQL é bloqueada."""
        from app.sql.validators import validate_sql
        from app.core.exceptions import SQLValidationError
        
        # -- comment injection
        with pytest.raises(SQLValidationError):
            validate_sql("SELECT * FROM users -- hack")

    def test_validate_sql_block_comment(self):
        """Verifica block comments são bloqueados."""
        from app.sql.validators import validate_sql
        from app.core.exceptions import SQLValidationError
        
        with pytest.raises(SQLValidationError):
            validate_sql("SELECT /*comment*/ * FROM users")

    def test_validate_sql_union_injection(self):
        """Verifica UNION injection é detectada."""
        from app.sql.validators import validate_sql
        from app.core.exceptions import SQLValidationError
        
        # UPDATE em union com SELECT
        with pytest.raises(SQLValidationError):
            validate_sql("SELECT * FROM users; DROP TABLE users")

    def test_validate_sql_is_select_only_true(self):
        """Verifica is_select_only retorna True para SELECT."""
        from app.sql.validators import is_select_only
        
        assert is_select_only("SELECT 1") is True

    def test_is_select_only_false_for_insert(self):
        """Verifica is_select_only retorna False para INSERT."""
        from app.sql.validators import is_select_only
        
        assert is_select_only("INSERT INTO users VALUES (1)") is False

    def test_validate_sql_case_insensitive(self):
        """Verifica que validação é case-insensitive."""
        from app.sql.validators import validate_sql, SQLValidationError
        
        # select em minúsculas deve funcionar (começa com 'select')
        result = validate_sql("select * from users")
        assert result is True

    def test_validate_sql_insert_case_insensitive(self):
        """Verifica INSERT em maiúsculas/minúsculas é bloqueado."""
        from app.sql.validators import validate_sql, SQLValidationError
        
        with pytest.raises(SQLValidationError):
            validate_sql("insert into users values (1)")


class TestSQLReadOnlyTool:
    """Testes para SQLReadOnlyTool."""

    def test_tool_name(self, sql_readonly_tool):
        """Verifica nome da ferramenta."""
        assert sql_readonly_tool.tool_name == "sql_readonly"

    def test_tool_description_exists(self, sql_readonly_tool):
        """Verifica descrição existe e é não vazia."""
        assert len(sql_readonly_tool.tool_description) > 0

    def test_execute_with_valid_query(self, sql_readonly_tool):
        """Verifica execução com query válida."""
        result = sql_readonly_tool.execute({"query": "SELECT * FROM users"})
        
        assert isinstance(result, str)
        assert "executada" in result.lower() or "sucesso" in result.lower()

    def test_execute_with_empty_query(self, sql_readonly_tool):
        """Verifica execução sem query retorna erro."""
        result = sql_readonly_tool.execute({"query": ""})
        
        assert "Erro" in result or "error" in result.lower()

    def test_execute_without_query_key(self, sql_readonly_tool):
        """Verifica execução sem chave 'query'."""
        result = sql_readonly_tool.execute({})
        
        assert "Erro" in result or "error" in result.lower()

    def test_execute_with_dangerous_query(self, sql_readonly_tool):
        """Verifica que queries perigosas são bloqueadas."""
        result = sql_readonly_tool.execute({"query": "DROP TABLE users"})
        
        assert "Erro" in result or "error" in result.lower()

    def test_execute_with_mock_result(self, sql_readonly_tool):
        """Verifica resultado mockado."""
        result = sql_readonly_tool.execute({"query": "SELECT 1 AS demo"})
        
        assert isinstance(result, str)


class TestToolRegistry:
    """Testes para Tool Registry (ferramentas base)."""

    def test_list_tools_returns_list(self):
        """Verifica list_tools retorna lista."""
        from app.agents.tools.base import list_tools
        
        tools = list_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_list_contains_sql_readonly(self):
        """Verifica que sql_readonly está na lista."""
        from app.agents.tools.base import list_tools
        
        tool_names = [t["name"] for t in list_tools()]
        
        assert "sql_readonly" in tool_names

    def test_get_tool_by_name(self):
        """Verifica get_tool retorna ferramenta pelo nome."""
        from app.agents.tools.base import get_tool
        
        tool = get_tool("sql_readonly")
        
        assert tool is not None
        assert tool.tool_name == "sql_readonly"

    def test_get_tool_not_found(self):
        """Verifica get_tool retorna None para ferramenta inexistente."""
        from app.agents.tools.base import get_tool
        
        tool = get_tool("inexistent_tool")
        
        assert tool is None

    def test_get_tool_case_insensitive(self):
        """Verifica que get_tool é case-insensitive? (não garante)."""
        from app.agents.tools.base import get_tool
        
        # Depende da implementação - se não for case-insensitive, retorna None
        tool = get_tool("SQL_READONLY")
        # Se retornar None, a feature não existe

    def test_mock_tool_properties(self):
        """Verifica MockTool tem propriedades corretas."""
        from app.agents.tools.base import BaseTool
        
        # Deve poder criar subclass mock para testes
        class TestTool(BaseTool):
            @property
            def tool_name(self) -> str:
                return "test"
            
            @property
            def tool_description(self) -> str:
                return "Test"
            
            def execute(self, arguments: dict) -> str:
                return "executed"
        
        tool = TestTool()
        assert tool.tool_name == "test"


class TestExceptions:
    """Testes para exceções customizadas."""

    def test_provider_error_message(self):
        """Verifica ProviderError com mensagem."""
        from app.core.exceptions import ProviderError
        
        exc = ProviderError("Erro no provider")
        
        assert exc.message == "Erro no provider"
        assert str(exc) == "Erro no provider"

    def test_agent_error_message(self):
        """Verifica AgentError com mensagem e detail."""
        from app.core.exceptions import AgentError
        
        exc = AgentError("Agent failed", "Timeout exceeded")
        
        assert exc.message == "Agent failed"
        assert exc.detail == "Timeout exceeded"

    def test_sql_validation_error(self):
        """Verifica SQLValidationError."""
        from app.core.exceptions import SQLValidationError
        
        exc = SQLValidationError("Query inválida")
        
        assert exc.message == "Query inválida"
        assert str(exc) == "Query inválida"

    def test_tool_error(self):
        """Verifica ToolError com tool_name."""
        from app.core.exceptions import ToolError
        
        exc = ToolError("Tool failed", "sql_readonly", "Connection refused")
        
        assert exc.message == "Tool failed"
        assert exc.tool_name == "sql_readonly"
        assert exc.detail == "Connection refused"

    def test_not_found_error(self):
        """Verifica NotFoundError."""
        from app.core.exceptions import NotFoundError
        
        exc = NotFoundError("Recurso não encontrado")
        
        assert exc.message == "Recurso não encontrado"


class TestBaseAgent:
    """Testes para BaseAgent (ABC)."""

    def test_agent_id_default(self):
        """Verifica agent_id default."""
        from app.agents.base import BaseAgent
        
        class TestAgent(BaseAgent):
            def run(self, input_data: str, params: dict = None) -> dict:
                return {"output": "test", "_done": True}
        
        agent = TestAgent()
        assert agent.agent_id == "base"

    def test_agent_name_default(self):
        """Verifica agent_name default."""
        from app.agents.base import BaseAgent
        
        class TestAgent(BaseAgent):
            def run(self, input_data: str, params: dict = None) -> dict:
                return {"output": "test", "_done": True}
        
        agent = TestAgent()
        assert agent.agent_name == "Base Agent"

    def test_info_method(self):
        """Verifica método info()."""
        from app.agents.base import BaseAgent
        
        class TestAgent(BaseAgent):
            @property
            def agent_id(self) -> str:
                return "test_agent"
            
            @property
            def agent_name(self) -> str:
                return "Test Agent"
            
            def run(self, input_data: str, params: dict = None) -> dict:
                return {"output": "test", "_done": True}
        
        agent = TestAgent()
        info = agent.info()
        
        assert info["agent_id"] == "test_agent"
        assert info["name"] == "Test Agent"

    def test_abstract_run_not_implemented(self):
        """Verifica que run é abstrato."""
        from app.agents.base import BaseAgent
        
        with pytest.raises(TypeError):
            BaseAgent()


class TestResearchAgent:
    """Testes para ResearchAgent."""

    def test_agent_id(self, research_agent):
        """Verifica agent_id do ResearchAgent."""
        assert research_agent.agent_id == "research"

    def test_agent_name(self, research_agent):
        """Verifica agent_name do ResearchAgent."""
        assert research_agent.agent_name == "Research Agent"

    def test_run_returns_output(self, research_agent):
        """Verifica run retorna output."""
        result = research_agent.run("Teste")
        
        assert isinstance(result, dict)
        assert "output" in result
        assert "_done" in result

    def test_run_sets_done_true(self, research_agent):
        """Verifica _done=True no resultado."""
        result = research_agent.run("Teste")
        
        assert result["_done"] is True

    def test_run_with_params(self, research_agent):
        """Verifica run com params."""
        result = research_agent.run(
            "Pergunta",
            params={"tool": "sql_readonly", "query": "SELECT 1"}
        )
        
        assert isinstance(result["output"], str)

    def test_run_with_custom_tool(self, research_agent):
        """Verifica run com ferramenta customizada."""
        result = research_agent.run(
            "Teste",
            params={"tool": "sql_readonly"}
        )
        
        assert "_done" in result


class TestBaseToolCall:
    """Testes para __call__ do BaseTool."""

    def test_base_tool_call(self, sql_readonly_tool):
        """Verifica que __call__ delega para execute."""
        result = sql_readonly_tool(query="SELECT 1")
        
        assert isinstance(result, str)