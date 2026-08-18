from bot.llm.factory import get_llm_client
from bot.llm.prompts import WRITING_SAMPLE_PROMPT
from bot.utils.json_extract import extract_json


async def generate_writing_sample(words: list[str]) -> dict:
    prompt = WRITING_SAMPLE_PROMPT.format(words=", ".join(words))
    raw = await get_llm_client().generate(prompt, temperature=0.7)
    return extract_json(raw)
