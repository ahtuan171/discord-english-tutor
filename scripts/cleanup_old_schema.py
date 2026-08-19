"""One-time cleanup: drop columns/tables left over from the earlier
LLM-based design (paraphrase/writing/quiz features, preferred_mode) so the
live database matches the current models exactly.

Usage: python -m scripts.cleanup_old_schema
Safe to re-run (uses IF EXISTS everywhere).
"""

import asyncio

from sqlalchemy import text

from bot.db.session import engine

STATEMENTS = [
    "ALTER TABLE users DROP COLUMN IF EXISTS preferred_mode",
    "ALTER TABLE daily_lessons DROP COLUMN IF EXISTS paraphrase_sentences",
    "ALTER TABLE daily_lessons DROP COLUMN IF EXISTS writing_question",
    "ALTER TABLE daily_lessons DROP COLUMN IF EXISTS writing_sample",
    "ALTER TABLE daily_lessons DROP COLUMN IF EXISTS writing_annotations",
    "DROP TABLE IF EXISTS paraphrase_attempts",
    "DROP TABLE IF EXISTS writing_attempts",
    "DROP TABLE IF EXISTS quiz_attempts",
    "DROP TABLE IF EXISTS mistake_logs",
]


async def main() -> None:
    async with engine.begin() as conn:
        for stmt in STATEMENTS:
            print(f"  {stmt}")
            await conn.execute(text(stmt))
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
