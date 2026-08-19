import datetime

from sqlalchemy import select

from bot.db.models import User, UserVocabulary, Vocabulary, VocabStatus

REVIEW_INTERVALS_DAYS = {
    "know": 4,
    "almost": 2,
    "dont_know": 0,  # review again same/next day
}


async def get_or_create_user(session, discord_id: int, display_name: str) -> User:
    user = (
        await session.execute(select(User).where(User.discord_id == discord_id))
    ).scalar_one_or_none()
    if user:
        return user

    user = User(discord_id=discord_id, display_name=display_name)
    session.add(user)
    await session.flush()
    return user


async def touch_streak(session, user: User) -> None:
    today = datetime.date.today()
    if user.last_active_date == today:
        return
    yesterday = today - datetime.timedelta(days=1)
    user.streak_count = user.streak_count + 1 if user.last_active_date == yesterday else 1
    user.last_active_date = today


async def enroll_vocabulary(session, user: User, vocab_ids: list[int]) -> None:
    existing_ids = set(
        (
            await session.execute(
                select(UserVocabulary.vocabulary_id).where(
                    UserVocabulary.user_id == user.id,
                    UserVocabulary.vocabulary_id.in_(vocab_ids),
                )
            )
        )
        .scalars()
        .all()
    )
    for vid in vocab_ids:
        if vid in existing_ids:
            continue
        session.add(UserVocabulary(user_id=user.id, vocabulary_id=vid, status=VocabStatus.new))


async def record_review_result(session, user_id: int, vocabulary_id: int, result: str) -> None:
    """result: 'know' | 'almost' | 'dont_know'"""
    uv = (
        await session.execute(
            select(UserVocabulary).where(
                UserVocabulary.user_id == user_id,
                UserVocabulary.vocabulary_id == vocabulary_id,
            )
        )
    ).scalar_one_or_none()
    if not uv:
        uv = UserVocabulary(user_id=user_id, vocabulary_id=vocabulary_id)
        session.add(uv)

    now = datetime.datetime.utcnow()
    uv.last_reviewed_at = now

    if result == "know":
        uv.correct_count += 1
        uv.status = VocabStatus.mastered if uv.correct_count >= 3 else VocabStatus.learning
    elif result == "almost":
        uv.status = VocabStatus.learning
    else:
        uv.wrong_count += 1
        uv.status = VocabStatus.weak

    days = REVIEW_INTERVALS_DAYS.get(result, 1)
    uv.next_review_at = now + datetime.timedelta(days=days)


async def get_due_review_words(session, user_id: int, limit: int = 5) -> list[Vocabulary]:
    now = datetime.datetime.utcnow()
    rows = (
        await session.execute(
            select(Vocabulary)
            .join(UserVocabulary, UserVocabulary.vocabulary_id == Vocabulary.id)
            .where(
                UserVocabulary.user_id == user_id,
                UserVocabulary.status.in_(
                    [VocabStatus.new, VocabStatus.weak, VocabStatus.learning]
                ),
                (UserVocabulary.next_review_at.is_(None))
                | (UserVocabulary.next_review_at <= now),
            )
            .limit(limit)
        )
    ).scalars().all()
    return rows


def _build_summary(total_learned: int, mastered_count: int, weak_count: int, streak: int) -> str:
    if total_learned == 0:
        return "Run `/vocab` to get your first batch of vocabulary and start your streak!"
    if weak_count == 0 and mastered_count > 0:
        return f"Great work — {mastered_count} word(s) mastered and nothing weak right now. Keep the streak going!"
    if weak_count > 0:
        return f"Focus next: review your {weak_count} weak word(s) with `/review` or `/quick`."
    return f"You've learned {total_learned} word(s) so far. Keep it up, {streak}-day streak!"


async def build_weekly_report(session, user_id: int, streak: int = 0) -> dict:
    mastered = (
        await session.execute(
            select(Vocabulary.word)
            .join(UserVocabulary, UserVocabulary.vocabulary_id == Vocabulary.id)
            .where(UserVocabulary.user_id == user_id, UserVocabulary.status == VocabStatus.mastered)
        )
    ).scalars().all()

    weak = (
        await session.execute(
            select(Vocabulary.word)
            .join(UserVocabulary, UserVocabulary.vocabulary_id == Vocabulary.id)
            .where(UserVocabulary.user_id == user_id, UserVocabulary.status == VocabStatus.weak)
        )
    ).scalars().all()

    total_learned = (
        await session.execute(
            select(UserVocabulary.id).where(UserVocabulary.user_id == user_id)
        )
    ).scalars().all()

    return {
        "total_learned": len(total_learned),
        "mastered": mastered,
        "weak": weak,
        "summary": _build_summary(len(total_learned), len(mastered), len(weak), streak),
    }
