
from types import SimpleNamespace

from backend.models.groq_provider import GroqProvider
from backend.schemas.common import ModelProvider, ProcessingStatus
from backend.schemas.patient import PatientCase


def make_patient_case() -> PatientCase:
    return PatientCase(
        age=35,
        gender="female",
        symptoms=["fever", "cough"],
        symptom_duration="3 days",
    )


class FakeGroqClient:
    def __init__(self, content=None, error=None):
        self.content = content
        self.error = error
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=self.create)
        )

    def create(self, **kwargs):
        if self.error:
            raise self.error

        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=self.content)
                )
            ]
        )


def test_groq_provider_success():
    client = FakeGroqClient(
        content=(
            '{"primary_diagnosis":"Pneumonia",'
            '"alternative_diagnoses":["Bronchitis"],'
            '"reported_confidence":0.8,'
            '"reasoning":"Synthetic test response.",'
            '"recommended_tests":["Chest X-ray"]}'
        )
    )
    provider = GroqProvider(
        api_key="test-key",
        model_name="test-model",
        client=client,
    )

    result = provider.analyze_case(make_patient_case())

    assert result.status == ProcessingStatus.SUCCESS
    assert result.provider == ModelProvider.GROQ
    assert result.primary_diagnosis == "Pneumonia"
    assert result.alternative_diagnoses == ["Bronchitis"]
    assert result.recommended_tests == ["Chest X-ray"]
    assert result.latency_ms is not None


def test_groq_provider_configures_bounded_request(monkeypatch):
    captured = {}

    def fake_groq(**kwargs):
        captured.update(kwargs)
        return FakeGroqClient(content="{}")

    monkeypatch.setattr("backend.models.groq_provider.Groq", fake_groq)

    GroqProvider(api_key="test-key", model_name="test-model")

    assert captured["timeout"] == 60.0
    assert captured["max_retries"] == 0


def test_groq_provider_request_failure():
    client = FakeGroqClient(error=RuntimeError("Simulated request failure"))
    provider = GroqProvider(
        api_key="test-key",
        model_name="test-model",
        client=client,
    )

    result = provider.analyze_case(make_patient_case())

    assert result.status == ProcessingStatus.FAILED
    assert result.provider == ModelProvider.GROQ
    assert "Simulated request failure" in result.error_message


def test_groq_provider_invalid_json():
    client = FakeGroqClient(content="not valid JSON")
    provider = GroqProvider(
        api_key="test-key",
        model_name="test-model",
        client=client,
    )

    result = provider.analyze_case(make_patient_case())

    assert result.status == ProcessingStatus.FAILED
    assert result.provider == ModelProvider.GROQ
    assert "Invalid Groq response" in result.error_message
