"""Dependências injetáveis para as rotas da API."""

import logging
from typing import Generator

from fastapi import Depends, Request

from app.config import settings


def get_logger() -> logging.Logger:
    """Retorna o logger estruturado da aplicação."""
    return logging.getLogger("ia_api")


def get_settings() -> SettingsType:
    """Retorna as configurações globais (singleton)."""
    return settings