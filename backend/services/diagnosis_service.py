import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)
from backend.consensus.engine import build_consensus
from backend.models.base import BaseModelProvider
from backend.schemas.common import ProcessingStatus
from backend.schemas.consensus import ConsensusResult
from backend.schemas.patient import PatientCase


class DiagnosisService:
    def __init__(
        self,
        provider: BaseModelProvider | None = None,
        providers: list[BaseModelProvider] | None = None,
    ):
        if provider is not None and providers is not None:
            raise ValueError("Provide either provider or providers, not both.")

        self.providers = providers if providers is not None else (
            [provider] if provider is not None else []
        )

    def evaluate_case(self, patient_case: PatientCase) -> ConsensusResult:
        # Offline mock mode: no external API calls.
        if not self.providers:
            return self._build_mock_result(patient_case)

        with ThreadPoolExecutor(max_workers=len(self.providers)) as executor:
            responses = list(
                executor.map(
                    lambda provider: self._analyze_provider(
                        provider, patient_case
                    ),
                    self.providers,
                )
            )

        # A single model cannot establish cross-model consensus.
        if len(self.providers) == 1:
            response = responses[0]

            if response.status != ProcessingStatus.SUCCESS:
                return ConsensusResult(
                    primary_diagnosis=None,
                    agreement_score=0.0,
                    consensus_score=0.0,
                    disagreement_detected=True,
                    disagreement_summary=(
                        "The configured model provider failed to return "
                        "a valid response."
                    ),
                    explanation=(
                        response.error_message or "Model provider failed."
                    ),
                )

            return ConsensusResult(
                primary_diagnosis=response.primary_diagnosis,
                agreement_score=0.0,
                consensus_score=0.0,
                explanation=(
                    "Single-model result. Cross-model consensus has not "
                    "been calculated."
                ),
                recommended_tests=response.recommended_tests,
            )

        # Multiple configured providers: calculate consensus.
        return build_consensus(responses, patient_case)

    def _analyze_provider(self, provider, patient_case):
        try:
            return provider.analyze_case(patient_case)
        except Exception as exc:
            logger.exception(
                "Provider %s failed during analyze_case",
                type(provider).__name__,
            )

            from backend.schemas.common import ModelProvider
            from backend.schemas.model_response import ModelResponse

            provider_name = self._provider_identity(provider)
            return ModelResponse(
                model_name=type(provider).__name__,
                provider=provider_name,
                status=ProcessingStatus.FAILED,
                error_message=f"Provider execution failed: {exc}",
            )

    def _build_mock_result(
        self, patient_case: PatientCase
    ) -> ConsensusResult:
        """Create deterministic synthetic responses for offline testing."""
        from backend.schemas.common import ModelProvider
        from backend.schemas.model_response import ModelResponse

        symptoms = " ".join(patient_case.symptoms).casefold()

        if "cough" in symptoms and "fever" in symptoms:
            diagnoses = [
                (
                    "Synthetic Model A",
                    "Viral respiratory infection",
                    0.82,
                ),
                (
                    "Synthetic Model B",
                    "Viral respiratory infection",
                    0.78,
                ),
                (
                    "Synthetic Model C",
                    "Acute respiratory infection",
                    0.70,
                ),
            ]
            tests = [
                "Review temperature and oxygen saturation",
                "Consider appropriate respiratory testing",
            ]

        elif "headache" in symptoms:
            diagnoses = [
                (
                    "Synthetic Model A",
                    "Headache requiring further assessment",
                    0.72,
                ),
                (
                    "Synthetic Model B",
                    "Headache requiring further assessment",
                    0.75,
                ),
                (
                    "Synthetic Model C",
                    "Migraine-like headache",
                    0.64,
                ),
            ]
            tests = [
                "Clarify headache onset and severity",
                "Review associated neurological symptoms",
            ]

        else:
            diagnoses = [
                (
                    "Synthetic Model A",
                    "Undetermined — more information needed",
                    0.45,
                ),
                (
                    "Synthetic Model B",
                    "Undetermined — more information needed",
                    0.50,
                ),
                (
                    "Synthetic Model C",
                    "Further assessment required",
                    0.40,
                ),
            ]
            tests = [
                "Clarify symptom duration and severity",
                "Review relevant examination findings",
            ]

        responses = []

        for index, (name, diagnosis, confidence) in enumerate(diagnoses):
            provider = (
                ModelProvider.GROQ
                if index == 1
                else ModelProvider.GOOGLE
            )

            responses.append(
                ModelResponse(
                    model_name=name,
                    provider=provider,
                    status=ProcessingStatus.SUCCESS,
                    primary_diagnosis=diagnosis,
                    reported_confidence=confidence,
                    reasoning=(
                        "Illustrative synthetic response for offline "
                        "software testing; not a clinical assessment."
                    ),
                    recommended_tests=tests,
                )
            )

        return build_consensus(responses, patient_case)

    @staticmethod
    def _provider_identity(provider: BaseModelProvider):
        from backend.schemas.common import ModelProvider

        name = type(provider).__name__.lower()

        if "google" in name:
            return ModelProvider.GOOGLE
        if "groq" in name:
            return ModelProvider.GROQ
        if "anthropic" in name:
            return ModelProvider.ANTHROPIC

        return ModelProvider.OPENAI
