from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.learning import (
    QuestionGroupCreate,
    QuestionGroupPublic,
    SummaryCreate,
    SummaryPublic,
    TranscriptCreate,
    TranscriptPublic,
)
from app.services import learning_service

router = APIRouter(prefix="/learning", tags=["learning"])


@router.get("/summaries", response_model=list[SummaryPublic])
def list_summaries(
    youtube_id: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return [SummaryPublic.model_validate(s) for s in learning_service.list_summaries(db, youtube_id)]


@router.post("/summaries", response_model=SummaryPublic, status_code=status.HTTP_201_CREATED)
def upsert_summary(
    payload: SummaryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SummaryPublic.model_validate(learning_service.upsert_summary(db, current_user, payload))


@router.post("/transcripts", response_model=TranscriptPublic, status_code=status.HTTP_201_CREATED)
def upsert_transcript(
    payload: TranscriptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TranscriptPublic.model_validate(learning_service.upsert_transcript(db, current_user, payload))


@router.get("/questions", response_model=list[QuestionGroupPublic])
def list_questions(
    youtube_id: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return [QuestionGroupPublic.model_validate(g) for g in learning_service.list_question_groups(db, youtube_id)]


@router.post("/questions", response_model=QuestionGroupPublic, status_code=status.HTTP_201_CREATED)
def create_questions(
    payload: QuestionGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return QuestionGroupPublic.model_validate(learning_service.create_question_group(db, current_user, payload))
