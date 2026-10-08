from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WatchItem(Base):
    __tablename__ = "watch_items"

    watch_item_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    content_id: Mapped[int] = mapped_column(ForeignKey("content_items.content_id", ondelete="CASCADE"), nullable=False)
    youtube_id: Mapped[str | None] = mapped_column(ForeignKey("videos.youtube_id", ondelete="SET NULL"), nullable=True)
    current_time: Mapped[float] = mapped_column(Float, default=0.0)
    save_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active")  # active | ended
    average_focus: Mapped[float | None] = mapped_column(Float, nullable=True)
    next_ticket: Mapped[int] = mapped_column(Integer, default=1)
    next_sub_ticket: Mapped[int] = mapped_column(Integer, default=1)

    user = relationship("User", back_populates="watch_items")
    content = relationship("ContentItem", back_populates="watch_items")
    video = relationship("Video", back_populates="watch_items")
    watch_data = relationship("WatchData", back_populates="watch_item", cascade="all, delete-orphan")


class WatchData(Base):
    __tablename__ = "watch_data"

    watch_data_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    watch_item_id: Mapped[int] = mapped_column(ForeignKey("watch_items.watch_item_id", ondelete="CASCADE"), nullable=False)
    log_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    vid_watch_time: Mapped[float] = mapped_column(Float, default=0.0)
    interval: Mapped[float] = mapped_column(Float, default=1.0)
    ticket: Mapped[int] = mapped_column(Integer, default=0)
    sub_ticket: Mapped[int] = mapped_column(Integer, default=0)

    watch_item = relationship("WatchItem", back_populates="watch_data")
    log_data = relationship("LogData", back_populates="watch_data", cascade="all, delete-orphan")


class LogData(Base):
    __tablename__ = "log_data"

    log_data_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    watch_data_id: Mapped[int] = mapped_column(ForeignKey("watch_data.watch_data_id", ondelete="CASCADE"), nullable=False)
    fps_num: Mapped[float] = mapped_column(Float, default=1.0)
    extraction_type: Mapped[str] = mapped_column(String(64), default="face_landmarks")

    watch_data = relationship("WatchData", back_populates="log_data")
    model_results = relationship("ModelResult", back_populates="log_data", cascade="all, delete-orphan")


class ModelResult(Base):
    __tablename__ = "model_results"

    model_result_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    log_data_id: Mapped[int] = mapped_column(ForeignKey("log_data.log_data_id", ondelete="CASCADE"), nullable=False)
    model: Mapped[str] = mapped_column(String(64), nullable=False)
    result: Mapped[float] = mapped_column(Float, nullable=False)

    log_data = relationship("LogData", back_populates="model_results")
