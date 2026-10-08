from datetime import time

from pydantic import BaseModel, Field


class SummaryCreate(BaseModel):
    youtube_id: str = Field(min_length=5, max_length=32)
    language: str = Field(default="en", max_length=16)
    summary: dict = Field(default_factory=dict)


class SummaryPublic(BaseModel):
    summary_id: int
    youtube_id: str
    language: str
    summary: dict

    model_config = {"from_attributes": True}


class QuestionCreate(BaseModel):
    q_id: str = Field(min_length=1, max_length=64)
    difficulty: int = Field(default=1, ge=1, le=5)
    question: str = Field(min_length=1)
    answer1: str = ""
    answer2: str = ""
    answer3: str = ""
    answer4: str = ""
    keywords: list[str] = Field(default_factory=list)
    explanation_snippet: str = ""
    question_origin: time | None = None
    question_explanation_end: time | None = None


class QuestionGroupCreate(BaseModel):
    youtube_id: str = Field(min_length=5, max_length=32)
    language: str = Field(default="en", max_length=16)
    questions: list[QuestionCreate] = Field(default_factory=list)


class QuestionPublic(BaseModel):
    question_id: int
    question_group_id: int
    q_id: str
    difficulty: int
    question: str
    answer1: str
    answer2: str
    answer3: str
    answer4: str
    keywords: list
    explanation_snippet: str

    model_config = {"from_attributes": True}


class QuestionGroupPublic(BaseModel):
    question_group_id: int
    youtube_id: str
    language: str
    questions: list[QuestionPublic] = []

    model_config = {"from_attributes": True}


class TranscriptCreate(BaseModel):
    youtube_id: str = Field(min_length=5, max_length=32)
    language: str = Field(default="en", max_length=16)
    text: str = ""


class TranscriptPublic(BaseModel):
    transcript_id: int
    youtube_id: str
    language: str
    text: str

    model_config = {"from_attributes": True}
