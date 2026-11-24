
from fastapi import FastAPI

from pathlib import Path
from fastapi.responses import FileResponse
from backend.api.routes.diagnosis import router as diagnosis_router
from backend.api.routes.health import router as health_router
from backend.api.routes.evaluation import router as evaluation_router

app = FastAPI(
    title="Medical AI Consensus",
    description="Research API for multi-model clinical decision support.",
    version="0.1.0",
)


app.include_router(
    health_router,
    prefix="/health",
    tags=["health"],
)

app.include_router(
    diagnosis_router,
    prefix="/diagnosis",
    tags=["diagnosis"],
)

app.include_router(
    evaluation_router,
    prefix="/evaluation",
    tags=["evaluation"]
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_FILE = PROJECT_ROOT / "frontend" / "index.html"


@app.get("/", include_in_schema=False)
def frontend_home():
    return FileResponse(FRONTEND_FILE)
