from backend.models.base import ModelProvider
from backend.schemas.model_response import ModelResponse
from backend.schemas.patient import PatientCase


class AnthropicProvider(ModelProvider):
    name = "anthropic"

    def diagnose(self, patient_case: PatientCase, prompt: str) -> ModelResponse:
        return ModelResponse(provider=self.name, uncertainty="Provider call not implemented.")
