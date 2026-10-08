from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.learning import Question, QuestionGroup, Summary, Transcript
from app.models.user import User
from app.models.video import Video
from app.schemas.learning import QuestionGroupCreate, SummaryCreate, TranscriptCreate
from app.services.ops_service import log_action


def _video_or_404(db: Session, youtube_id: str) -> Video:
    video = db.scalar(select(Video).where(Video.youtube_id == youtube_id))
    if video is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    return video


def list_summaries(db: Session, youtube_id: str | None = None) -> list[Summary]:
    stmt = select(Summary)
    if youtube_id:
        stmt = stmt.where(Summary.youtube_id == youtube_id)
    return list(db.scalars(stmt.order_by(Summary.summary_id.desc())).all())


def upsert_summary(db: Session, user: User, payload: SummaryCreate) -> Summary:
    _video_or_404(db, payload.youtube_id)
    existing = db.scalar(
        select(Summary).where(Summary.youtube_id == payload.youtube_id, Summary.language == payload.language)
    )
    if existing:
        existing.summary = payload.summary
        summary = existing
    else:
        summary = Summary(youtube_id=payload.youtube_id, language=payload.language, summary=payload.summary)
        db.add(summary)
    log_action(db, user.user_id, f"summary.upsert:{payload.youtube_id}")
    db.commit()
    db.refresh(summary)
    return summary


def upsert_transcript(db: Session, user: User, payload: TranscriptCreate) -> Transcript:
    _video_or_404(db, payload.youtube_id)
    existing = db.scalar(
        select(Transcript).where(Transcript.youtube_id == payload.youtube_id, Transcript.language == payload.language)
    )
    if existing:
        existing.text = payload.text
        row = existing
    else:
        row = Transcript(youtube_id=payload.youtube_id, language=payload.language, text=payload.text)
        db.add(row)
    log_action(db, user.user_id, f"transcript.upsert:{payload.youtube_id}")
    db.commit()
    db.refresh(row)
    return row


def list_question_groups(db: Session, youtube_id: str | None = None) -> list[QuestionGroup]:
    stmt = select(QuestionGroup).options(joinedload(QuestionGroup.questions))
    if youtube_id:
        stmt = stmt.where(QuestionGroup.youtube_id == youtube_id)
    return list(db.scalars(stmt).unique().all())


def create_question_group(db: Session, user: User, payload: QuestionGroupCreate) -> QuestionGroup:
    _video_or_404(db, payload.youtube_id)
    group = QuestionGroup(youtube_id=payload.youtube_id, language=payload.language)
    db.add(group)
    db.flush()
    for q in payload.questions:
        db.add(
            Question(
                question_group_id=group.question_group_id,
                q_id=q.q_id,
                difficulty=q.difficulty,
                question=q.question,
                answer1=q.answer1,
                answer2=q.answer2,
                answer3=q.answer3,
                answer4=q.answer4,
                keywords=q.keywords,
                explanation_snippet=q.explanation_snippet,
                question_origin=q.question_origin,
                question_explanation_end=q.question_explanation_end,
            )
        )
    log_action(db, user.user_id, f"questions.create:{payload.youtube_id}")
    db.commit()
    return db.scalar(
        select(QuestionGroup)
        .options(joinedload(QuestionGroup.questions))
        .where(QuestionGroup.question_group_id == group.question_group_id)
    )
