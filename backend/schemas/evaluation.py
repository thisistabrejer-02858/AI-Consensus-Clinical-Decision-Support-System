
from pydantic import BaseModel, ConfigDict, Field


class EvaluationCaseInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_diagnosis: str = Field(min_length=1)
    predicted_diagnosis: str | None = None
    provider_successes: int = Field(ge=0)
    provider_count: int = Field(ge=1)
    agreement_score: float = Field(ge=0.0, le=1.0)


class EvaluationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cases: list[EvaluationCaseInput] = Field(min_length=1)
