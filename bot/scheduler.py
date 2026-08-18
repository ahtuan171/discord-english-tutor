import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands

from bot import config
from bot.db.session import get_session
from bot.services.lesson_service import get_lesson_vocabulary, get_or_create_today_lesson
from bot.utils.embeds import vocabulary_embed, writing_embed

log = logging.getLogger("scheduler")


def setup_scheduler(bot: commands.Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)

    async def post_daily_lesson() -> None:
        if not config.DAILY_CHANNEL_ID:
            log.warning("DAILY_CHANNEL_ID not set, skipping scheduled post")
            return

        channel = bot.get_channel(config.DAILY_CHANNEL_ID)
        if channel is None:
            log.warning("Could not find channel %s", config.DAILY_CHANNEL_ID)
            return

        async with get_session() as session:
            lesson, created = await get_or_create_today_lesson(session, channel.id)
            if not created:
                return  # already sent today
            vocab_list = await get_lesson_vocabulary(session, lesson)
            await session.commit()

        await channel.send(embed=vocabulary_embed(vocab_list))
        await channel.send(embed=writing_embed(lesson))
        await channel.send(
            "Run `/paraphrase`, `/quiz`, or `/quick` to practice today's lesson. Good luck! 🍀"
        )

    scheduler.add_job(
        post_daily_lesson,
        CronTrigger(hour=config.DAILY_HOUR, minute=config.DAILY_MINUTE),
        id="daily_lesson",
        replace_existing=True,
    )
    scheduler.start()
    return scheduler
