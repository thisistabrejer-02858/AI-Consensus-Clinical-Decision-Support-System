import pytest
from pydantic import ValidationError

from backend.schemas.consensus import (
    ConsensusResult,
    DiagnosisCandidate,
)
from backend.schemas.patient import PatientCase
from backend.schemas.model_response import ModelResponse
from backend.schemas.common import ModelProvider, ProcessingStatus


def test_valid_patient_case():
    case = PatientCase(
        age=45,
        gender="male",
        symptoms=["fever", "cough"]
    )

    assert case.age == 45
    assert len(case.symptoms) == 2


def test_invalid_age():
    with pytest.raises(ValidationError):
        PatientCase(
            age=-10,
            gender="male",
            symptoms=["fever"]
        )


def test_empty_symptoms_are_rejected():
    with pytest.raises(ValidationError):
        PatientCase(
            age=45,
            gender="male",
            symptoms=[]
        )


def test_model_response_confidence_range():
    with pytest.raises(ValidationError):
        ModelResponse(
            model_name="test-model",
            provider=ModelProvider.OPENAI,
            status=ProcessingStatus.SUCCESS,
            reported_confidence=1.5
        )
        
def test_valid_consensus_result():
    result = ConsensusResult(
        primary_diagnosis="pneumonia",
        agreement_score=0.85,
        consensus_score=0.82,
    )

    assert result.primary_diagnosis == "pneumonia"
    assert result.agreement_score == 0.85
    assert result.consensus_score == 0.82


def test_diagnosis_candidate():
    candidate = DiagnosisCandidate(
        diagnosis="pneumonia",
        supporting_models=["model-a", "model-b"],
        support_count=2,
        weighted_support=0.75,
    )

    assert candidate.diagnosis == "pneumonia"
    assert candidate.support_count == 2


def test_invalid_consensus_score():
    with pytest.raises(ValidationError):
        ConsensusResult(
            primary_diagnosis="pneumonia",
            agreement_score=0.8,
            consensus_score=1.5,
        )
