from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.playlist import PlaylistPublic
from app.schemas.video import VideoPublic


class GroupCreate(BaseModel):
    group_name: str = Field(min_length=1, max_length=255)
    description: str = ""


class GroupVideoAdd(BaseModel):
    video_id: int


class GroupPlaylistAdd(BaseModel):
    playlist_id: int


class GroupVideoItemPublic(BaseModel):
    group_video_item_id: int
    group_id: int
    video_id: int
    added_at: datetime
    item_order: int
    video: VideoPublic | None = None

    model_config = {"from_attributes": True}


class GroupPlaylistItemPublic(BaseModel):
    group_playlist_item_id: int
    group_id: int
    playlist_id: int
    added_at: datetime
    item_order: int
    playlist: PlaylistPublic | None = None

    model_config = {"from_attributes": True}


class GroupPublic(BaseModel):
    group_id: int
    user_id: int
    group_name: str
    description: str
    created_at: datetime
    updated_at: datetime
    next_item_order: int
    video_items: list[GroupVideoItemPublic] = []
    playlist_items: list[GroupPlaylistItemPublic] = []

    model_config = {"from_attributes": True}
