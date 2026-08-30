from sqlalchemy.exc import OperationalError

from app.api import health


def test_health_ok(client):
    """With a reachable database, /health returns 200 and a connected status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_health_degraded_when_db_unreachable(client, monkeypatch):
    """When the database raises, /health returns 503 with a stable JSON shape."""

    def boom(*args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("no connection"))

    monkeypatch.setattr(health.engine, "connect", boom)

    response = client.get("/health")
    assert response.status_code == 503
    assert response.json() == {"status": "degraded", "database": "disconnected"}
