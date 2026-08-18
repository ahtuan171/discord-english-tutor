"""Loads the curated vocabulary word bank from data/vocabulary/*.json.

Each file is one topic (environment.json, education.json, ...) containing
a JSON array of {"word": ..., "part_of_speech": ...}. The bot picks words
from here first so the curriculum stays exam-relevant and predictable;
the LLM is only used to generate definitions/examples for them. If the
whole bank has been taught already, the vocabulary service falls back to
asking the LLM to invent new words.
"""

import json
from functools import lru_cache

from bot import config


@lru_cache
def load_word_bank() -> list[dict]:
    entries: list[dict] = []
    if not config.VOCAB_DATA_DIR.exists():
        return entries

    for file_path in sorted(config.VOCAB_DATA_DIR.glob("*.json")):
        topic = file_path.stem
        with open(file_path, encoding="utf-8") as f:
            words = json.load(f)
        for item in words:
            entries.append(
                {
                    "word": item["word"].strip().lower(),
                    "part_of_speech": item.get("part_of_speech", ""),
                    "topic": topic,
                }
            )
    return entries
