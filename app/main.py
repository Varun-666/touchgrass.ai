from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .ai_engine import generate_mission, model_status
from .schemas import MissionRequest

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="TouchGrass AI",
    description="A local-first open-source AI companion that turns screen time into outdoor time.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/health")
def health():
    return model_status()


@app.post("/api/mission")
def mission(request: MissionRequest):
    return generate_mission(request)
