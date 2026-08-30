from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas import (
    ExplanationRead,
    ExplanationRequest,
    SimilarityCompareRequest,
    SimilarityResultRead,
)
from app.services.llm_service import generate_explanation_for_result
from app.services.similarity_service import compare_users, get_similarity_result

router = APIRouter(prefix="/similarity", tags=["similarity"])


@router.post("/compare", response_model=SimilarityResultRead, status_code=201)
def compare(payload: SimilarityCompareRequest, db: Session = Depends(get_db)) -> SimilarityResultRead:
    return compare_users(db, payload.user_a_id, payload.user_b_id)


@router.get("/{result_id}", response_model=SimilarityResultRead)
def read_similarity_result(result_id: str, db: Session = Depends(get_db)) -> SimilarityResultRead:
    return get_similarity_result(db, result_id)


@router.post("/{result_id}/explanation", response_model=ExplanationRead, status_code=201)
def explain_similarity_result(
    result_id: str,
    payload: ExplanationRequest | None = None,
    db: Session = Depends(get_db),
) -> ExplanationRead:
    return generate_explanation_for_result(
        db,
        result_id,
        use_llm=payload.use_llm if payload else False,
    )

