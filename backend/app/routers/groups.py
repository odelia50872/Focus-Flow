from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.group import GroupCreate, GroupPlaylistAdd, GroupPublic, GroupVideoAdd
from app.services import group_service

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("", response_model=list[GroupPublic])
def list_groups(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return group_service.list_groups(db, current_user)


@router.post("", response_model=GroupPublic, status_code=status.HTTP_201_CREATED)
def create_group(
    payload: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return group_service.create_group(db, current_user, payload)


@router.post("/{group_id}/videos", response_model=GroupPublic)
def add_group_video(
    group_id: int,
    payload: GroupVideoAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return group_service.add_video(db, current_user, group_id, payload)


@router.post("/{group_id}/playlists", response_model=GroupPublic)
def add_group_playlist(
    group_id: int,
    payload: GroupPlaylistAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return group_service.add_playlist(db, current_user, group_id, payload)
