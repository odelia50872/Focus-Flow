from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import DisplayNameUpdate, PasswordChange, UserPublic
from app.services import auth_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)) -> UserPublic:
    return auth_service.to_user_public(current_user)


@router.patch("/me", response_model=UserPublic)
def update_me(
    payload: DisplayNameUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserPublic:
    user = auth_service.update_display_name(db, current_user, payload.display_name)
    return auth_service.to_user_public(user)


@router.post("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    auth_service.change_password(db, current_user, payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    auth_service.delete_account(db, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
