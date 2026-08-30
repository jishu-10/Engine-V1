from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas import ProfileCompletionRead, ProfileRead
from app.services.profile_service import get_profile, get_profile_completion

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileRead)
def read_profile(
    user_id: str = Query(min_length=1, max_length=64),
    db: Session = Depends(get_db),
) -> ProfileRead:
    return get_profile(db, user_id)


@router.get("/completion", response_model=ProfileCompletionRead)
def read_profile_completion(
    user_id: str = Query(min_length=1, max_length=64),
    db: Session = Depends(get_db),
) -> ProfileCompletionRead:
    return get_profile_completion(db, user_id)

