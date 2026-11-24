
from fastapi import APIRouter, HTTPException

from backend.schemas.evaluation import EvaluationRequest
from backend.services.evaluation_service import (
    EvaluationRecord,
    EvaluationService,
)

router = APIRouter()
evaluation_service = EvaluationService()


@router.post("/")
def evaluate_results(request: EvaluationRequest) -> dict:
    records = [
        EvaluationRecord(
            expected_diagnosis=case.expected_diagnosis,
            predicted_diagnosis=case.predicted_diagnosis,
            provider_successes=case.provider_successes,
            provider_count=case.provider_count,
            agreement_score=case.agreement_score,
        )
        for case in request.cases
    ]

    try:
        return evaluation_service.evaluate(records)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
