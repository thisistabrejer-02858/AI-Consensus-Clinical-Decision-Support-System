from backend.models.base import ModelProvider
from backend.schemas.model_response import ModelResponse
from backend.schemas.patient import PatientCase


def run_models(
    providers: list[ModelProvider],
    patient_case: PatientCase,
    prompt: str,
) -> list[ModelResponse]:
    return [provider.diagnose(patient_case, prompt) for provider in providers]
