"""Entry point da API IA — FastAPI application."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.logging_config import setup_logger
from app.api.v1.health_routes import router as health_router
from app.api.v1.provider_routes import router as provider_router
from app.api.v1.chat_routes import router as chat_router
from app.api.v1.agent_routes import router as agent_router
from app.api.v1.tools_routes import router as tools_router

# Configura logging estruturado.
logger = setup_logger("ia_api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle do application — init e cleanup."""
    logger.info("Iniciando API IA %s v%s", settings.app_name, settings.version)
    yield
    logger.info("Encerrando API IA")


app = FastAPI(
    title="API IA",
    description=(
        "Hub corporativo de inteligência artificial. "
        "API HTTP com FastAPI para chat, agentes, ferramentas e consultas seguras a SQL."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# Middleware CORS (permitir origens locais).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# --- Montagem dos routers ---
app.include_router(health_router)
app.include_router(provider_router)
app.include_router(chat_router)
app.include_router(agent_router)
app.include_router(tools_router)


@app.middleware("http")
async def log_requests(request: Request, call):
    """Middleware para log de todas as requisições HTTP."""
    from datetime import UTC, datetime

    start_time = datetime.now(UTC)
    response = await call(request)
    duration_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

    logger.info(
        "HTTP %s %s -> %d (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/")
async def root() -> dict:
    """Rota raiz — redireciona para a documentação."""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "docs": "/docs",
        "health": "/v1/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )