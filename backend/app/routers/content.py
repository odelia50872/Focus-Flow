from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.content import ContentCreate, ContentPublic
from app.services import content_service

router = APIRouter(prefix="/content", tags=["content"])


@router.post("", response_model=ContentPublic, status_code=status.HTTP_201_CREATED)
def create_content(
    payload: ContentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ContentPublic:
    item = content_service.create_content(db, current_user, payload)
    return content_service.to_content_public(item)


@router.get("", response_model=list[ContentPublic])
def list_content(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ContentPublic]:
    return [content_service.to_content_public(item) for item in content_service.list_content(db, current_user)]


@router.get("/{content_id}", response_model=ContentPublic)
def get_content(
    content_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ContentPublic:
    try:
        numeric_id = int(content_id)
    except ValueError:
        from fastapi import HTTPException

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found") from None
    item = content_service.get_owned_content(db, current_user, numeric_id)
    return content_service.to_content_public(item)


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_content(
    content_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    try:
        numeric_id = int(content_id)
    except ValueError:
        from fastapi import HTTPException

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found") from None
    content_service.delete_content(db, current_user, numeric_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
