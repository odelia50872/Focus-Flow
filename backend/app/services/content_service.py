from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.content import ContentItem
from app.models.user import User
from app.models.video import Video
from app.schemas.content import ContentCreate, ContentPublic
from app.schemas.video import VideoCreate, VideoUpdate
from app.utils.content import parse_youtube_id, validate_content
from app.utils.ids import as_id, iso_utc


def to_content_public(item: ContentItem) -> ContentPublic:
    return ContentPublic(
        id=as_id(item.content_id),
        title=item.title,
        type=item.type,
        source=item.source,
        created_at=iso_utc(item.created_at) or "",
    )


def list_content(db: Session, user: User) -> list[ContentItem]:
    return list(
        db.scalars(
            select(ContentItem).where(ContentItem.user_id == user.user_id).order_by(ContentItem.created_at.desc())
        ).all()
    )


def get_owned_content(db: Session, user: User, content_id: int) -> ContentItem:
    item = db.get(ContentItem, content_id)
    if item is None or item.user_id != user.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return item


def _ensure_video(db: Session, user: User, youtube_id: str, title: str) -> Video:
    video = db.scalar(select(Video).where(Video.youtube_id == youtube_id))
    if video:
        return video
    video = Video(
        youtube_id=youtube_id,
        name=title,
        description="",
        subject_name="learning",
        upload_by=user.user_id,
    )
    db.add(video)
    db.flush()
    return video


def create_content(db: Session, user: User, payload: ContentCreate) -> ContentItem:
    kind, source, youtube_id = validate_content(payload.type, payload.source)
    title = payload.title.strip()
    if youtube_id:
        _ensure_video(db, user, youtube_id, title)
    item = ContentItem(
        user_id=user.user_id,
        title=title,
        type=kind,
        source=source,
        youtube_id=youtube_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def delete_content(db: Session, user: User, content_id: int) -> None:
    item = get_owned_content(db, user, content_id)
    db.delete(item)
    db.commit()


def list_videos(db: Session) -> list[Video]:
    return list(db.scalars(select(Video).order_by(Video.added_date.desc())).all())


def get_video(db: Session, video_id: int) -> Video:
    video = db.get(Video, video_id)
    if video is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return video


def get_video_by_youtube_id(db: Session, youtube_id: str) -> Video | None:
    return db.scalar(select(Video).where(Video.youtube_id == youtube_id))


def create_video(db: Session, payload: VideoCreate, user: User) -> Video:
    youtube_id = parse_youtube_id(payload.youtube_id)
    existing = get_video_by_youtube_id(db, youtube_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="YouTube id already exists")
    video = Video(
        youtube_id=youtube_id,
        name=payload.name.strip(),
        description=payload.description.strip(),
        subject_name=payload.subject_name.strip() or "general",
        length_seconds=payload.length_seconds,
        upload_by=user.user_id,
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


def update_video(db: Session, video_id: int, payload: VideoUpdate, user: User) -> Video:
    video = get_video(db, video_id)
    if video.upload_by is not None and video.upload_by != user.user_id and user.permission < 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(video, key, value)
    db.commit()
    db.refresh(video)
    return video


def delete_video(db: Session, video_id: int, user: User) -> None:
    video = get_video(db, video_id)
    if video.upload_by is not None and video.upload_by != user.user_id and user.permission < 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    db.delete(video)
    db.commit()
