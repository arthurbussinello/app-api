"""Exceções customizadas da API."""


class ProviderError(Exception):
    """Falha ao comunicar com provider de IA."""

    def __init__(self, message: str = "Erro no provider", detail: str | None = None):
        self.message = message
        self.detail = detail or message
        super().__init__(self.message)


class AgentError(Exception):
    """Falha na execução de agente."""

    def __init__(self, message: str = "Erro no agente", detail: str | None = None):
        self.message = message
        self.detail = detail or message
        super().__init__(self.message)


class SQLValidationError(Exception):
    """Query SQL não aprovou a validação de segurança."""

    def __init__(self, message: str = "Query SQL inválida", detail: str | None = None):
        self.message = message
        self.detail = detail or message
        super().__init__(self.message)


class ToolError(Exception):
    """Falha ao executar ferramenta."""

    def __init__(self, message: str = "Erro na ferramenta", tool_name: str = "", detail: str | None = None):
        self.message = message
        self.tool_name = tool_name
        self.detail = detail or message
        super().__init__(self.message)


class NotFoundError(Exception):
    """Recurso não encontrado."""

    def __init__(self, message: str = "Recurso não encontrado", detail: str | None = None):
        self.message = message
        self.detail = detail or message
        super().__init__(self.message)