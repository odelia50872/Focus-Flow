from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.playlist import Playlist, PlaylistItem
from app.models.user import User
from app.models.video import Video
from app.schemas.playlist import PlaylistCreate, PlaylistItemCreate, PlaylistItemPublic, PlaylistPublic
from app.schemas.video import VideoPublic
from app.services.ops_service import log_action


def _to_public(playlist: Playlist) -> PlaylistPublic:
    items = []
    for item in sorted(playlist.items, key=lambda i: i.item_order):
        items.append(
            PlaylistItemPublic(
                playlist_item_id=item.playlist_item_id,
                video_id=item.video_id,
                playlist_id=item.playlist_id,
                item_order=item.item_order,
                video=VideoPublic.model_validate(item.video) if item.video else None,
            )
        )
    return PlaylistPublic(
        playlist_id=playlist.playlist_id,
        user_id=playlist.user_id,
        playlist_name=playlist.playlist_name,
        permission=playlist.permission,
        next_item_order=playlist.next_item_order,
        items=items,
    )


def _owned(db: Session, user: User, playlist_id: int) -> Playlist:
    playlist = db.scalar(
        select(Playlist)
        .options(joinedload(Playlist.items).joinedload(PlaylistItem.video))
        .where(Playlist.playlist_id == playlist_id)
    )
    if playlist is None or playlist.user_id != user.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")
    return playlist


def list_playlists(db: Session, user: User) -> list[PlaylistPublic]:
    playlists = list(
        db.scalars(
            select(Playlist)
            .options(joinedload(Playlist.items).joinedload(PlaylistItem.video))
            .where(Playlist.user_id == user.user_id)
            .order_by(Playlist.playlist_id.desc())
        )
        .unique()
        .all()
    )
    return [_to_public(p) for p in playlists]


def create_playlist(db: Session, user: User, payload: PlaylistCreate) -> PlaylistPublic:
    playlist = Playlist(
        user_id=user.user_id,
        playlist_name=payload.playlist_name.strip(),
        permission=payload.permission.strip() or "private",
    )
    db.add(playlist)
    db.flush()
    log_action(db, user.user_id, f"playlist.create:{playlist.playlist_id}")
    db.commit()
    db.refresh(playlist)
    return _to_public(playlist)


def add_item(db: Session, user: User, playlist_id: int, payload: PlaylistItemCreate) -> PlaylistPublic:
    playlist = _owned(db, user, playlist_id)
    video = db.get(Video, payload.video_id)
    if video is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    exists = db.scalar(
        select(PlaylistItem).where(
            PlaylistItem.playlist_id == playlist_id,
            PlaylistItem.video_id == payload.video_id,
        )
    )
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Video already in playlist")

    item = PlaylistItem(
        playlist_id=playlist_id,
        video_id=payload.video_id,
        item_order=playlist.next_item_order,
    )
    playlist.next_item_order += 1
    db.add(item)
    log_action(db, user.user_id, f"playlist.add_video:{playlist_id}:{payload.video_id}")
    db.commit()
    return _to_public(_owned(db, user, playlist_id))


def remove_item(db: Session, user: User, playlist_id: int, item_id: int) -> None:
    playlist = _owned(db, user, playlist_id)
    item = db.get(PlaylistItem, item_id)
    if item is None or item.playlist_id != playlist.playlist_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist item not found")
    db.delete(item)
    log_action(db, user.user_id, f"playlist.remove_video:{playlist_id}:{item_id}")
    db.commit()
