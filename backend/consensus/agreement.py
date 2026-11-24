from collections import Counter

from backend.schemas.model_response import ModelResponse


def diagnosis_agreement(responses: list[ModelResponse]) -> Counter[str]:
    names = [
        diagnosis.name.strip().lower()
        for response in responses
        for diagnosis in response.diagnoses
        if diagnosis.name.strip()
    ]
    return Counter(names)
