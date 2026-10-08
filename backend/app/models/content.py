from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ContentItem(Base):
    __tablename__ = "content_items"
    __table_args__ = (UniqueConstraint("user_id", "title", "source", name="uq_content_user_title_source"),)

    content_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    youtube_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="content_items")
    watch_items = relationship("WatchItem", back_populates="content", cascade="all, delete-orphan")
