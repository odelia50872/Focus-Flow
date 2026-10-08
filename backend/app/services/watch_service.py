from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.content import ContentItem
from app.models.ops import WatchTicket
from app.models.user import User
from app.models.watch import LogData, ModelResult, WatchData, WatchItem
from app.schemas.session import ReadingCreate, ReadingPublic, SessionDetail, SessionSummary
from app.services.ops_service import log_action
from app.utils.ids import as_id, iso_utc


def _parse_content_id(content_id: str) -> int:
    try:
        return int(content_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found") from None


def _reading_count(db: Session, watch_item_id: int) -> int:
    return int(
        db.scalar(
            select(func.count(ModelResult.model_result_id))
            .join(LogData)
            .join(WatchData)
            .where(WatchData.watch_item_id == watch_item_id)
        )
        or 0
    )


def to_summary(db: Session, item: WatchItem) -> SessionSummary:
    content = db.get(ContentItem, item.content_id)
    return SessionSummary(
        id=as_id(item.watch_item_id),
        content_id=as_id(item.content_id),
        content_title=content.title if content else None,
        started_at=iso_utc(item.started_at) or "",
        ended_at=iso_utc(item.ended_at),
        reading_count=_reading_count(db, item.watch_item_id),
        average_score=item.average_focus,
    )


def start_session(db: Session, user: User, content_id: str) -> WatchItem:
    item_id = _parse_content_id(content_id)
    content = db.get(ContentItem, item_id)
    if content is None or content.user_id != user.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    item = WatchItem(
        user_id=user.user_id,
        content_id=content.content_id,
        youtube_id=content.youtube_id,
        status="active",
        started_at=datetime.now(timezone.utc),
    )
    db.add(item)
    log_action(db, user.user_id, f"session.start:{content.content_id}")
    db.commit()
    db.refresh(item)
    return item


def get_owned_watch_item(db: Session, user: User, watch_item_id: int) -> WatchItem:
    item = db.get(WatchItem, watch_item_id)
    if item is None or item.user_id != user.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return item


def record_reading(db: Session, user: User, watch_item_id: int, payload: ReadingCreate) -> ReadingPublic:
    item = get_owned_watch_item(db, user, watch_item_id)
    if item.status != "active":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Session already ended")

    ticket = item.next_ticket
    sub_ticket = item.next_sub_ticket
    item.next_ticket += 1
    created_at = datetime.now(timezone.utc)

    watch_data = WatchData(
        watch_item_id=item.watch_item_id,
        vid_watch_time=payload.position,
        interval=1.0,
        ticket=ticket,
        sub_ticket=sub_ticket,
        log_date=created_at,
    )
    db.add(watch_data)
    if item.youtube_id:
        db.add(WatchTicket(youtube_id=item.youtube_id, ticket=ticket, sub_ticket=sub_ticket))
    db.flush()

    log_data = LogData(
        watch_data_id=watch_data.watch_data_id,
        fps_num=10,
        extraction_type=payload.extraction_type,
    )
    db.add(log_data)
    db.flush()

    db.add(ModelResult(log_data_id=log_data.log_data_id, model=payload.model_name, result=payload.score))
    db.flush()

    item.current_time = payload.position
    scores = list(
        db.scalars(
            select(ModelResult.result)
            .join(LogData)
            .join(WatchData)
            .where(WatchData.watch_item_id == item.watch_item_id)
        ).all()
    )
    item.average_focus = sum(scores) / len(scores) if scores else payload.score
    db.commit()
    return ReadingPublic(position=payload.position, score=payload.score, created_at=iso_utc(created_at) or "")


def end_session(db: Session, user: User, watch_item_id: int) -> WatchItem:
    item = get_owned_watch_item(db, user, watch_item_id)
    if item.status != "ended":
        item.status = "ended"
        item.ended_at = datetime.now(timezone.utc)
        log_action(db, user.user_id, f"session.end:{item.watch_item_id}")
        db.commit()
        db.refresh(item)
    return item


def list_sessions(db: Session, user: User) -> list[SessionSummary]:
    items = list(
        db.scalars(select(WatchItem).where(WatchItem.user_id == user.user_id).order_by(WatchItem.started_at.desc())).all()
    )
    return [to_summary(db, item) for item in items]


def get_session_detail(db: Session, user: User, watch_item_id: int) -> SessionDetail:
    item = get_owned_watch_item(db, user, watch_item_id)
    rows = db.execute(
        select(WatchData.vid_watch_time, ModelResult.result, WatchData.log_date)
        .join(LogData, LogData.watch_data_id == WatchData.watch_data_id)
        .join(ModelResult, ModelResult.log_data_id == LogData.log_data_id)
        .where(WatchData.watch_item_id == item.watch_item_id)
        .order_by(WatchData.log_date.asc())
    ).all()
    readings = [
        ReadingPublic(position=row[0], score=row[1], created_at=iso_utc(row[2]) or "")
        for row in rows
    ]
    summary = to_summary(db, item)
    return SessionDetail(**summary.model_dump(), readings=readings)
