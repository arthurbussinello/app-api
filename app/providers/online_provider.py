"""Provider online — simula chamadas HTTP para API externa de IA."""

import httpx


class OnlineProvider(BaseProvider):
    """Provider que se conecta a uma API de IA online (simulado)."""

    def __init__(self, base_url: str = "", api_key: str = ""):
        self.base_url = base_url or "https://api.example.com/v1"
        self.api_key = api_key or "sk-exemplo-online-000"

    @property
    def provider_id(self) -> str:
        return "online"

    def complete(self, prompt: str, **kwargs) -> str:
        """Simula chamada HTTP para endpoint de completions."""
        # Em produção, faria POST real para self.base_url/completions.
        return f"[OnlineProvider] Resposta simulada para: '{prompt[:80]}'"

    def chat(self, messages: list[dict], **kwargs) -> dict:
        """Simula chamada HTTP para endpoint de chat completions."""
        last_content = messages[-1].get("content", "") if messages else ""
        return {
            "message": {
                "role": "assistant",
                "content": f"[OnlineProvider] Resposta simulada para: '{last_content[:80]}'",
            }
        }

    def health_check(self) -> dict:
        """Verifica conectividade com a API externa."""
        try:
            # Em produção, faria um GET real de health check.
            return {"status": "ok", "provider": self.provider_id, "endpoint": self.base_url}
        except Exception as e:
            return {"status": "error", "provider": self.provider_id, "detail": str(e)}