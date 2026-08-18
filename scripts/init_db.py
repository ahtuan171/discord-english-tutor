"""Standalone helper: create all tables without starting the bot.

Usage: python -m scripts.init_db
"""

import asyncio

from bot.db.session import init_models


async def main() -> None:
    await init_models()
    print("Database tables created.")


if __name__ == "__main__":
    asyncio.run(main())
