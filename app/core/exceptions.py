"""Exceções customizadas e handlers da API."""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


def register_exception_handlers(app) -> None:
    """Registra handlers para exceções customizadas no FastAPI.

    Mapeia cada exceção personalizada para um status code HTTP padronizado,
    garantindo respostas de erro consistentes e estruturadas.
    """

    @app.exception_handler(ProviderError)
    async def provider_error_handler(request: Request, exc: ProviderError):
        return JSONResponse(
            status_code=502,
            content={"detail": f"Erro no provider: {exc.detail}"},
        )

    @app.exception_handler(AgentError)
    async def agent_error_handler(request: Request, exc: AgentError):
        return JSONResponse(
            status_code=500,
            content={"detail": f"Erro no agente: {exc.detail}"},
        )

    @app.exception_handler(SQLValidationError)
    async def sql_validation_error_handler(request: Request, exc: SQLValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": f"Validação SQL falhou: {exc.detail}"},
        )

    @app.exception_handler(ToolError)
    async def tool_error_handler(request: Request, exc: ToolError):
        status = 500 if not exc.tool_name else 400
        return JSONResponse(
            status_code=status,
            content={"detail": f"Erro na ferramenta '{exc.tool_name}': {exc.detail}"},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": f"Not found: {exc.detail}"},
        )

    # Também trata HTTPException padrão com conteúdo estruturado.
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail if exc.detail else "Erro na requisição"},
        )


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