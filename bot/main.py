import asyncio
import logging

from pathlib import Path

import discord
from discord.ext import commands

from bot import config
from bot.db.session import init_models
from bot.scheduler import setup_scheduler

# Ensure logs directory exists
logs_dir = Path(__file__).resolve().parent.parent / "logs"
logs_dir.mkdir(parents=True, exist_ok=True)
log_file = logs_dir / "bot.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file, encoding="utf-8"),
    ],
)
log = logging.getLogger("english-tutor-bot")

COGS = [
    "bot.cogs.vocab",
    "bot.cogs.review",
    "bot.cogs.quick",
    "bot.cogs.progress",
]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready() -> None:
    log.info("Logged in as %s (id=%s)", bot.user, bot.user.id)

    guild_id = config.GUILD_ID
    if guild_id:
        guild = discord.Object(id=guild_id)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        log.info("Slash commands synced to guild %s (instant)", guild_id)
    else:
        await bot.tree.sync()
        log.info("Slash commands synced globally (can take up to 1 hour to appear)")

    setup_scheduler(bot)


async def main() -> None:
    if not config.DISCORD_BOT_TOKEN:
        raise RuntimeError("DISCORD_BOT_TOKEN is not set. Copy env.example to .env and fill it in.")

    await init_models()

    async with bot:
        for cog in COGS:
            await bot.load_extension(cog)
        await bot.start(config.DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
