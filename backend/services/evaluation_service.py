
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationRecord:
    """One synthetic case evaluated against a reference label."""

    expected_diagnosis: str
    predicted_diagnosis: str | None
    provider_successes: int
    provider_count: int
    agreement_score: float


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().casefold())


class EvaluationService:
    """Calculate reproducible metrics for synthetic evaluation cases."""

    def evaluate(self, records: list[EvaluationRecord]) -> dict:
        if not records:
            raise ValueError("At least one evaluation record is required.")

        for record in records:
            if not record.expected_diagnosis.strip():
                raise ValueError("Expected diagnosis cannot be empty.")
            if record.provider_count < 1:
                raise ValueError("Provider count must be at least one.")
            if not 0 <= record.provider_successes <= record.provider_count:
                raise ValueError(
                    "Provider successes must be between zero and provider count."
                )
            if not 0.0 <= record.agreement_score <= 1.0:
                raise ValueError("Agreement score must be between 0 and 1.")

        total = len(records)
        covered = [
            record for record in records
            if record.predicted_diagnosis
            and record.predicted_diagnosis.strip()
        ]

        correct = sum(
            _normalize(record.predicted_diagnosis)
            == _normalize(record.expected_diagnosis)
            for record in covered
        )

        provider_count = sum(record.provider_count for record in records)
        provider_successes = sum(
            record.provider_successes for record in records
        )

        return {
            "total_cases": total,
            "covered_cases": len(covered),
            "coverage_rate": len(covered) / total,
            "exact_match_count": correct,
            "exact_match_rate": correct / len(covered) if covered else 0.0,
            "provider_success_rate": provider_successes / provider_count,
            "mean_agreement_score": (
                sum(record.agreement_score for record in records) / total
            ),
            "evaluation_note": (
                "Exact-match and agreement metrics are research measures, "
                "not proof of clinical correctness. Exact matching does not "
                "account for clinically equivalent diagnosis terminology."
            ),
        }
