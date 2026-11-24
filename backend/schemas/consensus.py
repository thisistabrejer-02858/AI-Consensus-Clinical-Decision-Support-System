from typing import Optional

from pydantic import BaseModel, Field, ConfigDict
from backend.schemas.common import ModelProvider, ProcessingStatus


class ModelRunSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_name: str
    provider: ModelProvider
    status: ProcessingStatus
    diagnosis: Optional[str] = None
    latency_ms: Optional[float] = Field(default=None, ge=0)
    error_message: Optional[str] = None


class DiagnosisCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    diagnosis: str

    supporting_models: list[str] = Field(
        default_factory=list
    )

    support_count: int = Field(
        default=0,
        ge=0
    )

    weighted_support: float = Field(
        default=0.0,
        ge=0.0
    )


class ConsensusResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    primary_diagnosis: Optional[str] = None

    agreement_score: float = Field(
        ge=0.0,
        le=1.0
    )

    consensus_score: float = Field(
        ge=0.0,
        le=1.0
    )

    candidates: list[DiagnosisCandidate] = Field(
        default_factory=list
    )

    disagreement_detected: bool = False

    disagreement_summary: Optional[str] = None

    recommended_tests: list[str] = Field(
        default_factory=list
    )

    model_runs: list[ModelRunSummary] = Field(default_factory=list)

    explanation: Optional[str] = None