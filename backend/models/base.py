from abc import ABC, abstractmethod

from backend.schemas.model_response import ModelResponse
from backend.schemas.patient import PatientCase


class BaseModelProvider(ABC):
    """Common interface for all LLM providers."""

    @abstractmethod
    def analyze_case(self, patient_case: PatientCase) -> ModelResponse:
        """Analyze a patient case and return a normalized model response."""
        raise NotImplementedError