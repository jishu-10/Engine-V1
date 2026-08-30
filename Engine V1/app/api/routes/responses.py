from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas import ResponseCreate, ResponseRead
from app.services.response_service import get_responses, submit_response

router = APIRouter(prefix="/responses", tags=["responses"])


@router.post("", response_model=ResponseRead, status_code=201)
def create_response(payload: ResponseCreate, db: Session = Depends(get_db)) -> ResponseRead:
    return submit_response(db, payload)


@router.get("", response_model=list[ResponseRead])
def list_responses(
    user_id: str = Query(min_length=1, max_length=64),
    db: Session = Depends(get_db),
) -> list[ResponseRead]:
    return get_responses(db, user_id)
