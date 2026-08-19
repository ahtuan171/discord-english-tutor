import datetime
import enum

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class VocabStatus(str, enum.Enum):
    new = "new"
    learning = "learning"
    mastered = "mastered"
    weak = "weak"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    discord_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100), default="")
    streak_count: Mapped[int] = mapped_column(Integer, default=0)
    last_active_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    vocab_progress: Mapped[list["UserVocabulary"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Vocabulary(Base):
    __tablename__ = "vocabulary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    word: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    part_of_speech: Mapped[str] = mapped_column(String(30), default="")
    definition: Mapped[str] = mapped_column(Text)
    example: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )


class DictionaryEntry(Base):
    """Offline dictionary lookup table, seeded once from the Wordset dataset
    (github.com/wordset/wordset-dictionary, CC-BY-SA 4.0, built on WordNet).
    Vocabulary generation queries this table — no LLM involved."""

    __tablename__ = "dictionary_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    word: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    part_of_speech: Mapped[str] = mapped_column(String(30), default="")
    definition: Mapped[str] = mapped_column(Text)
    example: Mapped[str] = mapped_column(Text, default="")
    synonyms: Mapped[list] = mapped_column(JSON, default=list)


class UserVocabulary(Base):
    __tablename__ = "user_vocabulary"
    __table_args__ = (UniqueConstraint("user_id", "vocabulary_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    vocabulary_id: Mapped[int] = mapped_column(ForeignKey("vocabulary.id"))
    status: Mapped[VocabStatus] = mapped_column(Enum(VocabStatus), default=VocabStatus.new)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    wrong_count: Mapped[int] = mapped_column(Integer, default=0)
    last_reviewed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    next_review_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="vocab_progress")
    vocabulary: Mapped["Vocabulary"] = relationship()


class DailyLesson(Base):
    """Tracks which vocabulary words were sent to a channel on a given day,
    so /daily and the scheduler don't regenerate or resend the same day twice."""

    __tablename__ = "daily_lessons"
    __table_args__ = (UniqueConstraint("channel_id", "lesson_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    channel_id: Mapped[int] = mapped_column(BigInteger)
    lesson_date: Mapped[datetime.date] = mapped_column(Date)
    vocabulary_ids: Mapped[list] = mapped_column(JSON, default=list)
    sent_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
