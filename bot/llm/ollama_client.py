import httpx

from bot import config
from bot.llm.base import LLMClient


class OllamaClient(LLMClient):
    def __init__(self) -> None:
        self._base_url = config.OLLAMA_HOST.rstrip("/")
        self._model = config.OLLAMA_MODEL

    async def generate(self, prompt: str, *, temperature: float = 0.7) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self._base_url}/api/generate",
                json={
                    "model": self._model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": temperature},
                },
            )
            response.raise_for_status()
            return response.json()["response"]
