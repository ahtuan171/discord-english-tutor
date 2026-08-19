import discord
from discord import app_commands
from discord.ext import commands

from bot import config
from bot.cogs.review import ReviewView
from bot.db.session import get_session
from bot.services.progress_service import get_due_review_words, get_or_create_user


class Quick(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="quick", description="Streak Saver — a 1-minute review when you're busy")
    async def quick(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        async with get_session() as session:
            user = await get_or_create_user(session, interaction.user.id, interaction.user.display_name)
            due_words = await get_due_review_words(session, user.id, limit=config.QUICK_MODE_WORD_COUNT)
            await session.commit()
            user_id = user.id

        if not due_words:
            await interaction.followup.send(
                "No weak/learning words to review right now. Try `/vocab` to learn some new words. 🔥"
            )
            return

        await interaction.followup.send(
            "🕷️ **Quick Mode** — you don't need to study everything today. Let's just keep the streak alive."
        )
        for v in due_words:
            embed = discord.Embed(
                title=v.word,
                description=f"{v.definition}\n*{v.example}*",
                color=discord.Color.orange(),
            )
            await interaction.channel.send(embed=embed, view=ReviewView(user_id, v.id, v.word))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Quick(bot))
