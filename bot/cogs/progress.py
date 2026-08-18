import discord
from discord import app_commands
from discord.ext import commands

from bot.db.session import get_session
from bot.services.progress_service import build_weekly_report, get_or_create_user
from bot.utils.embeds import weekly_report_embed


class Progress(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="progress", description="See your weekly learning report")
    async def progress(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        async with get_session() as session:
            user = await get_or_create_user(session, interaction.user.id, interaction.user.display_name)
            report = await build_weekly_report(session, user.id)
            streak = user.streak_count
            await session.commit()

        await interaction.followup.send(
            embed=weekly_report_embed(interaction.user.display_name, report, streak)
        )

    @app_commands.command(name="stats", description="Alias for /progress")
    async def stats(self, interaction: discord.Interaction) -> None:
        await self.progress.callback(self, interaction)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Progress(bot))
