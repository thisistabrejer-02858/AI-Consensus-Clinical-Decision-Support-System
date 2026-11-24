
import re

from backend.recommendation.missing_information import (
    identify_missing_information,
)
from backend.schemas.common import ProcessingStatus
from backend.schemas.consensus import (
    ConsensusResult,
    DiagnosisCandidate,
    ModelRunSummary,
)
from backend.schemas.model_response import ModelResponse
from backend.schemas.patient import PatientCase


def _normalize_diagnosis(value: str) -> str:
    """Normalize formatting without merging medical synonyms."""
    return re.sub(
        r"\s+",
        " ",
        re.sub(r"[^\w\s]", " ", value.casefold()),
    ).strip()


def build_consensus(
    responses: list[ModelResponse],
    patient_case: PatientCase | None = None,
) -> ConsensusResult:
    successful = [
        response
        for response in responses
        if response.status == ProcessingStatus.SUCCESS
        and response.primary_diagnosis
        and response.primary_diagnosis.strip()
    ]

    missing = (
        identify_missing_information(patient_case)
        if patient_case is not None
        else []
    )

    if not successful:
        errors = [
            response.error_message
            for response in responses
            if response.error_message
        ]
        return ConsensusResult(
            primary_diagnosis=None,
            agreement_score=0.0,
            consensus_score=0.0,
            disagreement_detected=True,
            disagreement_summary="No provider returned a usable diagnosis.",
            recommended_tests=missing,
            model_runs=_model_run_summaries(responses),
            explanation="; ".join(errors) or "No successful model responses.",
        )

    groups: dict[str, list[ModelResponse]] = {}
    for response in successful:
        key = _normalize_diagnosis(response.primary_diagnosis)
        groups.setdefault(key, []).append(response)

    total = len(successful)
    ranked = sorted(
        groups.items(),
        key=lambda item: (
            len(item[1]),
            sum(r.reported_confidence or 0.0 for r in item[1]),
            item[0],
        ),
        reverse=True,
    )

    candidates = []
    for _, members in ranked:
        support = len(members)
        candidates.append(
            DiagnosisCandidate(
                diagnosis=members[0].primary_diagnosis.strip(),
                supporting_models=[r.model_name for r in members],
                support_count=support,
                weighted_support=support / total,
            )
        )

    top_support = len(ranked[0][1])
    tied_top = len(ranked) > 1 and len(ranked[1][1]) == top_support
    winning_members = ranked[0][1]
    disagreement = len(groups) > 1
    agreement_score = top_support / total

    recommended_tests = list(
        dict.fromkeys(
            test
            for response in successful
            for test in response.recommended_tests
        )
    )
    recommended_tests.extend(
        item for item in missing if item not in recommended_tests
    )

    if disagreement:
        disagreement_summary = (
            "Providers returned different primary diagnoses: "
            + "; ".join(candidate.diagnosis for candidate in candidates)
        )
        recommended_tests.append(
            "Review the conflicting assessments and gather case-specific "
            "information that may help distinguish the alternatives."
        )
    else:
        disagreement_summary = None

    failed_count = len(responses) - len(successful)

    if tied_top:
        primary_diagnosis = None
        explanation = (
            f"The leading diagnoses are tied, each supported by "
            f"{top_support} of {total} usable provider response(s). "
            "No unique consensus diagnosis was selected. "
            f"Usable diagnoses: {total}/{len(responses)} provider responses. "
            "Agreement measures model alignment, not clinical correctness."
        )
    else:
        primary_diagnosis = winning_members[0].primary_diagnosis.strip()
        explanation = (
            f"{top_support} of {total} usable provider response(s) "
            f"supported '{primary_diagnosis}'. "
            f"Usable diagnoses: {total}/{len(responses)} provider responses. "
            "Agreement measures model alignment, not clinical correctness."
        )

    if failed_count:
        explanation += (
            f" {failed_count} provider(s) failed or returned unusable output. "
            "Treat this consensus as incomplete."
        )

    return ConsensusResult(
        primary_diagnosis=primary_diagnosis,
        agreement_score=agreement_score,
        consensus_score=agreement_score,
        candidates=candidates,
        disagreement_detected=disagreement,
        disagreement_summary=disagreement_summary,
        recommended_tests=list(dict.fromkeys(recommended_tests)),
        model_runs=_model_run_summaries(responses),
        explanation=explanation,
    )


def _model_run_summaries(
    responses: list[ModelResponse],
) -> list[ModelRunSummary]:
    return [
        ModelRunSummary(
            model_name=response.model_name,
            provider=response.provider,
            status=response.status,
            diagnosis=(
                response.primary_diagnosis.strip()
                if response.status == ProcessingStatus.SUCCESS
                and response.primary_diagnosis
                and response.primary_diagnosis.strip()
                else None
            ),
            latency_ms=response.latency_ms,
            error_message=response.error_message,
        )
        for response in responses
    ]
