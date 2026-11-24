import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import os

from dotenv import load_dotenv

from backend.models.google_provider import GoogleProvider
from backend.schemas.patient import PatientCase


load_dotenv()


def main() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing from .env")

    if not model_name:
        raise RuntimeError("GEMINI_MODEL is missing from .env")

    provider = GoogleProvider(
        api_key=api_key,
        model_name=model_name,
    )

    # Synthetic case for project testing only.
    patient_case = PatientCase(
        age=45,
        gender="male",
        symptoms=["fever", "cough", "shortness of breath"],
        symptom_duration="3 days",
        medical_history=[],
        current_medications=[],
        allergies=[],
        test_results=[],
    )

    result = provider.analyze_case(patient_case)

    print("\n--- Gemini Diagnostic Result ---")
    print(f"Model: {result.model_name}")
    print(f"Provider: {result.provider.value}")
    print(f"Status: {result.status.value}")
    print(f"Error: {result.error_message}")
    print(f"Primary diagnosis: {result.primary_diagnosis}")
    print(f"Alternative diagnoses: {result.alternative_diagnoses}")
    print(f"Reported confidence: {result.reported_confidence}")
    print(f"Reasoning: {result.reasoning}")
    print(f"Recommended tests: {result.recommended_tests}")
    print(f"Latency: {result.latency_ms:.2f} ms")


if __name__ == "__main__":
    main()