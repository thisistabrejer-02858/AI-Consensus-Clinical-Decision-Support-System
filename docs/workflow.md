# Workflow

1. User submits a patient case.
2. Backend validates the request with `PatientCase`.
3. Prompt builder creates provider-neutral diagnostic prompts.
4. Model runner executes configured providers.
5. Response normalizer maps provider output into `ModelResponse`.
6. Consensus engine compares diagnoses and supporting evidence.
7. Recommendation modules identify disagreements and missing information.
8. API returns a `ConsensusResponse`.
