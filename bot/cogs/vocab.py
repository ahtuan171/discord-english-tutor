import discord
from discord import app_commands
from discord.ext import commands

from bot import config
from bot.db.session import get_session
from bot.services.progress_service import enroll_vocabulary, get_or_create_user, touch_streak
from bot.services.vocabulary_service import generate_daily_words
from bot.utils.embeds import vocabulary_embed


class Vocab(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="vocab", description="Get the next batch of new vocabulary words to learn"
    )
    async def vocab(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        async with get_session() as session:
            user = await get_or_create_user(
                session, interaction.user.id, interaction.user.display_name
            )
            await touch_streak(session, user)

            vocab_list = await generate_daily_words(session, config.DAILY_WORD_COUNT)
            await enroll_vocabulary(session, user, [v.id for v in vocab_list])
            await session.commit()

        if not vocab_list:
            await interaction.followup.send(
                "🎉 You've learned every word in the word bank! There's nothing new right now, "
                "but you can keep practicing what you've learned with `/review` or `/quick`. "
                f"🔥 Streak: **{user.streak_count}** day(s).\n"
                "(Want more words? Add them to `data/vocabulary/*.json`.)"
            )
            return

        await interaction.followup.send(embed=vocabulary_embed(vocab_list))
        await interaction.followup.send(
            f"Added to your review list — run `/review` anytime (e.g. end of day) to practice "
            f"these with I know / Almost / Don't know. Call `/vocab` again anytime for more new "
            f"words. 🔥 Streak: **{user.streak_count}** day(s)."
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Vocab(bot))
