from pydantic import BaseModel, Field

from app.schemas.video import VideoPublic


class PlaylistCreate(BaseModel):
    playlist_name: str = Field(min_length=1, max_length=255)
    permission: str = Field(default="private", max_length=32)


class PlaylistItemCreate(BaseModel):
    video_id: int


class PlaylistItemPublic(BaseModel):
    playlist_item_id: int
    video_id: int
    playlist_id: int
    item_order: int
    video: VideoPublic | None = None

    model_config = {"from_attributes": True}


class PlaylistPublic(BaseModel):
    playlist_id: int
    user_id: int
    playlist_name: str
    permission: str
    next_item_order: int
    items: list[PlaylistItemPublic] = []

    model_config = {"from_attributes": True}
