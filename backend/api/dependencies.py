
import os

from dotenv import load_dotenv

from backend.models.google_provider import GoogleProvider
from backend.models.groq_provider import GroqProvider
from backend.services.diagnosis_service import DiagnosisService

load_dotenv()


def _required_setting(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is required for the selected mode.")
    return value


def get_diagnosis_service() -> DiagnosisService:
    mode = os.getenv("DIAGNOSIS_MODE", "mock").strip().lower()

    if mode == "mock":
        return DiagnosisService()

    if mode == "gemini":
        provider = GoogleProvider(
            api_key=_required_setting("GEMINI_API_KEY"),
            model_name=_required_setting("GEMINI_MODEL"),
        )
        return DiagnosisService(provider=provider)

    if mode == "groq":
        provider = GroqProvider(
            api_key=_required_setting("GROQ_API_KEY"),
            model_name=_required_setting("GROQ_MODEL"),
        )
        return DiagnosisService(provider=provider)

    if mode == "multi":
        gemini = GoogleProvider(
            api_key=_required_setting("GEMINI_API_KEY"),
            model_name=_required_setting("GEMINI_MODEL"),
        )
        groq = GroqProvider(
            api_key=_required_setting("GROQ_API_KEY"),
            model_name=_required_setting("GROQ_MODEL"),
        )
        return DiagnosisService(providers=[gemini, groq])

    raise ValueError(
        f"Unsupported DIAGNOSIS_MODE: {mode!r}. "
        "Choose mock, gemini, groq, or multi."
    )
