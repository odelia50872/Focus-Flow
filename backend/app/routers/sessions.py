from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.session import ReadingCreate, ReadingPublic, SessionCreate, SessionDetail, SessionSummary
from app.services import watch_service

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _parse_id(session_id: str) -> int:
    try:
        return int(session_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found") from None


@router.post("", response_model=SessionSummary, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SessionSummary:
    item = watch_service.start_session(db, current_user, payload.content_id)
    return watch_service.to_summary(db, item)


@router.get("", response_model=list[SessionSummary])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SessionSummary]:
    return watch_service.list_sessions(db, current_user)


@router.get("/{session_id}", response_model=SessionDetail)
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SessionDetail:
    return watch_service.get_session_detail(db, current_user, _parse_id(session_id))


@router.post("/{session_id}/readings", response_model=ReadingPublic, status_code=status.HTTP_201_CREATED)
def add_reading(
    session_id: str,
    payload: ReadingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReadingPublic:
    return watch_service.record_reading(db, current_user, _parse_id(session_id), payload)


@router.post("/{session_id}/end", response_model=SessionSummary)
def end_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SessionSummary:
    item = watch_service.end_session(db, current_user, _parse_id(session_id))
    return watch_service.to_summary(db, item)
