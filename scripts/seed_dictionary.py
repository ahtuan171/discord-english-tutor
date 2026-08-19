"""One-time ETL: download the Wordset open dictionary
(github.com/wordset/wordset-dictionary, CC-BY-SA 4.0, built on Princeton
WordNet) and load it into the `dictionary_entries` table so the bot can
look up word -> definition/example/part_of_speech from the database
instead of calling an LLM.

Usage: python -m scripts.seed_dictionary
Safe to re-run: existing words are skipped (ON CONFLICT DO NOTHING).
"""

import asyncio
import json
import urllib.request

from sqlalchemy.dialects.postgresql import insert as pg_insert

from bot.db.models import DictionaryEntry
from bot.db.session import SessionLocal, init_models

BASE_URL = "https://raw.githubusercontent.com/wordset/wordset-dictionary/master/data/{}.json"
LETTERS = list("abcdefghijklmnopqrstuvwxyz") + ["misc"]

# Postgres caps bound parameters at 32767 per statement; DictionaryEntry has
# 5 columns, so keep well under 32767 / 5 rows per INSERT.
CHUNK_SIZE = 2000


def fetch_letter_file(letter: str) -> dict:
    url = BASE_URL.format(letter)
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read())


def pick_best_meaning(meanings: list[dict]) -> dict | None:
    if not meanings:
        return None
    with_example = [m for m in meanings if m.get("example")]
    return with_example[0] if with_example else meanings[0]


async def seed_letter(letter: str) -> int:
    data = fetch_letter_file(letter)
    rows = []
    for word, entry in data.items():
        meaning = pick_best_meaning(entry.get("meanings", []))
        if not meaning or not meaning.get("def"):
            continue
        rows.append(
            {
                "word": word.strip().lower(),
                "part_of_speech": meaning.get("speech_part", ""),
                "definition": meaning["def"],
                "example": meaning.get("example", ""),
                "synonyms": meaning.get("synonyms", []),
            }
        )

    if not rows:
        return 0

    async with SessionLocal() as session:
        for i in range(0, len(rows), CHUNK_SIZE):
            chunk = rows[i : i + CHUNK_SIZE]
            stmt = pg_insert(DictionaryEntry).values(chunk)
            stmt = stmt.on_conflict_do_nothing(index_elements=["word"])
            await session.execute(stmt)
        await session.commit()
    return len(rows)


async def main() -> None:
    await init_models()
    total = 0
    for letter in LETTERS:
        count = await seed_letter(letter)
        total += count
        print(f"  {letter}.json -> {count} entries")
    print(f"Done. Inserted up to {total} dictionary entries (duplicates skipped).")


if __name__ == "__main__":
    asyncio.run(main())
