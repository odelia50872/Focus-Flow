from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    content_id: str = Field(min_length=1)


class SessionSummary(BaseModel):
    id: str
    content_id: str
    content_title: str | None = None
    started_at: str
    ended_at: str | None = None
    reading_count: int
    average_score: float | None = None


class ReadingCreate(BaseModel):
    position: float = Field(ge=0)
    score: float = Field(ge=0, le=1)
    model_name: str = Field(default="v4_2", max_length=64)
    extraction_type: str = Field(default="face_landmarks", max_length=64)


class ReadingPublic(BaseModel):
    position: float
    score: float
    created_at: str


class SessionDetail(SessionSummary):
    readings: list[ReadingPublic]
