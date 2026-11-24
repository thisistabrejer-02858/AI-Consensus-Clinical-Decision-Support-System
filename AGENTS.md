# Agent Guidelines

## Purpose

Agents in this project should support clinical reasoning research by producing structured, auditable, and safety-aware outputs.

## Ground Rules

- Do not present generated diagnoses as definitive medical advice.
- Preserve uncertainty and disagreement between models.
- Prefer structured outputs over free-form prose.
- Keep prompts and evaluation logic versioned.
- Redact patient-identifying information from test fixtures and logs.

## Expected Workflow

1. Build a case prompt from normalized patient data.
2. Query configured model providers.
3. Normalize model responses into shared schemas.
4. Compute agreement, confidence, and disagreement summaries.
5. Recommend missing information or next-step tests when warranted.
