from bot.llm.factory import get_llm_client
from bot.llm.prompts import (
    EXTRACT_MISTAKE_PROMPT,
    GRADE_RECALL_ANSWER_PROMPT,
    RECALL_QUIZ_PROMPT,
)
from bot.utils.json_extract import extract_json


async def generate_recall_quiz(
    words: list[str], paraphrase_sentence: str, count: int = 5
) -> list[dict]:
    prompt = RECALL_QUIZ_PROMPT.format(
        words=", ".join(words), paraphrase_sentence=paraphrase_sentence, count=count
    )
    raw = await get_llm_client().generate(prompt, temperature=0.6)
    return extract_json(raw)


async def grade_recall_answer(question: str, word: str | None, answer: str) -> dict:
    prompt = GRADE_RECALL_ANSWER_PROMPT.format(question=question, word=word or "N/A", answer=answer)
    raw = await get_llm_client().generate(prompt, temperature=0.2)
    return extract_json(raw)


async def detect_mistake(text: str) -> dict:
    prompt = EXTRACT_MISTAKE_PROMPT.format(text=text)
    raw = await get_llm_client().generate(prompt, temperature=0.1)
    return extract_json(raw)
