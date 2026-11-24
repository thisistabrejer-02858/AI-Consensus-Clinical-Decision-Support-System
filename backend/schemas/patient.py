from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class PatientCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: Optional[str] = None

    age: int = Field(..., ge=0, le=120)

    gender: str

    symptoms: list[str] = Field(..., min_length=1)

    symptom_duration: Optional[str] = None

    medical_history: list[str] = Field(default_factory=list)

    current_medications: list[str] = Field(default_factory=list)

    allergies: list[str] = Field(default_factory=list)

    test_results: list[str] = Field(default_factory=list)