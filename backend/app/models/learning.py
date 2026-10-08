from datetime import datetime, time

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Time, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Transcript(Base):
    __tablename__ = "transcripts"

    transcript_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    youtube_id: Mapped[str] = mapped_column(ForeignKey("videos.youtube_id", ondelete="CASCADE"), nullable=False)
    language: Mapped[str] = mapped_column(String(16), default="en")
    text: Mapped[str] = mapped_column(Text, default="")

    video = relationship("Video", back_populates="transcripts")


class Summary(Base):
    __tablename__ = "summaries"

    summary_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    youtube_id: Mapped[str] = mapped_column(ForeignKey("videos.youtube_id", ondelete="CASCADE"), nullable=False)
    language: Mapped[str] = mapped_column(String(16), default="en")
    summary: Mapped[dict] = mapped_column(JSONB, default=dict)

    video = relationship("Video", back_populates="summaries")


class QuestionGroup(Base):
    __tablename__ = "question_groups"

    question_group_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    youtube_id: Mapped[str] = mapped_column(ForeignKey("videos.youtube_id", ondelete="CASCADE"), nullable=False)
    language: Mapped[str] = mapped_column(String(16), default="en")

    video = relationship("Video", back_populates="question_groups")
    questions = relationship("Question", back_populates="group", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    question_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_group_id: Mapped[int] = mapped_column(
        ForeignKey("question_groups.question_group_id", ondelete="CASCADE"), nullable=False
    )
    q_id: Mapped[str] = mapped_column(String(64), nullable=False)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)
    question_origin: Mapped[time | None] = mapped_column(Time, nullable=True)
    question_explanation_end: Mapped[time | None] = mapped_column(Time, nullable=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer1: Mapped[str] = mapped_column(Text, default="")
    answer2: Mapped[str] = mapped_column(Text, default="")
    answer3: Mapped[str] = mapped_column(Text, default="")
    answer4: Mapped[str] = mapped_column(Text, default="")
    keywords: Mapped[list] = mapped_column(JSONB, default=list)
    explanation_snippet: Mapped[str] = mapped_column(Text, default="")

    group = relationship("QuestionGroup", back_populates="questions")
