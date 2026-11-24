from backend.schemas.model_response import ModelResponse


def estimate_confidence(responses: list[ModelResponse]) -> float:
    if not responses:
        return 0.0

    non_empty = sum(1 for response in responses if response.diagnoses)
    return round(non_empty / len(responses), 2)
