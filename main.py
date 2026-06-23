"""api-ia — FastAPI entrypoint."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.logging_config import setup_logging
from app.core.exceptions import register_exception_handlers

setup_logging()

app = FastAPI(
    title="api-ia",
    description="Hub corporativo de inteligência artificial em Python (FastAPI).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

from app.api.v1 import health_routes, provider_routes, chat_routes, agent_routes, tools_routes

app.include_router(health_routes.router, prefix="/health", tags=["health"])
app.include_router(provider_routes.router, prefix="/v1", tags=["providers"])
app.include_router(chat_routes.router, prefix="/v1", tags=["chat"])
app.include_router(agent_routes.router, prefix="/v1", tags=["agents"])
app.include_router(tools_routes.router, prefix="/v1", tags=["tools"])


@app.get("/")
def root():
    return {
        "name": "api-ia",
        "status": "running",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
    )