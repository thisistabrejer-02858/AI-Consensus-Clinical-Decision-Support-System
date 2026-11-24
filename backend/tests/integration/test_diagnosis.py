
from fastapi.testclient import TestClient

from backend.api.dependencies import get_diagnosis_service
from backend.main import app
from backend.services.diagnosis_service import DiagnosisService

client = TestClient(app)


def test_create_diagnosis(monkeypatch):
    monkeypatch.setitem(
        app.dependency_overrides,
        get_diagnosis_service,
        lambda: DiagnosisService(),
    )

    response = client.post(
        "/diagnosis/",
        json={
            "age": 45,
            "gender": "male",
            "symptoms": ["fever", "cough"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    # Mock mode returns a deterministic synthetic consensus result.
    assert data["primary_diagnosis"] == "Viral respiratory infection"
    assert data["agreement_score"] == 2 / 3
    assert data["consensus_score"] == 2 / 3
    assert len(data["candidates"]) >= 2
    assert len(data["model_runs"]) == 3
    assert all(run["status"] == "success" for run in data["model_runs"])
    assert data["disagreement_detected"] is True
    assert len(data["recommended_tests"]) > 0
