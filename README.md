# AI Consensus-Based Clinical Decision Support System

A research-oriented clinical decision-support prototype that compares multiple AI model responses for a synthetic patient case, measures agreement, identifies disagreement, and produces a consensus-oriented summary.

## 1. Project Scope

This project is a B.Tech minor project and a research prototype. It is not a medical device and must not be used as a substitute for professional clinical judgment. Outputs are not clinically validated diagnoses.

Use synthetic cases for development and evaluation.

## 2. Architecture

- `backend/` — FastAPI API, model provider adapters, orchestration, consensus engine, schemas, and services.
- `frontend/` — HTML, CSS, and JavaScript interface.
- `prompts/` — Prompt templates and diagnostic instructions.
- `evaluation/` — Evaluation datasets, runners, metrics, and results.
- `scripts/` — Synthetic benchmark and provider-testing scripts.
- `tests/` — Automated unit, integration, and connection tests.
- `docs/` — Requirements, architecture, workflow, methodology, safety scope, and decision records.
- `.env.example` — Environment-variable template.
- `requirements.txt` — Python dependencies.

## 3. Requirements

- Python 3.11 or a compatible version supported by the dependencies.
- API credentials for the providers you want to test live.
- Internet access for live provider requests.

## 4. Installation

Run these commands from the project root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a local `.env` file from `.env.example` and configure the required variables. Never commit `.env` or expose API keys.

## 5. Configuration

Set `DIAGNOSIS_MODE` in `.env` according to the intended task:

- `mock` — deterministic mock responses for offline development and testing.
- `gemini` — Gemini provider mode.
- `groq` — Groq provider mode.
- `multi` — multi-provider diagnosis using Gemini and Groq.

For live multi-provider testing, configure valid provider credentials and model names. The application may return a partial result if a provider fails.

## 6. Run the Application

Activate the virtual environment and start FastAPI:

```powershell
python -m uvicorn backend.main:app --reload
```

Open the API documentation:

`http://127.0.0.1:8000/docs`

Open the frontend:

`http://127.0.0.1:8000/`

Use fictional synthetic cases during development. Restart the server after changing configuration values when necessary.

## 7. Run Tests

Run the offline test suite without the standalone Gemini connection tests:

```powershell
python -m pytest --ignore=tests/test_gemini_connection.py --ignore=scripts/test_gemini_real.py -v
```

Run the synthetic benchmark:

```powershell
python -m scripts.run_synthetic_benchmark
```

Run the standalone Gemini test when live API validation is needed:

```powershell
python scripts/test_gemini_real.py
```

Live tests require valid credentials, network access, and provider availability. They may fail because of rate limits or temporary service errors.

## 8. Evaluation and Limitations

The deterministic synthetic benchmark previously produced 12/12 exact matches against its expected mock labels, with 100% coverage and 100% mock-provider success. These results validate consistency with the mock rules only; they do not demonstrate real-model accuracy or clinical effectiveness.

Live integration testing has demonstrated successful responses from both providers, but Gemini has also intermittently returned `503 UNAVAILABLE` due to high demand.

Agreement measures model alignment, not clinical correctness. Different diagnosis wording may also affect exact-match and agreement calculations. Provider failures, tied diagnoses, and incomplete consensus must be interpreted cautiously.

## 9. Safety and Responsible Use

- Do not enter identifiable patient information.
- Treat all outputs as research artifacts, not medical advice.
- A successful HTTP response does not guarantee that every provider succeeded.
- A high agreement score does not establish that a diagnosis is correct.
- Clinical use would require appropriate validation, oversight, privacy safeguards, and risk assessment.
