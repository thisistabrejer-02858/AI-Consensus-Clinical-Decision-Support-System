# Clinical Consensus frontend

React/Vite frontend for the existing AI Consensus-Based Clinical Decision Support System. All frontend code is isolated in this directory; the original `frontend/` remains available as a fallback.

## Run locally

1. Start the existing FastAPI backend from the project root:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   python -m uvicorn backend.main:app --reload
   ```

2. In a second terminal:

   ```powershell
   cd frontend-react
   npm install
   if (!(Test-Path .env)) { Copy-Item .env.example .env }
   npm run dev
   ```

   Open the local URL printed by Vite. The default API base URL is `http://127.0.0.1:8000`. Vite proxies local development API calls to the backend so development does not require changing backend CORS settings.

Set `VITE_API_BASE_URL` in `frontend-react/.env` to override the API base URL. A cross-origin deployed frontend requires the backend deployment to allow its origin; this frontend does not change backend CORS configuration.

## Pages and API

- Dashboard and new synthetic case analysis.
- Diagnosis results and candidate comparison.
- Browser-local analysis history.
- Evaluation metrics submitted to `POST /evaluation/` using the checked-in synthetic fixture copied from `data/synthetic_evaluation.json`.
- About, configuration, and research-scope information.

The app calls `GET /health/`, `POST /diagnosis/`, and `POST /evaluation/`. The diagnosis response does not contain individual provider responses, provider-failure metadata, or missing-information fields; the UI identifies these limitations rather than inventing values. Evaluation is aggregate-only.

History stores result summaries in this browser's local storage, up to 50 entries; it does not store case inputs or create backend patient records. Use synthetic data only.

## Checks

```powershell
npm run lint
npm run build
```
