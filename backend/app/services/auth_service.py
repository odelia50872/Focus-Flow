from collections import defaultdict
from datetime import datetime, timedelta, timezone
from threading import Lock

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.session import AuthSession
from app.models.user import User
from app.schemas.auth import PasswordChange, UserCreate, UserLogin, UserPublic
from app.services.ops_service import log_action
from app.utils.ids import as_id, iso_utc
from app.utils.security import create_access_token, hash_password, verify_password

settings = get_settings()

_login_lock = Lock()
_login_attempts: dict[str, list[datetime]] = defaultdict(list)
MAX_LOGIN_ATTEMPTS = 8
LOGIN_WINDOW_SECONDS = 10 * 60


def to_user_public(user: User) -> UserPublic:
    return UserPublic(
        id=as_id(user.user_id),
        email=user.email,
        display_name=user.display_name,
        created_at=iso_utc(user.creation_date) or "",
    )


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def _split_display_name(payload: UserCreate) -> tuple[str, str, str]:
    display = (payload.display_name or "").strip()
    first = (payload.first_name or "").strip()
    last = (payload.last_name or "").strip()
    if not display:
        display = " ".join(part for part in [first, last] if part).strip()
    if not display:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="display_name is required")
    if not first:
        parts = display.split(" ", 1)
        first = parts[0]
        last = parts[1] if len(parts) > 1 else ""
    return first, last, display


def validate_password_strength(password: str) -> None:
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters",
        )


def register_user(db: Session, payload: UserCreate) -> User:
    validate_password_strength(payload.password)
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    first, last, display = _split_display_name(payload)
    user = User(
        first_name=first,
        last_name=last,
        display_name=display,
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _check_lockout(email: str) -> None:
    now = datetime.now(timezone.utc)
    with _login_lock:
        recent = [t for t in _login_attempts[email] if now - t < timedelta(seconds=LOGIN_WINDOW_SECONDS)]
        _login_attempts[email] = recent
        if len(recent) >= MAX_LOGIN_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Too many login attempts. Try again in a few minutes",
            )


def _record_failure(email: str) -> None:
    with _login_lock:
        _login_attempts[email].append(datetime.now(timezone.utc))


def _clear_failures(email: str) -> None:
    with _login_lock:
        _login_attempts.pop(email, None)


def authenticate_user(db: Session, payload: UserLogin) -> User:
    email = payload.email.lower()
    _check_lockout(email)
    user = get_user_by_email(db, email)
    if user is None or not verify_password(payload.password, user.password_hash):
        _record_failure(email)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    _clear_failures(email)
    return user


def issue_token_for_user(db: Session, user: User) -> tuple[str, int]:
    token, jti, expires_at = create_access_token(subject=str(user.user_id))
    session = AuthSession(user_id=user.user_id, token_jti=jti, expires_at=expires_at)
    db.add(session)
    log_action(db, user.user_id, "auth.login")
    db.commit()
    expires_in = int(settings.access_token_expire_minutes * 60)
    return token, expires_in


def logout_user(db: Session, user: User, jti: str | None) -> None:
    if not jti:
        return
    session = db.scalar(select(AuthSession).where(AuthSession.user_id == user.user_id, AuthSession.token_jti == jti))
    if session:
        db.delete(session)
        log_action(db, user.user_id, "auth.logout")
        db.commit()


def is_session_valid(db: Session, *, user_id: int, jti: str) -> bool:
    session = db.scalar(select(AuthSession).where(AuthSession.user_id == user_id, AuthSession.token_jti == jti))
    if session is None:
        return False
    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at > datetime.now(timezone.utc)


def update_display_name(db: Session, user: User, display_name: str) -> User:
    name = display_name.strip()
    if not name:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="display_name is required")
    parts = name.split(" ", 1)
    user.display_name = name
    user.first_name = parts[0]
    user.last_name = parts[1] if len(parts) > 1 else ""
    log_action(db, user.user_id, "profile.update")
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, payload: PasswordChange) -> None:
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    validate_password_strength(payload.new_password)
    user.password_hash = hash_password(payload.new_password)
    db.execute(delete(AuthSession).where(AuthSession.user_id == user.user_id))
    log_action(db, user.user_id, "auth.password_change")
    db.commit()


def delete_account(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()
