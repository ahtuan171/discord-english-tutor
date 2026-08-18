import random

import discord
from discord import app_commands
from discord.ext import commands

from bot.db.models import ParaphraseAttempt
from bot.db.session import get_session
from bot.services.lesson_service import get_lesson_vocabulary, get_or_create_today_lesson
from bot.services.paraphrase_service import grade_paraphrase
from bot.services.progress_service import get_or_create_user, log_mistake, touch_streak
from bot.services.quiz_service import detect_mistake
from bot.utils.embeds import paraphrase_feedback_embed, paraphrase_prompt_embed

ANSWER_TIMEOUT_SECONDS = 180


class Practice(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="paraphrase", description="Practice paraphrasing today's sentence")
    async def paraphrase(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        async with get_session() as session:
            user = await get_or_create_user(
                session, interaction.user.id, interaction.user.display_name
            )
            lesson, _ = await get_or_create_today_lesson(session, interaction.channel_id)
            await session.commit()
            sentences = lesson.paraphrase_sentences or []
            lesson_id = lesson.id
            user_id = user.id

        if not sentences:
            await interaction.followup.send("No paraphrase sentences available today. Try `/daily` first.")
            return

        sentence = random.choice(sentences)
        await interaction.followup.send(embed=paraphrase_prompt_embed(sentence))

        def check(m: discord.Message) -> bool:
            return m.author.id == interaction.user.id and m.channel.id == interaction.channel_id

        try:
            reply = await self.bot.wait_for("message", check=check, timeout=ANSWER_TIMEOUT_SECONDS)
        except TimeoutError:
            await interaction.followup.send("⌛ No answer received in time. Try `/paraphrase` again anytime.")
            return

        result = await grade_paraphrase(sentence, reply.content)
        mistake = await detect_mistake(reply.content)

        async with get_session() as session:
            session.add(
                ParaphraseAttempt(
                    user_id=user_id,
                    lesson_id=lesson_id,
                    original_sentence=sentence,
                    user_answer=reply.content,
                    score=result.get("score", 0),
                    feedback=result.get("feedback", ""),
                )
            )
            if mistake.get("has_mistake"):
                await log_mistake(session, user_id, mistake)
            await touch_streak(session, await get_or_create_user(session, interaction.user.id, interaction.user.display_name))
            await session.commit()

        await reply.reply(embed=paraphrase_feedback_embed(sentence, reply.content, result))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Practice(bot))
