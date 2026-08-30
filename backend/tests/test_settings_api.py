from tests.conftest import requires_db

pytestmark = requires_db


def test_get_returns_env_defaults_then_patch_overrides(api_client):
    initial = api_client.get("/api/v1/settings").json()
    assert initial["notify_min_score"] == 0  # env default
    assert initial["notify_email"] is None

    patched = api_client.patch(
        "/api/v1/settings", json={"notify_min_score": 40, "notify_email": "me@example.com"}
    )
    assert patched.status_code == 200
    assert patched.json() == {"notify_min_score": 40, "notify_email": "me@example.com"}

    assert api_client.get("/api/v1/settings").json()["notify_min_score"] == 40


def test_patch_validates_score_range(api_client):
    assert api_client.patch("/api/v1/settings", json={"notify_min_score": 500}).status_code == 422
