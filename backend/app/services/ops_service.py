from sqlalchemy.orm import Session

from app.models.ops import ActivityLog


def log_action(db: Session, user_id: int, action: str) -> None:
    db.add(ActivityLog(user_id=user_id, action=action))
