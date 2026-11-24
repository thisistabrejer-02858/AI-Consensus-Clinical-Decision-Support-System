
from fastapi import APIRouter, Depends

from backend.api.dependencies import get_diagnosis_service
from backend.schemas.consensus import ConsensusResult
from backend.schemas.patient import PatientCase
from backend.services.diagnosis_service import DiagnosisService


router = APIRouter()


@router.post("/", response_model=ConsensusResult)
def create_diagnosis(
    patient_case: PatientCase,
    service: DiagnosisService = Depends(get_diagnosis_service),
) -> ConsensusResult:
    return service.evaluate_case(patient_case)

