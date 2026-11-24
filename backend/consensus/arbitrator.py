from backend.schemas.model_response import DiagnosisCandidate, ModelResponse


def arbitrate(responses: list[ModelResponse]) -> list[DiagnosisCandidate]:
    for response in responses:
        if response.diagnoses:
            return response.diagnoses[:3]
    return []
