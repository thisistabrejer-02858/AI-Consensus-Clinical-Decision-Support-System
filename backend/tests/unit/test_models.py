from backend.orchestration.prompt_builder import build_diagnostic_prompt
from backend.schemas.patient import PatientCase
from backend.models.google_provider import GoogleProvider
from backend.models.google_response import GeminiDiagnosticResponse
from backend.services.diagnosis_service import DiagnosisService
from backend.schemas.common import ModelProvider, ProcessingStatus
from backend.schemas.model_response import ModelResponse

from types import SimpleNamespace

from backend.models.google_provider import GoogleProvider
from backend.schemas.patient import PatientCase

class FakeGeminiClient:
    class Models:
        def generate_content(self, **kwargs):
            return SimpleNamespace(
                text="""
                {
                    "primary_diagnosis": "pneumonia",
                    "alternative_diagnoses": ["bronchitis"],
                    "reported_confidence": 0.88,
                    "reasoning": "Fever and cough may be consistent with pneumonia.",
                    "recommended_tests": ["chest X-ray"]
                }
                """
            )

    def __init__(self):
        self.models = self.Models()


def test_google_provider_analyze_case_without_api_call():
    provider = GoogleProvider(
        api_key="test-key",
        model_name="test-model",
        client=FakeGeminiClient(),
    )

    patient_case = PatientCase(
        age=45,
        gender="male",
        symptoms=["fever", "cough"],
    )

    result = provider.analyze_case(patient_case)

    assert result.primary_diagnosis == "pneumonia"
    assert result.alternative_diagnoses == ["bronchitis"]
    assert result.reported_confidence == 0.88
    assert result.recommended_tests == ["chest X-ray"]
    assert result.status.value == "success"
    
def test_google_provider_initialization():
    provider = GoogleProvider(
        api_key="test-key",
        model_name="test-model",
    )

    assert provider.model_name == "test-model"
    assert provider.client is not None


def test_google_provider_configures_bounded_request(monkeypatch):
    captured = {}

    def fake_client(**kwargs):
        captured.update(kwargs)
        return FakeGeminiClient()

    monkeypatch.setattr("backend.models.google_provider.genai.Client", fake_client)

    GoogleProvider(api_key="test-key", model_name="test-model")

    http_options = captured["http_options"]
    assert http_options.timeout == 60_000
    assert http_options.retry_options.attempts == 1
    
def test_diagnostic_prompt_contains_patient_information():
    patient_case = PatientCase(
        age=45,
        gender="male",
        symptoms=["fever", "cough"],
    )

    prompt = build_diagnostic_prompt(patient_case)

    assert "45" in prompt
    assert "male" in prompt
    assert "fever, cough" in prompt  
    
def test_gemini_diagnostic_response():
    response = GeminiDiagnosticResponse(
        primary_diagnosis="pneumonia",
        alternative_diagnoses=["bronchitis"],
        reported_confidence=0.88,
        reasoning="Fever and cough are consistent with pneumonia.",
        recommended_tests=["chest X-ray"],
    )

    assert response.primary_diagnosis == "pneumonia"
    assert response.reported_confidence == 0.88
    assert "bronchitis" in response.alternative_diagnoses
    
class FailingGeminiClient:
    class Models:
        def generate_content(self, **kwargs):
            from google.genai.errors import ServerError

            raise ServerError(
                503,
                {
                    "error": {
                        "code": 503,
                        "message": "Temporary test failure",
                        "status": "UNAVAILABLE",
                    }
                },
            )

    def __init__(self):
        self.models = self.Models()  
        
def test_google_provider_handles_api_failure():
    provider = GoogleProvider(
        api_key="test-key",
        model_name="test-model",
        client=FailingGeminiClient(),
    )

    patient_case = PatientCase(
        age=45,
        gender="male",
        symptoms=["fever", "cough"],
    )

    result = provider.analyze_case(patient_case)

    assert result.status.value == "failed"
    assert result.error_message is not None
    assert result.primary_diagnosis is None   


def test_google_provider_classifies_deadline_exceeded_as_timeout():
    class DeadlineExceededClient:
        class Models:
            def generate_content(self, **kwargs):
                from google.genai.errors import ServerError

                raise ServerError(
                    504,
                    {
                        "error": {
                            "code": 504,
                            "message": "Deadline expired before operation completed.",
                            "status": "DEADLINE_EXCEEDED",
                        }
                    },
                )

        def __init__(self):
            self.models = self.Models()

    provider = GoogleProvider(
        api_key="test-key",
        model_name="test-model",
        client=DeadlineExceededClient(),
    )

    result = provider.analyze_case(
        PatientCase(age=45, gender="unspecified", symptoms=["cough"])
    )

    assert result.status == ProcessingStatus.TIMEOUT
    assert "HTTP 504" in result.error_message
    assert "DEADLINE_EXCEEDED" in result.error_message
    
class MalformedGeminiClient:
    class Models:
        def generate_content(self, **kwargs):
            from types import SimpleNamespace

            return SimpleNamespace(text="This is not valid JSON")

    def __init__(self):
        self.models = self.Models()


def test_google_provider_handles_malformed_response():
    provider = GoogleProvider(
        api_key="test-key",
        model_name="test-model",
        client=MalformedGeminiClient(),
    )

    patient_case = PatientCase(
        age=45,
        gender="male",
        symptoms=["fever", "cough"],
    )

    result = provider.analyze_case(patient_case)

    assert result.status.value == "failed"
    assert result.primary_diagnosis is None
    assert "Invalid structured response" in result.error_message      
    
def test_diagnosis_service_uses_provider():
    class FakeProvider:
        def analyze_case(self, patient_case):
            return ModelResponse(
                model_name="fake-model",
                provider=ModelProvider.GOOGLE,
                status=ProcessingStatus.SUCCESS,
                primary_diagnosis="pneumonia",
                recommended_tests=["chest X-ray"],
            )

    service = DiagnosisService(provider=FakeProvider())

    patient_case = PatientCase(
        age=45,
        gender="male",
        symptoms=["fever", "cough"],
    )

    result = service.evaluate_case(patient_case)

    assert result.primary_diagnosis == "pneumonia"
    assert result.recommended_tests == ["chest X-ray"]
    assert result.consensus_score == 0.0    
    

def test_diagnosis_service_combines_multiple_fake_providers():
    from backend.models.base import BaseModelProvider
    from backend.schemas.common import ModelProvider, ProcessingStatus
    from backend.schemas.model_response import ModelResponse
    from backend.schemas.patient import PatientCase
    from backend.services.diagnosis_service import DiagnosisService

    class FakeProvider(BaseModelProvider):
        def __init__(self, name, provider, diagnosis):
            self.name = name
            self.provider = provider
            self.diagnosis = diagnosis

        def analyze_case(self, patient_case):
            return ModelResponse(
                model_name=self.name,
                provider=self.provider,
                status=ProcessingStatus.SUCCESS,
                primary_diagnosis=self.diagnosis,
                reported_confidence=0.8,
                recommended_tests=["Review relevant clinical findings"],
            )

    patient = PatientCase(
        age=30,
        gender="unspecified",
        symptoms=["cough", "fever"],
    )

    service = DiagnosisService(
        providers=[
            FakeProvider(
                "Fake Google", ModelProvider.GOOGLE,
                "Viral respiratory infection",
            ),
            FakeProvider(
                "Fake Groq", ModelProvider.GROQ,
                "Viral respiratory infection",
            ),
            FakeProvider(
                "Fake Third Model", ModelProvider.OPENAI,
                "Acute respiratory infection",
            ),
        ]
    )

    result = service.evaluate_case(patient)

    assert result.primary_diagnosis == "Viral respiratory infection"
    assert result.agreement_score == 2 / 3
    assert result.consensus_score == 2 / 3
    assert result.disagreement_detected is True
    assert len(result.candidates) >= 2


def test_diagnosis_service_runs_multiple_providers_concurrently():
    from threading import Barrier

    from backend.models.base import BaseModelProvider
    from backend.schemas.common import ModelProvider, ProcessingStatus
    from backend.schemas.model_response import ModelResponse
    from backend.schemas.patient import PatientCase
    from backend.services.diagnosis_service import DiagnosisService

    providers_started_together = Barrier(2)

    class SynchronizedProvider(BaseModelProvider):
        def __init__(self, provider, diagnosis):
            self.provider = provider
            self.diagnosis = diagnosis

        def analyze_case(self, patient_case):
            providers_started_together.wait(timeout=2)
            return ModelResponse(
                model_name=self.provider.value,
                provider=self.provider,
                status=ProcessingStatus.SUCCESS,
                primary_diagnosis=self.diagnosis,
                reported_confidence=0.8,
            )

    patient = PatientCase(
        age=30,
        gender="unspecified",
        symptoms=["cough", "fever"],
    )
    service = DiagnosisService(
        providers=[
            SynchronizedProvider(
                ModelProvider.GOOGLE, "Viral respiratory infection"
            ),
            SynchronizedProvider(
                ModelProvider.GROQ, "Viral respiratory infection"
            ),
        ]
    )

    result = service.evaluate_case(patient)

    assert result.primary_diagnosis == "Viral respiratory infection"
    assert result.agreement_score == 1.0
    assert len(result.model_runs) == 2


def test_diagnosis_service_continues_when_one_provider_fails():
    from backend.models.base import BaseModelProvider
    from backend.schemas.common import ModelProvider, ProcessingStatus
    from backend.schemas.model_response import ModelResponse
    from backend.schemas.patient import PatientCase
    from backend.services.diagnosis_service import DiagnosisService

    class WorkingProvider(BaseModelProvider):
        def analyze_case(self, patient_case):
            return ModelResponse(
                model_name="Working Fake Provider",
                provider=ModelProvider.GOOGLE,
                status=ProcessingStatus.SUCCESS,
                primary_diagnosis="Synthetic diagnosis A",
                reported_confidence=0.8,
            )

    class FailingProvider(BaseModelProvider):
        def analyze_case(self, patient_case):
            raise RuntimeError("Simulated provider failure")

    patient = PatientCase(
        age=30,
        gender="unspecified",
        symptoms=["cough"],
    )

    service = DiagnosisService(
        providers=[FailingProvider(), WorkingProvider()]
    )
    result = service.evaluate_case(patient)

    assert result.primary_diagnosis == "Synthetic diagnosis A"
    assert result.agreement_score == 1.0
