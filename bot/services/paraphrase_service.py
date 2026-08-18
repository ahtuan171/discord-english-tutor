from bot.llm.factory import get_llm_client
from bot.llm.prompts import PARAPHRASE_FEEDBACK_PROMPT, PARAPHRASE_SENTENCES_PROMPT
from bot.utils.json_extract import extract_json


async def generate_paraphrase_sentences(words: list[str], count: int = 3) -> list[str]:
    prompt = PARAPHRASE_SENTENCES_PROMPT.format(words=", ".join(words), count=count)
    raw = await get_llm_client().generate(prompt, temperature=0.7)
    return extract_json(raw)


async def grade_paraphrase(original: str, answer: str) -> dict:
    prompt = PARAPHRASE_FEEDBACK_PROMPT.format(original=original, answer=answer)
    raw = await get_llm_client().generate(prompt, temperature=0.3)
    return extract_json(raw)
