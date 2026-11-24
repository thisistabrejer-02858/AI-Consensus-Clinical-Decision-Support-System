# Architecture

The system is organized into five backend layers:

1. API routes receive requests and return structured responses.
2. Services coordinate use cases such as diagnosis and evaluation.
3. Orchestration builds prompts, executes providers, and normalizes responses.
4. Model providers isolate external model APIs behind a common interface.
5. Consensus modules compute agreement, weighting, confidence, and arbitration.

The frontend will call backend endpoints and render model-by-model reasoning, consensus output, uncertainty, and recommended follow-up information.
