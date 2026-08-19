import logging

from sqlalchemy import select

from bot import config
from bot.db.models import DictionaryEntry, Vocabulary
from bot.services.word_bank import load_word_bank

log = logging.getLogger("vocabulary_service")


async def _next_words_from_bank(session, count: int) -> list[dict]:
    """Walk the curated word bank in file order and return the first `count`
    words that haven't been taught yet (i.e. not already in the Vocabulary
    table). Returns fewer than `count` (possibly zero) once the whole bank
    has been taught — spaced-repetition review of already-taught words is
    handled separately by /review and /quick, not by re-sending new-word
    batches here."""
    bank = load_word_bank()
    if not bank:
        return []

    taught_words = set((await session.execute(select(Vocabulary.word))).scalars().all())
    picked = [entry for entry in bank if entry["word"] not in taught_words]
    return picked[:count]


async def _lookup_dictionary_entries(session, words: list[str]) -> dict[str, DictionaryEntry]:
    if not words:
        return {}
    rows = (
        await session.execute(select(DictionaryEntry).where(DictionaryEntry.word.in_(words)))
    ).scalars().all()
    return {row.word: row for row in rows}


async def generate_daily_words(session, count: int = config.DAILY_WORD_COUNT) -> list[Vocabulary]:
    bank_entries = await _next_words_from_bank(session, count)

    words_needing_lookup = [e["word"] for e in bank_entries if not e.get("definition")]
    dictionary_by_word = await _lookup_dictionary_entries(session, words_needing_lookup)

    vocab_objs: list[Vocabulary] = []
    for entry in bank_entries:
        word = entry["word"]

        existing_vocab = (
            await session.execute(select(Vocabulary).where(Vocabulary.word == word))
        ).scalar_one_or_none()
        if existing_vocab:
            vocab_objs.append(existing_vocab)
            continue

        if entry.get("definition"):
            part_of_speech, definition, example = (
                entry.get("part_of_speech", ""),
                entry["definition"],
                entry.get("example", ""),
            )
        else:
            dict_entry = dictionary_by_word.get(word)
            if not dict_entry:
                log.warning(
                    "No dictionary entry found for %r — run `python -m scripts.seed_dictionary` "
                    "or add a manual definition/example in data/vocabulary/. Skipping.",
                    word,
                )
                continue
            part_of_speech = entry.get("part_of_speech") or dict_entry.part_of_speech
            definition, example = dict_entry.definition, dict_entry.example

        vocab = Vocabulary(
            word=word,
            part_of_speech=part_of_speech,
            definition=definition,
            example=example,
        )
        session.add(vocab)
        vocab_objs.append(vocab)

    await session.flush()
    return vocab_objs
