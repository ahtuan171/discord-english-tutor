import datetime

from sqlalchemy import select

from bot import config
from bot.db.models import DailyLesson, Vocabulary
from bot.services.vocabulary_service import generate_daily_words


async def get_today_lesson(session, channel_id: int) -> DailyLesson | None:
    today = datetime.date.today()
    return (
        await session.execute(
            select(DailyLesson).where(
                DailyLesson.channel_id == channel_id, DailyLesson.lesson_date == today
            )
        )
    ).scalar_one_or_none()


async def get_or_create_today_lesson(session, channel_id: int) -> tuple[DailyLesson, bool]:
    """Returns (lesson, was_created)."""
    existing = await get_today_lesson(session, channel_id)
    if existing:
        return existing, False

    vocab_objs = await generate_daily_words(session, config.DAILY_WORD_COUNT)

    lesson = DailyLesson(
        channel_id=channel_id,
        lesson_date=datetime.date.today(),
        vocabulary_ids=[v.id for v in vocab_objs],
        sent_at=datetime.datetime.utcnow(),
    )
    session.add(lesson)
    await session.flush()
    return lesson, True


async def get_lesson_vocabulary(session, lesson: DailyLesson) -> list[Vocabulary]:
    if not lesson.vocabulary_ids:
        return []
    return (
        await session.execute(select(Vocabulary).where(Vocabulary.id.in_(lesson.vocabulary_ids)))
    ).scalars().all()
