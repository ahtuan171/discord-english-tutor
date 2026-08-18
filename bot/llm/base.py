from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Common interface every LLM provider (Gemini, Ollama, ...) must implement.

    generate() always returns raw text. Callers that need structured data
    ask the model for JSON in the prompt and parse it themselves (see
    bot/llm/prompts.py + bot/utils/json_extract.py).
    """

    @abstractmethod
    async def generate(self, prompt: str, *, temperature: float = 0.7) -> str:
        ...
