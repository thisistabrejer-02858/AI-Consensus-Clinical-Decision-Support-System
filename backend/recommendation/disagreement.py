from backend.schemas.model_response import ModelResponse


def summarize_disagreements(responses: list[ModelResponse]) -> list[str]:
    diagnosis_sets = [
        {diagnosis.name.strip().lower() for diagnosis in response.diagnoses}
        for response in responses
    ]
    if len(diagnosis_sets) <= 1 or all(item == diagnosis_sets[0] for item in diagnosis_sets):
        return []
    return ["Models differ on the leading diagnosis candidates."]
