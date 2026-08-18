from sqlalchemy import select

from bot import config
from bot.db.models import Vocabulary
from bot.llm.factory import get_llm_client
from bot.llm.prompts import DAILY_VOCAB_PROMPT, DEFINE_WORDS_PROMPT
from bot.services.word_bank import load_word_bank
from bot.utils.json_extract import extract_json


async def _next_words_from_bank(session, count: int) -> list[dict]:
    """Walk the curated word bank in file order and return the first `count`
    words that haven't been taught yet (i.e. not already in the Vocabulary
    table). Returns fewer than `count` if the bank is running low."""
    bank = load_word_bank()
    if not bank:
        return []

    taught_words = set((await session.execute(select(Vocabulary.word))).scalars().all())

    picked = []
    for entry in bank:
        if entry["word"] in taught_words:
            continue
        picked.append(entry)
        if len(picked) >= count:
            break
    return picked


async def _define_words(bank_entries: list[dict]) -> list[dict]:
    words = ", ".join(e["word"] for e in bank_entries)
    prompt = DEFINE_WORDS_PROMPT.format(words=words)
    raw = await get_llm_client().generate(prompt, temperature=0.4)
    defined = extract_json(raw)

    by_word = {d["word"].strip().lower(): d for d in defined}
    results = []
    for entry in bank_entries:
        d = by_word.get(entry["word"])
        results.append(
            {
                "word": entry["word"],
                "part_of_speech": entry.get("part_of_speech") or (d or {}).get("part_of_speech", ""),
                "definition": (d or {}).get("definition", ""),
                "example": (d or {}).get("example", ""),
            }
        )
    return results


async def generate_daily_words(session, count: int = config.DAILY_WORD_COUNT) -> list[Vocabulary]:
    bank_entries = await _next_words_from_bank(session, count)

    items: list[dict] = []
    if bank_entries:
        items.extend(await _define_words(bank_entries))

    remaining = count - len(items)
    if remaining > 0:
        # Word bank exhausted (or missing) — fall back to letting the LLM invent words.
        existing = (await session.execute(select(Vocabulary.word))).scalars().all()
        exclude_words = ", ".join(existing[-200:]) or "none"
        prompt = DAILY_VOCAB_PROMPT.format(count=remaining, exclude_words=exclude_words)
        raw = await get_llm_client().generate(prompt, temperature=0.8)
        items.extend(extract_json(raw))

    vocab_objs: list[Vocabulary] = []
    for item in items:
        word = item["word"].strip().lower()
        existing_vocab = (
            await session.execute(select(Vocabulary).where(Vocabulary.word == word))
        ).scalar_one_or_none()
        if existing_vocab:
            vocab_objs.append(existing_vocab)
            continue

        vocab = Vocabulary(
            word=word,
            part_of_speech=item.get("part_of_speech", ""),
            definition=item["definition"],
            example=item["example"],
        )
        session.add(vocab)
        vocab_objs.append(vocab)

    await session.flush()
    return vocab_objs
