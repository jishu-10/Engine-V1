from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas import ValidationMetricsRead
from app.services.analytics_service import validation_metrics

router = APIRouter(prefix="/validation", tags=["validation"])


@router.get("/metrics", response_model=ValidationMetricsRead)
def read_validation_metrics(db: Session = Depends(get_db)) -> ValidationMetricsRead:
    return validation_metrics(db)

