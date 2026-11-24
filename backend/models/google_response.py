from pydantic import BaseModel, Field


class GeminiDiagnosticResponse(BaseModel):
    """Structured diagnostic information returned by Gemini."""

    primary_diagnosis: str = Field(
        description="The most likely primary diagnosis."
    )

    alternative_diagnoses: list[str] = Field(
        default_factory=list,
        description="Other plausible alternative diagnoses."
    )

    reported_confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="The model's self-reported confidence from 0 to 1."
    )

    reasoning: str = Field(
        description="Concise clinical reasoning supporting the assessment."
    )

    recommended_tests: list[str] = Field(
        default_factory=list,
        description="Additional diagnostic tests or information that may help."
    )