from pydantic import BaseModel, Field


class ContentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    type: str = Field(min_length=1, max_length=32)
    source: str = Field(min_length=1)


class ContentPublic(BaseModel):
    id: str
    title: str
    type: str
    source: str
    created_at: str
