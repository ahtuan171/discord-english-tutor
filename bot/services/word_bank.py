"""Loads the curated vocabulary word bank from data/vocabulary/*.json.

Files are named "NN_topic.json" (01_environment.json, 02_education.json, ...) —
the numeric prefix controls teaching order (plain alphabetical sort would put
e.g. "awl_sublist_1.json" before "environment.json", breaking topic order).
Each file is a JSON array of {"word": ..., "part_of_speech": ...} plus a
manual {"definition": ..., "example": ...} written for every word so the
bot never depends on an LLM or a dictionary lookup that might return an
obscure or wrong sense of a common word.
"""

import json
import re
from functools import lru_cache

from bot import config

_PREFIX_RE = re.compile(r"^\d+_")


@lru_cache
def load_word_bank() -> list[dict]:
    entries: list[dict] = []
    if not config.VOCAB_DATA_DIR.exists():
        return entries

    for file_path in sorted(config.VOCAB_DATA_DIR.glob("*.json")):
        topic = _PREFIX_RE.sub("", file_path.stem)
        with open(file_path, encoding="utf-8") as f:
            words = json.load(f)
        for item in words:
            entries.append(
                {
                    "word": item["word"].strip().lower(),
                    "part_of_speech": item.get("part_of_speech", ""),
                    "topic": topic,
                    "definition": item.get("definition", ""),
                    "example": item.get("example", ""),
                }
            )
    return entries
