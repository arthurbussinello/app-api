"""Configurações da aplicação carregadas de variáveis de ambiente."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Server
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = True

    # Provider default
    provider_default: str = "local"
    provider_local_enabled: bool = True
    provider_online_enabled: bool = False
    provider_corporate_enabled: bool = False
    provider_online_base_url: str = "https://api.example.com/v1"
    provider_online_api_key: str = "sk-exemplo-online-000"
    provider_corporate_base_url: str = "https://ia.corporate.internal/api/v1"
    provider_corporate_api_key: str = "corporate-api-key-exemplo"

    # SQL Server (read-only)
    sql_server: str = "localhost"
    sql_database: str = "company_db"
    sql_port: int = 1433
    sql_user: str = "db_reader"
    sql_password: str = "db_password_placeholder"

    # Agentes
    agent_max_iterations: int = 5
    agent_timeout_seconds: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()