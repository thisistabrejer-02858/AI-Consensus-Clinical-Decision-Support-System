
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_evaluation_endpoint_returns_metrics():
    response = client.post(
        "/evaluation/",
        json={
            "cases": [
                {
                    "expected_diagnosis": "Pneumonia",
                    "predicted_diagnosis": "Pneumonia",
                    "provider_successes": 2,
                    "provider_count": 2,
                    "agreement_score": 1.0,
                },
                {
                    "expected_diagnosis": "Bronchitis",
                    "predicted_diagnosis": "Asthma",
                    "provider_successes": 1,
                    "provider_count": 2,
                    "agreement_score": 0.5,
                },
            ]
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["total_cases"] == 2
    assert result["covered_cases"] == 2
    assert result["exact_match_count"] == 1
    assert result["exact_match_rate"] == 0.5


def test_evaluation_endpoint_rejects_empty_cases():
    response = client.post("/evaluation/", json={"cases": []})

    assert response.status_code == 422
