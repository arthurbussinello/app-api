"""Verificações de permissão simples."""


def check_api_key(api_key: str | None) -> bool:
    """Verifica se a chave de API é válida (simulado)."""
    if not api_key:
        return False
    # Em produção, validaria contra um secret real.
    return len(api_key) > 0


def check_role(user_roles: list[str] | None, required_role: str = "reader") -> bool:
    """Verifica se o usuário possui a role necessária."""
    if not user_roles or not required_role:
        return True
    return required_role in user_roles