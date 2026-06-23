"""Provider corporativo — simula chamadas para gateway de IA da empresa."""


class CorporateProvider(BaseProvider):
    """Provider que se conecta ao gateway de IA corporativo (simulado)."""

    def __init__(self, base_url: str = "", api_key: str = ""):
        self.base_url = base_url or "https://ia.corporate.internal/api/v1"
        self.api_key = api_key or "corporate-api-key-exemplo"

    @property
    def provider_id(self) -> str:
        return "corporate"

    def complete(self, prompt: str, **kwargs) -> str:
        """Simula chamada ao gateway corporativo com autenticação."""
        return (
            f"[CorporateProvider] Resposta simulada via gateway: '{prompt[:80]}'\n"
            f"Auth: {self.api_key[:6]}*** | Endpoint: {self.base_url}"
        )

    def chat(self, messages: list[dict], **kwargs) -> dict:
        """Simula chat completion pelo gateway corporativo."""
        last_content = messages[-1].get("content", "") if messages else ""
        return {
            "message": {
                "role": "assistant",
                "content": (
                    f"[CorporateProvider] Resposta do gateway: '{last_content[:80]}'"
                ),
            }
        }

    def health_check(self) -> dict:
        """Verifica conectividade com o gateway corporativo."""
        try:
            # Em produção, faria GET real para health check.
            return {
                "status": "ok",
                "provider": self.provider_id,
                "endpoint": self.base_url,
            }
        except Exception as e:
            return {"status": "error", "provider": self.provider_id, "detail": str(e)}