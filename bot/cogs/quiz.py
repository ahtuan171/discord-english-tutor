import discord
from discord import app_commands
from discord.ext import commands

from bot import config
from bot.db.models import QuizAttempt
from bot.db.session import get_session
from bot.services.lesson_service import get_lesson_vocabulary, get_or_create_today_lesson
from bot.services.progress_service import (
    get_due_review_words,
    get_or_create_user,
    record_review_result,
    touch_streak,
)
from bot.services.quiz_service import generate_recall_quiz, grade_recall_answer

ANSWER_TIMEOUT_SECONDS = 120


async def _ask_and_grade(bot, interaction, question: str, word: str | None) -> bool:
    await interaction.channel.send(f"🧠 {question}")

    def check(m: discord.Message) -> bool:
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel_id

    try:
        reply = await bot.wait_for("message", check=check, timeout=ANSWER_TIMEOUT_SECONDS)
    except TimeoutError:
        await interaction.channel.send("⌛ Skipping — no answer in time.")
        return False

    result = await grade_recall_answer(question, word, reply.content)
    is_correct = bool(result.get("is_correct"))
    icon = "✅" if is_correct else "🔸"
    msg = f"{icon} {result.get('feedback', '')}"
    if not is_correct and result.get("correction"):
        msg += f"\nModel answer: {result['correction']}"
    await reply.reply(msg)
    return is_correct


class Quiz(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="quiz", description="5-minute active recall challenge on today's lesson")
    async def quiz(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        async with get_session() as session:
            user = await get_or_create_user(
                session, interaction.user.id, interaction.user.display_name
            )
            lesson, _ = await get_or_create_today_lesson(session, interaction.channel_id)
            vocab_list = await get_lesson_vocabulary(session, lesson)
            await session.commit()
            user_id, lesson_id = user.id, lesson.id
            words = [v.word for v in vocab_list]
            word_id_by_word = {v.word: v.id for v in vocab_list}
            paraphrase_sentence = (lesson.paraphrase_sentences or ["Technology makes life easier."])[0]

        questions = await generate_recall_quiz(words, paraphrase_sentence, count=5)
        await interaction.followup.send("🧠 **5-minute challenge** — without looking at today's vocabulary:")

        for q in questions:
            await interaction.channel.send(f"**{q['question']}**")

            def check(m: discord.Message) -> bool:
                return m.author.id == interaction.user.id and m.channel.id == interaction.channel_id

            try:
                reply = await self.bot.wait_for("message", check=check, timeout=ANSWER_TIMEOUT_SECONDS)
            except TimeoutError:
                await interaction.channel.send("⌛ Skipping — no answer in time.")
                continue

            result = await grade_recall_answer(q["question"], q.get("word"), reply.content)
            is_correct = bool(result.get("is_correct"))
            icon = "✅" if is_correct else "🔸"
            msg = f"{icon} {result.get('feedback', '')}"
            if not is_correct and result.get("correction"):
                msg += f"\nModel answer: {result['correction']}"
            await reply.reply(msg)

            async with get_session() as session:
                session.add(
                    QuizAttempt(
                        user_id=user_id,
                        lesson_id=lesson_id,
                        question=q["question"],
                        user_answer=reply.content,
                        is_correct=is_correct,
                    )
                )
                word = q.get("word")
                if word and word in word_id_by_word:
                    await record_review_result(
                        session, user_id, word_id_by_word[word], "know" if is_correct else "dont_know"
                    )
                await touch_streak(session, await get_or_create_user(session, interaction.user.id, interaction.user.display_name))
                await session.commit()

        await interaction.channel.send("🎉 Quiz complete! Run `/progress` anytime to see your weekly stats.")

    @app_commands.command(name="quick", description="Streak Saver — a 2-3 minute review when you're busy")
    async def quick(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        async with get_session() as session:
            user = await get_or_create_user(
                session, interaction.user.id, interaction.user.display_name
            )
            due_words = await get_due_review_words(session, user.id, limit=config.QUICK_MODE_WORD_COUNT)
            await session.commit()
            user_id = user.id

        if not due_words:
            await interaction.followup.send(
                "No weak/learning words to review right now. Try `/daily` to start today's lesson. 🔥"
            )
            return

        await interaction.followup.send(
            "🕷️ **Quick Mode** — you don't need to study everything today. Let's just keep the streak alive."
        )

        for v in due_words:
            question = f'What does "{v.word}" mean?'
            is_correct = await _ask_and_grade(self.bot, interaction, question, v.word)
            async with get_session() as session:
                await record_review_result(session, user_id, v.id, "know" if is_correct else "dont_know")
                await touch_streak(session, await get_or_create_user(session, interaction.user.id, interaction.user.display_name))
                await session.commit()

        await interaction.channel.send("🔥 Streak saved. See you tomorrow!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Quiz(bot))
