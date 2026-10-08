from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    creation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    permission: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    sessions = relationship("AuthSession", back_populates="user", cascade="all, delete-orphan")
    videos = relationship("Video", back_populates="uploader")
    content_items = relationship("ContentItem", back_populates="owner", cascade="all, delete-orphan")
    watch_items = relationship("WatchItem", back_populates="user", cascade="all, delete-orphan")
    playlists = relationship("Playlist", back_populates="user", cascade="all, delete-orphan")
    groups = relationship("Group", back_populates="owner", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    email_confirmations = relationship("EmailConfirmation", back_populates="user", cascade="all, delete-orphan")
