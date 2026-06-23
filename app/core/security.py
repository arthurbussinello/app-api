"""Utilitários de segurança para a API."""


def sanitize_input(text: str, max_length: int = 4096) -> str:
    """Sanitiza entrada do usuário removendo caracteres nulos e controladores."""
    if not isinstance(text, str):
        return str(text)
    # Remove caracteres null e controladores.
    cleaned = "".join(ch for ch in text if ord(ch) >= 32 or ch in "\n\r\t")
    return cleaned[:max_length]


def generate_request_id() -> str:
    """Gera um ID único para requisições (simulado)."""
    import uuid
    return f"req_{uuid.uuid4().hex[:16]}"