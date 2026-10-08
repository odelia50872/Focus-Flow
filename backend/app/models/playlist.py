from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Playlist(Base):
    __tablename__ = "playlists"

    playlist_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    playlist_name: Mapped[str] = mapped_column(String(255), nullable=False)
    permission: Mapped[str] = mapped_column(String(32), default="private")
    next_item_order: Mapped[int] = mapped_column(Integer, default=1)

    user = relationship("User", back_populates="playlists")
    items = relationship("PlaylistItem", back_populates="playlist", cascade="all, delete-orphan")
    group_links = relationship("GroupPlaylistItem", back_populates="playlist", cascade="all, delete-orphan")


class PlaylistItem(Base):
    __tablename__ = "playlist_items"

    playlist_item_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    video_id: Mapped[int] = mapped_column(ForeignKey("videos.video_id", ondelete="CASCADE"), nullable=False)
    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlists.playlist_id", ondelete="CASCADE"), nullable=False)
    item_order: Mapped[int] = mapped_column(Integer, nullable=False)

    playlist = relationship("Playlist", back_populates="items")
    video = relationship("Video", back_populates="playlist_items")
