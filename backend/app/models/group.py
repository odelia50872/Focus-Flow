from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Group(Base):
    __tablename__ = "groups"

    group_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    group_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    next_item_order: Mapped[int] = mapped_column(Integer, default=1)

    owner = relationship("User", back_populates="groups")
    video_items = relationship("GroupVideoItem", back_populates="group", cascade="all, delete-orphan")
    playlist_items = relationship("GroupPlaylistItem", back_populates="group", cascade="all, delete-orphan")


class GroupVideoItem(Base):
    __tablename__ = "group_video_items"

    group_video_item_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.group_id", ondelete="CASCADE"), nullable=False)
    video_id: Mapped[int] = mapped_column(ForeignKey("videos.video_id", ondelete="CASCADE"), nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    item_order: Mapped[int] = mapped_column(Integer, nullable=False)

    group = relationship("Group", back_populates="video_items")
    video = relationship("Video", back_populates="group_items")


class GroupPlaylistItem(Base):
    __tablename__ = "group_playlist_items"

    group_playlist_item_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.group_id", ondelete="CASCADE"), nullable=False)
    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlists.playlist_id", ondelete="CASCADE"), nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    item_order: Mapped[int] = mapped_column(Integer, nullable=False)

    group = relationship("Group", back_populates="playlist_items")
    playlist = relationship("Playlist", back_populates="group_links")
