
import logging
from time import perf_counter

from pydantic import ValidationError
from google import genai
from google.genai import errors, types

from backend.models.base import BaseModelProvider
from backend.models.google_response import GeminiDiagnosticResponse
from backend.orchestration.prompt_builder import build_diagnostic_prompt
from backend.schemas.common import ModelProvider, ProcessingStatus
from backend.schemas.model_response import ModelResponse
from backend.schemas.patient import PatientCase

logger = logging.getLogger(__name__)


class GoogleProvider(BaseModelProvider):
    """Gemini provider implementation."""

    def __init__(self, api_key: str, model_name: str, client=None):
        self.client = client if client is not None else genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=60_000,
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        )
        self.model_name = model_name

    def analyze_case(self, patient_case: PatientCase) -> ModelResponse:
        start_time = perf_counter()
        prompt = build_diagnostic_prompt(patient_case)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": GeminiDiagnosticResponse,
                    "max_output_tokens": 2048,
                },
            )

            response_text = response.text
            if not response_text:
                finish_reason = "unknown"
                try:
                    candidates = response.candidates or []
                    if candidates:
                        finish_reason = str(
                            candidates[0].finish_reason or "unknown"
                        )
                except (AttributeError, IndexError, TypeError):
                    pass

                raise ValueError(
                    "Gemini returned empty output. "
                    f"Finish reason: {finish_reason}"
                )

            try:
                diagnostic = GeminiDiagnosticResponse.model_validate_json(
                    response_text
                )
            except ValidationError as exc:
                finish_reason = "unknown"
                try:
                    candidates = response.candidates or []
                    if candidates:
                        finish_reason = str(
                            candidates[0].finish_reason or "unknown"
                        )
                except (AttributeError, IndexError, TypeError):
                    pass

                raise ValueError(
    "Invalid structured response: "
    f"Finish reason: {finish_reason}. Details: {exc}"
) from exc

            return ModelResponse(
                model_name=self.model_name,
                provider=ModelProvider.GOOGLE,
                status=ProcessingStatus.SUCCESS,
                primary_diagnosis=diagnostic.primary_diagnosis,
                alternative_diagnoses=diagnostic.alternative_diagnoses,
                reported_confidence=diagnostic.reported_confidence,
                reasoning=diagnostic.reasoning,
                recommended_tests=diagnostic.recommended_tests,
                latency_ms=(perf_counter() - start_time) * 1000,
            )

        except errors.APIError as exc:
            logger.warning("Gemini API request failed: %s", exc)
            if exc.code == 504 or exc.status == "DEADLINE_EXCEEDED":
                status = ProcessingStatus.TIMEOUT
                error_message = (
                    "Gemini exceeded the provider deadline (HTTP 504, "
                    "DEADLINE_EXCEEDED). Try again later or use another model."
                )
            elif exc.code in (401, 403):
                status = ProcessingStatus.FAILED
                error_message = (
                    f"Gemini rejected the request (HTTP {exc.code}). "
                    "Check the API key and its model access."
                )
            elif exc.code == 404:
                status = ProcessingStatus.FAILED
                error_message = (
                    "The configured Gemini model was not found (HTTP 404). "
                    "Check GEMINI_MODEL."
                )
            elif exc.code == 429:
                status = ProcessingStatus.FAILED
                error_message = (
                    "Gemini rate or quota limit reached (HTTP 429). "
                    "Check the provider quota and retry later."
                )
            else:
                status = ProcessingStatus.FAILED
                error_message = (
                    f"Gemini API request failed (HTTP {exc.code}, "
                    f"{exc.status or 'unknown status'})."
                )

        except (ValidationError, ValueError) as exc:
            logger.warning("Gemini response could not be validated: %s", exc)
            status = ProcessingStatus.FAILED
            error_message = str(exc)

        except Exception:
            logger.exception("Unexpected Gemini provider failure")
            status = ProcessingStatus.FAILED
            error_message = "Unexpected Gemini provider failure; see server logs."

        return ModelResponse(
            model_name=self.model_name,
            provider=ModelProvider.GOOGLE,
            status=status,
            latency_ms=(perf_counter() - start_time) * 1000,
            error_message=error_message,
        )
