import discord
from discord import app_commands
from discord.ext import commands

from bot.db.models import WritingAttempt
from bot.db.session import get_session
from bot.services.progress_service import get_or_create_user, log_mistake, touch_streak
from bot.services.lesson_service import get_or_create_today_lesson
from bot.services.quiz_service import detect_mistake
from bot.utils.embeds import writing_embed

ANSWER_TIMEOUT_SECONDS = 600


class Writing(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="writing", description="View today's IELTS writing question and try answering it")
    async def writing(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        async with get_session() as session:
            user = await get_or_create_user(
                session, interaction.user.id, interaction.user.display_name
            )
            lesson, _ = await get_or_create_today_lesson(session, interaction.channel_id)
            await session.commit()
            user_id, lesson_id, question = user.id, lesson.id, lesson.writing_question

        await interaction.followup.send(embed=writing_embed(lesson))
        await interaction.followup.send(
            "✍️ Want to try answering? Reply with a few sentences within 10 minutes "
            "(or skip — no pressure)."
        )

        def check(m: discord.Message) -> bool:
            return m.author.id == interaction.user.id and m.channel.id == interaction.channel_id

        try:
            reply = await self.bot.wait_for("message", check=check, timeout=ANSWER_TIMEOUT_SECONDS)
        except TimeoutError:
            return

        mistake = await detect_mistake(reply.content)

        async with get_session() as session:
            session.add(
                WritingAttempt(
                    user_id=user_id,
                    lesson_id=lesson_id,
                    question=question,
                    user_text=reply.content,
                )
            )
            if mistake.get("has_mistake"):
                await log_mistake(session, user_id, mistake)
                await session.commit()
                await reply.reply(
                    f"📝 Noted one thing to review: ❌ `{mistake['wrong_text']}` → ✅ `{mistake['corrected_text']}`\n"
                    f"_{mistake.get('reason', '')}_"
                )
            else:
                await session.commit()
                await reply.reply("✅ Nice, no obvious grammar issues spotted. Keep it up!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Writing(bot))
