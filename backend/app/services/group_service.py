from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.group import Group, GroupPlaylistItem, GroupVideoItem
from app.models.playlist import Playlist
from app.models.user import User
from app.models.video import Video
from app.schemas.group import (
    GroupCreate,
    GroupPlaylistAdd,
    GroupPlaylistItemPublic,
    GroupPublic,
    GroupVideoAdd,
    GroupVideoItemPublic,
)
from app.schemas.video import VideoPublic
from app.services.ops_service import log_action
from app.services.playlist_service import _to_public as playlist_to_public


def _to_public(group: Group) -> GroupPublic:
    videos = []
    for item in sorted(group.video_items, key=lambda i: i.item_order):
        videos.append(
            GroupVideoItemPublic(
                group_video_item_id=item.group_video_item_id,
                group_id=item.group_id,
                video_id=item.video_id,
                added_at=item.added_at,
                item_order=item.item_order,
                video=VideoPublic.model_validate(item.video) if item.video else None,
            )
        )
    playlists = []
    for item in sorted(group.playlist_items, key=lambda i: i.item_order):
        playlists.append(
            GroupPlaylistItemPublic(
                group_playlist_item_id=item.group_playlist_item_id,
                group_id=item.group_id,
                playlist_id=item.playlist_id,
                added_at=item.added_at,
                item_order=item.item_order,
                playlist=playlist_to_public(item.playlist) if item.playlist else None,
            )
        )
    return GroupPublic(
        group_id=group.group_id,
        user_id=group.user_id,
        group_name=group.group_name,
        description=group.description,
        created_at=group.created_at,
        updated_at=group.updated_at,
        next_item_order=group.next_item_order,
        video_items=videos,
        playlist_items=playlists,
    )


def _owned(db: Session, user: User, group_id: int) -> Group:
    group = db.scalar(
        select(Group)
        .options(
            joinedload(Group.video_items).joinedload(GroupVideoItem.video),
            joinedload(Group.playlist_items).joinedload(GroupPlaylistItem.playlist),
        )
        .where(Group.group_id == group_id)
    )
    if group is None or group.user_id != user.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return group


def list_groups(db: Session, user: User) -> list[GroupPublic]:
    groups = list(
        db.scalars(
            select(Group)
            .options(
                joinedload(Group.video_items).joinedload(GroupVideoItem.video),
                joinedload(Group.playlist_items).joinedload(GroupPlaylistItem.playlist),
            )
            .where(Group.user_id == user.user_id)
            .order_by(Group.updated_at.desc())
        )
        .unique()
        .all()
    )
    return [_to_public(g) for g in groups]


def create_group(db: Session, user: User, payload: GroupCreate) -> GroupPublic:
    group = Group(
        user_id=user.user_id,
        group_name=payload.group_name.strip(),
        description=payload.description.strip(),
    )
    db.add(group)
    db.flush()
    log_action(db, user.user_id, f"group.create:{group.group_id}")
    db.commit()
    db.refresh(group)
    return _to_public(group)


def add_video(db: Session, user: User, group_id: int, payload: GroupVideoAdd) -> GroupPublic:
    group = _owned(db, user, group_id)
    video = db.get(Video, payload.video_id)
    if video is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    exists = db.scalar(
        select(GroupVideoItem).where(
            GroupVideoItem.group_id == group_id,
            GroupVideoItem.video_id == payload.video_id,
        )
    )
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Video already in group")
    db.add(
        GroupVideoItem(group_id=group_id, video_id=payload.video_id, item_order=group.next_item_order)
    )
    group.next_item_order += 1
    log_action(db, user.user_id, f"group.add_video:{group_id}:{payload.video_id}")
    db.commit()
    return _to_public(_owned(db, user, group_id))


def add_playlist(db: Session, user: User, group_id: int, payload: GroupPlaylistAdd) -> GroupPublic:
    group = _owned(db, user, group_id)
    playlist = db.get(Playlist, payload.playlist_id)
    if playlist is None or playlist.user_id != user.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")
    exists = db.scalar(
        select(GroupPlaylistItem).where(
            GroupPlaylistItem.group_id == group_id,
            GroupPlaylistItem.playlist_id == payload.playlist_id,
        )
    )
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Playlist already in group")
    db.add(
        GroupPlaylistItem(group_id=group_id, playlist_id=payload.playlist_id, item_order=group.next_item_order)
    )
    group.next_item_order += 1
    log_action(db, user.user_id, f"group.add_playlist:{group_id}:{payload.playlist_id}")
    db.commit()
    return _to_public(_owned(db, user, group_id))
