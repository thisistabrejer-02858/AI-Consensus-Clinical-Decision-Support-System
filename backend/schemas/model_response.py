from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from .common import ModelProvider, ProcessingStatus


class ModelResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_name: str
    provider: ModelProvider

    status: ProcessingStatus

    primary_diagnosis: Optional[str] = None

    alternative_diagnoses: list[str] = Field(
        default_factory=list
    )

    reported_confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0
    )

    reasoning: Optional[str] = None

    recommended_tests: list[str] = Field(
        default_factory=list
    )

    latency_ms: Optional[float] = Field(
        default=None,
        ge=0
    )

    error_message: Optional[str] = None