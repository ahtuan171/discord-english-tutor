import discord

from bot.db.models import DailyLesson, Vocabulary

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


def paraphrase_prompt_embed(sentence: str) -> discord.Embed:
    embed = discord.Embed(
        title="🧠 Paraphrase Practice",
        description=f"Rewrite this sentence without changing its meaning:\n\n**{sentence}**",
        color=BRAND_COLOR,
    )
    embed.set_footer(text="Reply in this channel with your paraphrase.")
    return embed


def paraphrase_feedback_embed(original: str, answer: str, result: dict) -> discord.Embed:
    embed = discord.Embed(
        title="✅ Paraphrase Feedback" if result.get("score", 0) >= 6 else "📝 Paraphrase Feedback",
        color=BRAND_COLOR,
    )
    embed.add_field(name="Original", value=original, inline=False)
    embed.add_field(name="Your answer", value=answer, inline=False)
    embed.add_field(name="Score", value=f"{result.get('score', '?')}/10", inline=True)
    if result.get("good_swaps"):
        embed.add_field(name="Good swaps", value="\n".join(result["good_swaps"]), inline=False)
    embed.add_field(name="Feedback", value=result.get("feedback", ""), inline=False)
    if result.get("better_alternative"):
        embed.add_field(
            name="⭐ Band 7+ alternative", value=result["better_alternative"], inline=False
        )
    return embed


def writing_embed(lesson: DailyLesson) -> discord.Embed:
    embed = discord.Embed(
        title="✍️ IELTS Writing Task 2",
        description=lesson.writing_question,
        color=BRAND_COLOR,
    )
    embed.add_field(name="📖 Sample paragraph", value=lesson.writing_sample, inline=False)
    if lesson.writing_annotations:
        notes = "\n".join(
            f"**{a['phrase']}** ({a['type']}) — {a['note']}" for a in lesson.writing_annotations
        )
        embed.add_field(name="Annotations", value=notes, inline=False)
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
    if report["mistake_counts"]:
        mistakes = "\n".join(f"- {cat}: {count}" for cat, count in report["mistake_counts"].items())
        embed.add_field(name="Frequent writing issues", value=mistakes, inline=False)
    embed.add_field(name="Coach's note", value=report["summary"], inline=False)
    return embed
