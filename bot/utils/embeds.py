import discord

from bot.db.models import Vocabulary

BRAND_COLOR = discord.Color.blurple()


def vocabulary_embed(vocab_list: list[Vocabulary]) -> discord.Embed:
    embed = discord.Embed(
        title="🕷️ Today's 10 Words",
        color=BRAND_COLOR,
    )
    for i, v in enumerate(vocab_list, start=1):
        pos = f" ({v.part_of_speech})" if v.part_of_speech else ""
        embed.add_field(
            name=f"{i}. {v.word}{pos}",
            value=f"{v.definition}\n*{v.example}*",
            inline=False,
        )
    return embed


def weekly_report_embed(display_name: str, report: dict, streak: int) -> discord.Embed:
    embed = discord.Embed(
        title=f"📊 {display_name}'s Weekly Report",
        color=BRAND_COLOR,
    )
    embed.add_field(name="🔥 Streak", value=f"{streak} day(s)", inline=True)
    embed.add_field(name="Vocabulary learned", value=str(report["total_learned"]), inline=True)
    embed.add_field(
        name="Strong",
        value=", ".join(report["mastered"]) or "—",
        inline=False,
    )
    embed.add_field(
        name="Needs review",
        value=", ".join(report["weak"]) or "—",
        inline=False,
    )
    embed.add_field(name="Next step", value=report["summary"], inline=False)
    return embed
