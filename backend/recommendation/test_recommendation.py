from backend.schemas.model_response import ModelResponse


def collect_recommended_tests(responses: list[ModelResponse]) -> list[str]:
    tests = {
        test.strip()
        for response in responses
        for test in response.recommended_tests
        if test.strip()
    }
    return sorted(tests)
