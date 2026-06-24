"""Entry point da API IA — FastAPI application.

Usage:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    # ou para production:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import setup_logger
from app.api.v1.health_routes import router as health_router
from app.api.v1.provider_routes import router as provider_router
from app.api.v1.chat_routes import router as chat_router
from app.api.v1.agent_routes import router as agent_router
from app.api.v1.tools_routes import router as tools_router

# Configura logging estruturado com JSON.
logger = setup_logger("ia_api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle do application — init e cleanup."""
    logger.info("=" * 60)
    logger.info("INICIANDO API IA %s v%s", "API IA", "0.1.0")
    logger.info("=" * 60)
    yield
    logger.info("=" * 60)
    logger.info("ENCERRANDO API IA")
    logger.info("=" * 60)


app = FastAPI(
    title="API IA",
    description=(
        "Hub corporativo de inteligência artificial. "
        "API HTTP com FastAPI para chat, agentes, ferramentas e consultas seguras a SQL."
    ),
    version="0.1.0",
    contact={
        "name": "API IA",
    },
    license_info={},
    lifespan=lifespan,
)

# Registra handlers para exceções customizadas (ProviderError, AgentError, etc).
register_exception_handlers(app)

# Middleware CORS (permitir origens locais).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)


# --- Montagem dos routers (prefixo /v1 exceto health) ---
app.include_router(health_router, prefix="/v1")
app.include_router(provider_router, prefix="/v1", tags=["providers"])
app.include_router(chat_router, prefix="/v1", tags=["chat"])
app.include_router(agent_router, prefix="/v1", tags=["agents"])
app.include_router(tools_router, prefix="/v1", tags=["tools"])


@app.middleware("http")
async def log_requests(request: Request, call):
    """Middleware para log de todas as requisições HTTP com tempo de resposta."""
    from datetime import UTC, datetime

    start_time = datetime.now(UTC)
    response = await call(request)
    duration_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

    logger.info(
        "HTTP %s %s -> %d (%.2fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/")
async def root() -> dict:
    """Rota raiz — informações básicas da API."""
    return {
        "name": "API IA",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/v1/health",
        "status": "running",
    }


@app.get("/info")
async def info() -> dict:
    """Informações detalhadas da aplicação e configuração."""
    return {
        "name": "API IA",
        "version": "0.1.0",
        "host": settings.app_host,
        "port": settings.app_port,
        "debug": settings.app_debug,
        "docs": "/docs",
        "health": "/v1/health",
        "providers_enabled": {
            "local": settings.provider_local_enabled,
            "online": settings.provider_online_enabled,
            "corporate": settings.provider_corporate_enabled,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
    )