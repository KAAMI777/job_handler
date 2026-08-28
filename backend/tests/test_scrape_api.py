from app.services import scrape_service
from tests.conftest import requires_db

pytestmark = requires_db


def test_start_run_returns_202_and_schedules_task(api_client, monkeypatch):
    calls: list[int] = []
    monkeypatch.setattr(scrape_service, "execute_run", calls.append)

    response = api_client.post("/api/v1/scrape/run", json={"run_type": "scheduled"})
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "running"

    run_id = body["run_id"]
    assert calls == [run_id]

    poll = api_client.get(f"/api/v1/scrape/run/{run_id}")
    assert poll.status_code == 200
    assert poll.json()["run_type"] == "scheduled"


def test_second_run_while_one_is_active_is_409(api_client, monkeypatch):
    monkeypatch.setattr(scrape_service, "execute_run", lambda run_id: None)

    first = api_client.post("/api/v1/scrape/run", json={})
    assert first.status_code == 202

    second = api_client.post("/api/v1/scrape/run", json={})
    assert second.status_code == 409
    assert second.json()["detail"]["run_id"] == first.json()["run_id"]


def test_unknown_run_is_404(api_client):
    assert api_client.get("/api/v1/scrape/run/424242").status_code == 404
