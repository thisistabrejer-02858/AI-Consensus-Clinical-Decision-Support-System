
from backend.schemas.patient import PatientCase


def build_diagnostic_prompt(patient_case: PatientCase) -> str:
    """Build a compact prompt for clinical decision-support research."""

    symptoms = ", ".join(patient_case.symptoms)
    medical_history = ", ".join(patient_case.medical_history) or "Not provided"
    medications = ", ".join(patient_case.current_medications) or "Not provided"
    allergies = ", ".join(patient_case.allergies) or "Not provided"
    test_results = ", ".join(patient_case.test_results) or "Not provided"

    return f"""
You are supporting a clinical decision-support research prototype.
This is not a definitive diagnosis. Use only the supplied information.

CASE
Age: {patient_case.age}
Gender: {patient_case.gender}
Symptoms: {symptoms}
Duration: {patient_case.symptom_duration or "Not provided"}
Medical history: {medical_history}
Current medications: {medications}
Allergies: {allergies}
Test results: {test_results}

Return concise structured fields:
- primary_diagnosis: short diagnostic label
- alternative_diagnoses: at most 2 short labels
- reported_confidence: number from 0 to 1, reflecting uncertainty
- reasoning: at most 2 short sentences
- recommended_tests: at most 3 concise items

Do not repeat the case details. Do not invent missing information.
State uncertainty clearly and include urgent warning signs when relevant.
Return only the fields required by the supplied response schema.
""".strip()
