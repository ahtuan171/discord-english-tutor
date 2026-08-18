import discord
from discord import app_commands
from discord.ext import commands

from bot.db.session import get_session
from bot.services.progress_service import get_due_review_words, get_or_create_user, record_review_result, touch_streak


class ReviewView(discord.ui.View):
    def __init__(self, user_id: int, vocabulary_id: int, word: str) -> None:
        super().__init__(timeout=120)
        self.user_id = user_id
        self.vocabulary_id = vocabulary_id
        self.word = word

    async def _handle(self, interaction: discord.Interaction, result: str) -> None:
        async with get_session() as session:
            await record_review_result(session, self.user_id, self.vocabulary_id, result)
            db_user = await get_or_create_user(session, interaction.user.id, interaction.user.display_name)
            await touch_streak(session, db_user)
            await session.commit()

        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"Noted for **{self.word}**. ({result})", ephemeral=True)

    @discord.ui.button(label="I know", style=discord.ButtonStyle.success)
    async def know(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self._handle(interaction, "know")

    @discord.ui.button(label="Almost", style=discord.ButtonStyle.primary)
    async def almost(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self._handle(interaction, "almost")

    @discord.ui.button(label="Don't know", style=discord.ButtonStyle.danger)
    async def dont_know(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self._handle(interaction, "dont_know")


class Review(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="review", description="Spaced-repetition review of your weak/learning words")
    async def review(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        async with get_session() as session:
            user = await get_or_create_user(session, interaction.user.id, interaction.user.display_name)
            due_words = await get_due_review_words(session, user.id, limit=8)
            await session.commit()
            user_id = user.id

        if not due_words:
            await interaction.followup.send("🎉 Nothing due for review right now. Great job keeping up!")
            return

        await interaction.followup.send(f"🔄 You have **{len(due_words)}** word(s) due for review:")
        for v in due_words:
            embed = discord.Embed(
                title=v.word,
                description=f"{v.definition}\n*{v.example}*",
                color=discord.Color.orange(),
            )
            await interaction.channel.send(embed=embed, view=ReviewView(user_id, v.id, v.word))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Review(bot))
