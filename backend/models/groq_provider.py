
from time import perf_counter

from groq import Groq
from pydantic import ValidationError

from backend.models.base import BaseModelProvider
from backend.models.google_response import GeminiDiagnosticResponse
from backend.orchestration.prompt_builder import build_diagnostic_prompt
from backend.schemas.common import ModelProvider, ProcessingStatus
from backend.schemas.model_response import ModelResponse
from backend.schemas.patient import PatientCase


class GroqProvider(BaseModelProvider):
    """Groq provider implementation."""

    def __init__(self, api_key: str, model_name: str, client=None):
        self.client = (
            client
            if client is not None
            else Groq(api_key=api_key, timeout=60.0, max_retries=0)
        )
        self.model_name = model_name

    def analyze_case(self, patient_case: PatientCase) -> ModelResponse:
        start_time = perf_counter()
        prompt = build_diagnostic_prompt(patient_case)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are assisting a clinical decision-support "
                            "research prototype. Analyze synthetic cases "
                            "only. This is not a substitute for professional "
                            "medical diagnosis. Return valid JSON matching "
                            "the requested diagnostic structure."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content

            if not content:
                raise ValueError("Groq returned an empty response.")

            diagnostic = GeminiDiagnosticResponse.model_validate_json(
                content
            )

            return ModelResponse(
                model_name=self.model_name,
                provider=ModelProvider.GROQ,
                status=ProcessingStatus.SUCCESS,
                primary_diagnosis=diagnostic.primary_diagnosis,
                alternative_diagnoses=diagnostic.alternative_diagnoses,
                reported_confidence=diagnostic.reported_confidence,
                reasoning=diagnostic.reasoning,
                recommended_tests=diagnostic.recommended_tests,
                latency_ms=(perf_counter() - start_time) * 1000,
            )

        except (ValidationError, ValueError) as exc:
            return ModelResponse(
                model_name=self.model_name,
                provider=ModelProvider.GROQ,
                status=ProcessingStatus.FAILED,
                latency_ms=(perf_counter() - start_time) * 1000,
                error_message=f"Invalid Groq response: {exc}",
            )

        except Exception as exc:
            # Keep provider failures inside the normalized response.
            return ModelResponse(
                model_name=self.model_name,
                provider=ModelProvider.GROQ,
                status=ProcessingStatus.FAILED,
                latency_ms=(perf_counter() - start_time) * 1000,
                error_message=f"Groq request failed: {exc}",
            )
