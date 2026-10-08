from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WatchTicket(Base):
    __tablename__ = "watch_tickets"

    watch_ticket_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    youtube_id: Mapped[str | None] = mapped_column(ForeignKey("videos.youtube_id", ondelete="SET NULL"), nullable=True)
    session_id: Mapped[int | None] = mapped_column(ForeignKey("sessions.session_id", ondelete="SET NULL"), nullable=True)
    ticket: Mapped[int] = mapped_column(Integer, default=0)
    sub_ticket: Mapped[int] = mapped_column(Integer, default=0)


class Subscription(Base):
    __tablename__ = "subscriptions"

    subscription_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlists.playlist_id", ondelete="CASCADE"), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="subscriptions")
    playlist = relationship("Playlist")


class ActivityLog(Base):
    __tablename__ = "logs"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    date_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="logs")


class EmailConfirmation(Base):
    __tablename__ = "email_confirmations"

    passcode: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    timer: Mapped[int] = mapped_column(Integer, default=600)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="email_confirmations")


class GenerationLock(Base):
    __tablename__ = "generation_locks"

    lock_key: Mapped[str] = mapped_column(String(255), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
