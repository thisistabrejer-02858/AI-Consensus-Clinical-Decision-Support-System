
from backend.schemas.patient import PatientCase
from backend.services.diagnosis_service import DiagnosisService
from backend.services.evaluation_service import EvaluationRecord, EvaluationService


# These expected labels match the deterministic mock service.
# This is a software benchmark, not a clinically validated dataset.
BENCHMARK_CASES = [
    {
        "case_id": "SYN-001",
        "symptoms": ["cough", "fever"],
        "expected": "Viral respiratory infection",
    },
    {
        "case_id": "SYN-002",
        "symptoms": ["fever", "cough", "sore throat"],
        "expected": "Viral respiratory infection",
    },
    {
        "case_id": "SYN-003",
        "symptoms": ["cough", "fever", "fatigue"],
        "expected": "Viral respiratory infection",
    },
    {
        "case_id": "SYN-004",
        "symptoms": ["headache"],
        "expected": "Headache requiring further assessment",
    },
    {
        "case_id": "SYN-005",
        "symptoms": ["headache", "nausea"],
        "expected": "Headache requiring further assessment",
    },
    {
        "case_id": "SYN-006",
        "symptoms": ["headache", "fatigue"],
        "expected": "Headache requiring further assessment",
    },
    {
        "case_id": "SYN-007",
        "symptoms": ["fatigue"],
        "expected": "Undetermined — more information needed",
    },
    {
        "case_id": "SYN-008",
        "symptoms": ["joint pain"],
        "expected": "Undetermined — more information needed",
    },
    {
        "case_id": "SYN-009",
        "symptoms": ["dizziness"],
        "expected": "Undetermined — more information needed",
    },
    {
        "case_id": "SYN-010",
        "symptoms": ["loss of appetite"],
        "expected": "Undetermined — more information needed",
    },
    {
        "case_id": "SYN-011",
        "symptoms": ["cough", "fever", "body aches"],
        "expected": "Viral respiratory infection",
    },
    {
        "case_id": "SYN-012",
        "symptoms": ["headache", "light sensitivity"],
        "expected": "Headache requiring further assessment",
    },
]


def main():
    # No external providers or API calls.
    diagnosis_service = DiagnosisService()
    evaluation_service = EvaluationService()
    records = []
    case_matches = 0

    print("\nSYNTHETIC BENCHMARK RESULTS")
    print("=" * 72)

    for case in BENCHMARK_CASES:
        patient = PatientCase(
            case_id=case["case_id"],
            age=35,
            gender="unspecified",
            symptoms=case["symptoms"],
            symptom_duration="3 days",
        )

        result = diagnosis_service.evaluate_case(patient)

        # Candidate support counts represent usable responses that
        # contributed to the consensus.
        successful_count = sum(
            candidate.support_count for candidate in result.candidates
        )

        matched = (
            result.primary_diagnosis is not None
            and result.primary_diagnosis.strip().casefold()
            == case["expected"].strip().casefold()
        )
        case_matches += int(matched)

        records.append(
            EvaluationRecord(
                expected_diagnosis=case["expected"],
                predicted_diagnosis=result.primary_diagnosis,
                provider_successes=successful_count,
                provider_count=3,
                agreement_score=result.agreement_score,
            )
        )

        print(f"\n{case['case_id']}: {', '.join(case['symptoms'])}")
        print(f"Expected:   {case['expected']}")
        print(f"Predicted:  {result.primary_diagnosis}")
        print(f"Exact match: {'PASS' if matched else 'FAIL'}")
        print(f"Agreement:  {result.agreement_score:.2%}")
        print(f"Usable providers: {successful_count}/3")
        print(f"Disagreement: {'Yes' if result.disagreement_detected else 'No'}")

    metrics = evaluation_service.evaluate(records)

    print("\n" + "=" * 72)
    print("AGGREGATE METRICS")
    print("=" * 72)

    for name, value in metrics.items():
        print(f"{name}: {value}")

    print(f"case_level_exact_matches: {case_matches}/{len(BENCHMARK_CASES)}")
    print("\nLIMITATIONS")
    print("- Cases use deterministic mock responses.")
    print("- Expected labels are aligned to mock-service rules.")
    print("- Results do not measure real model or clinical accuracy.")
    print("- Provider failures and disagreement require separate scenario tests.")


if __name__ == "__main__":
    main()
