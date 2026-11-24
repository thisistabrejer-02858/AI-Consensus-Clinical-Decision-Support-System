
import pytest

from backend.services.evaluation_service import (
    EvaluationRecord,
    EvaluationService,
)


def test_evaluation_calculates_metrics():
    service = EvaluationService()

    result = service.evaluate([
        EvaluationRecord("Pneumonia", "pneumonia", 2, 2, 1.0),
        EvaluationRecord("Bronchitis", "Asthma", 1, 2, 0.5),
        EvaluationRecord("Influenza", None, 0, 2, 0.0),
    ])

    assert result["total_cases"] == 3
    assert result["covered_cases"] == 2
    assert result["coverage_rate"] == pytest.approx(2 / 3)
    assert result["exact_match_count"] == 1
    assert result["exact_match_rate"] == pytest.approx(0.5)
    assert result["provider_success_rate"] == pytest.approx(0.5)
    assert result["mean_agreement_score"] == pytest.approx(0.5)


def test_evaluation_rejects_empty_records():
    with pytest.raises(ValueError):
        EvaluationService().evaluate([])


def test_evaluation_handles_zero_coverage():
    result = EvaluationService().evaluate([
        EvaluationRecord("Pneumonia", None, 0, 2, 0.0),
    ])

    assert result["coverage_rate"] == 0.0
    assert result["exact_match_rate"] == 0.0


def test_evaluation_rejects_invalid_provider_counts():
    with pytest.raises(ValueError):
        EvaluationService().evaluate([
            EvaluationRecord("Pneumonia", "Pneumonia", 3, 2, 1.0),
        ])


def test_evaluation_rejects_empty_records():
    import pytest
    from backend.services.evaluation_service import EvaluationService

    with pytest.raises(ValueError):
        EvaluationService().evaluate([])


def test_evaluation_handles_no_successful_predictions():
    from backend.services.evaluation_service import (
        EvaluationRecord,
        EvaluationService,
    )

    record = EvaluationRecord(
        expected_diagnosis="Synthetic diagnosis A",
        predicted_diagnosis=None,
        provider_successes=0,
        provider_count=2,
        agreement_score=0.0,
    )

    result = EvaluationService().evaluate([record])

    assert result["total_cases"] == 1
    assert result["covered_cases"] == 0
    assert result["coverage_rate"] == 0.0
    assert result["exact_match_rate"] == 0.0
