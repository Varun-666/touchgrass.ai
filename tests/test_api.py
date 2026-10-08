from fastapi.testclient import TestClient

from app.main import app
from app.ai_engine import generate_mission
from app.schemas import MissionRequest

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["local"] is True


def test_mission_schema_without_loading_model():
    mission = generate_mission(MissionRequest(mode="nature", duration=20, energy="low", setting="park"))
    assert mission.duration_minutes == 20
    assert len(mission.steps) == 3
    assert len(mission.look_for) == 3


def test_invalid_duration():
    response = client.post("/api/mission", json={"duration": 5})
    assert response.status_code == 422
