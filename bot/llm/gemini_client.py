import asyncio

import google.generativeai as genai

from bot import config
from bot.llm.base import LLMClient


class GeminiClient(LLMClient):
    def __init__(self) -> None:
        if not config.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set in .env")
        genai.configure(api_key=config.GEMINI_API_KEY)
        self._model = genai.GenerativeModel(config.GEMINI_MODEL)

    async def generate(self, prompt: str, *, temperature: float = 0.7) -> str:
        def _call() -> str:
            response = self._model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=temperature),
            )
            return response.text

        return await asyncio.to_thread(_call)
