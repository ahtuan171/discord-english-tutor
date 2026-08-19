import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
VOCAB_DATA_DIR = BASE_DIR / "data" / "vocabulary"


def _int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value else default


DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
DAILY_CHANNEL_ID = _int("DAILY_CHANNEL_ID", 0)
GUILD_ID = _int("GUILD_ID", 0)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/english_tutor",
)

DAILY_HOUR = _int("DAILY_HOUR", 8)
DAILY_MINUTE = _int("DAILY_MINUTE", 0)
TIMEZONE = os.getenv("TIMEZONE", "Asia/Ho_Chi_Minh")

DAILY_WORD_COUNT = 10
QUICK_MODE_WORD_COUNT = 3
