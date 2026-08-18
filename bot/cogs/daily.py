import discord
from discord import app_commands
from discord.ext import commands

from bot.db.session import get_session
from bot.services.lesson_service import get_lesson_vocabulary, get_or_create_today_lesson
from bot.services.progress_service import enroll_vocabulary, get_or_create_user, touch_streak
from bot.utils.embeds import vocabulary_embed, writing_embed


class Daily(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="daily", description="Get today's vocabulary + writing lesson")
    async def daily(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        async with get_session() as session:
            user = await get_or_create_user(
                session, interaction.user.id, interaction.user.display_name
            )
            await touch_streak(session, user)

            lesson, created = await get_or_create_today_lesson(session, interaction.channel_id)
            vocab_list = await get_lesson_vocabulary(session, lesson)
            await enroll_vocabulary(session, user, [v.id for v in vocab_list])
            await session.commit()

        await interaction.followup.send(embed=vocabulary_embed(vocab_list))
        await interaction.followup.send(embed=writing_embed(lesson))
        await interaction.followup.send(
            "Next: run `/paraphrase` to practice, `/quiz` for active recall, "
            f"or `/quick` if you're short on time. 🔥 Streak: **{user.streak_count}** day(s)."
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Daily(bot))
