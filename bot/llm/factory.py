from functools import lru_cache

from bot import config
from bot.llm.base import LLMClient


@lru_cache
def get_llm_client() -> LLMClient:
    if config.LLM_PROVIDER == "ollama":
        from bot.llm.ollama_client import OllamaClient

        return OllamaClient()

    from bot.llm.gemini_client import GeminiClient

    return GeminiClient()
