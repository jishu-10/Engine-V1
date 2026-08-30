from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas import UserCreate, UserRead
from app.services.user_service import create_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=201)
def create_test_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    return create_user(db, payload.id)

