
from backend.schemas.patient import PatientCase


def identify_missing_information(
    patient_case: PatientCase,
) -> list[str]:
    """Identify useful case details that were not provided."""

    missing = []

    if not patient_case.symptom_duration:
        missing.append("Clarify symptom onset and duration.")

    if not patient_case.medical_history:
        missing.append("Obtain relevant past medical and surgical history.")

    if not patient_case.current_medications:
        missing.append("Confirm current medications and doses.")

    if not patient_case.allergies:
        missing.append("Confirm known allergies and previous reactions.")

    if not patient_case.test_results:
        missing.append("Review available examination findings and test results.")

    if not patient_case.gender:
        missing.append("Clarify relevant demographic information.")

    return missing
