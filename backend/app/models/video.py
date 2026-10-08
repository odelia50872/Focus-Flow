from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Video(Base):
    __tablename__ = "videos"

    video_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    youtube_id: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    upload_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    subject_name: Mapped[str] = mapped_column(String(120), default="general")
    added_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    length_seconds: Mapped[int] = mapped_column(Integer, default=0)

    uploader = relationship("User", back_populates="videos")
    watch_items = relationship("WatchItem", back_populates="video", cascade="all, delete-orphan")
    playlist_items = relationship("PlaylistItem", back_populates="video", cascade="all, delete-orphan")
    group_items = relationship("GroupVideoItem", back_populates="video", cascade="all, delete-orphan")
    transcripts = relationship("Transcript", back_populates="video", cascade="all, delete-orphan")
    summaries = relationship("Summary", back_populates="video", cascade="all, delete-orphan")
    question_groups = relationship("QuestionGroup", back_populates="video", cascade="all, delete-orphan")
