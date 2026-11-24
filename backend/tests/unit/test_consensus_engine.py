
from backend.consensus.engine import build_consensus
from backend.schemas.common import ModelProvider, ProcessingStatus
from backend.schemas.model_response import ModelResponse


def make_response(
    model_name: str,
    diagnosis: str | None,
    *,
    status: ProcessingStatus = ProcessingStatus.SUCCESS,
    confidence: float = 0.8,
    tests: list[str] | None = None,
) -> ModelResponse:
    return ModelResponse(
        model_name=model_name,
        provider=(
            ModelProvider.GOOGLE
            if model_name == "gemini-test"
            else ModelProvider.GROQ
        ),
        status=status,
        primary_diagnosis=diagnosis,
        reported_confidence=confidence if diagnosis else None,
        recommended_tests=tests or [],
        error_message="Simulated provider failure"
        if status == ProcessingStatus.FAILED
        else None,
    )


def test_consensus_when_models_agree():
    result = build_consensus(
        [
            make_response("gemini-test", "Pneumonia"),
            make_response("groq-test", "Pneumonia"),
        ]
    )

    assert result.primary_diagnosis == "Pneumonia"
    assert result.agreement_score == 1.0
    assert result.consensus_score == 1.0
    assert result.disagreement_detected is False
    assert result.candidates[0].support_count == 2
    assert [run.model_name for run in result.model_runs] == [
        "gemini-test",
        "groq-test",
    ]
    assert [run.diagnosis for run in result.model_runs] == [
        "Pneumonia",
        "Pneumonia",
    ]


def test_consensus_detects_disagreement():
    result = build_consensus([
        make_response("gemini-test", "Pneumonia"),
        make_response("groq-test", "Bronchitis"),
    ])

    assert result.disagreement_detected is True
    assert result.disagreement_summary
    assert len(result.candidates) == 2
    assert result.agreement_score == 0.5


def test_consensus_handles_one_failed_provider():
    result = build_consensus([
        make_response("gemini-test", "Pneumonia"),
        make_response(
            "groq-test",
            None,
            status=ProcessingStatus.FAILED,
        ),
    ])

    assert result.primary_diagnosis == "Pneumonia"
    assert result.agreement_score == 1.0
    assert "1 provider(s) failed" in result.explanation
    failed_run = next(run for run in result.model_runs if run.status == ProcessingStatus.FAILED)
    assert failed_run.model_name == "groq-test"
    assert failed_run.diagnosis is None


def test_consensus_preserves_sanitized_provider_error():
    failed = make_response(
        "gemini-test",
        None,
        status=ProcessingStatus.TIMEOUT,
    ).model_copy(update={
        "error_message": "Gemini exceeded the provider deadline (HTTP 504)."
    })

    result = build_consensus([failed])

    assert result.model_runs[0].status == ProcessingStatus.TIMEOUT
    assert "HTTP 504" in result.model_runs[0].error_message


def test_consensus_handles_all_providers_failing():
    result = build_consensus([
        make_response(
            "gemini-test",
            None,
            status=ProcessingStatus.FAILED,
        ),
        make_response(
            "groq-test",
            None,
            status=ProcessingStatus.FAILED,
        ),
    ])

    assert result.primary_diagnosis is None
    assert result.agreement_score == 0.0
    assert result.consensus_score == 0.0
    assert result.disagreement_detected is True
    assert "No provider returned a usable diagnosis" in (
        result.disagreement_summary
    )
