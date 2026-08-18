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


class DailyMode(str, enum.Enum):
    normal = "normal"
    busy = "busy"
    streak_saver = "streak_saver"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    discord_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100), default="")
    streak_count: Mapped[int] = mapped_column(Integer, default=0)
    last_active_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    preferred_mode: Mapped[DailyMode] = mapped_column(
        Enum(DailyMode), default=DailyMode.normal
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    vocab_progress: Mapped[list["UserVocabulary"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    mistakes: Mapped[list["MistakeLog"]] = relationship(
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
    __tablename__ = "daily_lessons"
    __table_args__ = (UniqueConstraint("channel_id", "lesson_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    channel_id: Mapped[int] = mapped_column(BigInteger)
    lesson_date: Mapped[datetime.date] = mapped_column(Date)
    vocabulary_ids: Mapped[list] = mapped_column(JSON, default=list)
    paraphrase_sentences: Mapped[list] = mapped_column(JSON, default=list)
    writing_question: Mapped[str] = mapped_column(Text, default="")
    writing_sample: Mapped[str] = mapped_column(Text, default="")
    writing_annotations: Mapped[list] = mapped_column(JSON, default=list)
    sent_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)


class ParaphraseAttempt(Base):
    __tablename__ = "paraphrase_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    lesson_id: Mapped[int | None] = mapped_column(ForeignKey("daily_lessons.id"), nullable=True)
    original_sentence: Mapped[str] = mapped_column(Text)
    user_answer: Mapped[str] = mapped_column(Text)
    score: Mapped[int] = mapped_column(Integer, default=0)
    feedback: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )


class WritingAttempt(Base):
    __tablename__ = "writing_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    lesson_id: Mapped[int | None] = mapped_column(ForeignKey("daily_lessons.id"), nullable=True)
    question: Mapped[str] = mapped_column(Text)
    user_text: Mapped[str] = mapped_column(Text)
    feedback: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    lesson_id: Mapped[int | None] = mapped_column(ForeignKey("daily_lessons.id"), nullable=True)
    question: Mapped[str] = mapped_column(Text)
    user_answer: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )


class MistakeLog(Base):
    __tablename__ = "mistake_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    wrong_text: Mapped[str] = mapped_column(Text)
    corrected_text: Mapped[str] = mapped_column(Text)
    reason: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(50), default="general")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    user: Mapped["User"] = relationship(back_populates="mistakes")
