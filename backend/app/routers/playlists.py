from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.playlist import PlaylistCreate, PlaylistItemCreate, PlaylistPublic
from app.services import playlist_service

router = APIRouter(prefix="/playlists", tags=["playlists"])


@router.get("", response_model=list[PlaylistPublic])
def list_playlists(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return playlist_service.list_playlists(db, current_user)


@router.post("", response_model=PlaylistPublic, status_code=status.HTTP_201_CREATED)
def create_playlist(
    payload: PlaylistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return playlist_service.create_playlist(db, current_user, payload)


@router.post("/{playlist_id}/items", response_model=PlaylistPublic)
def add_playlist_item(
    playlist_id: int,
    payload: PlaylistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return playlist_service.add_item(db, current_user, playlist_id, payload)


@router.delete("/{playlist_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_playlist_item(
    playlist_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    playlist_service.remove_item(db, current_user, playlist_id, item_id)
