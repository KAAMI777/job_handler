from app.api.deps import get_current_user
from app.main import app
from tests.conftest import requires_db

pytestmark = requires_db


def test_global_path_when_auth_disabled(api_client):
    """With no real user (auth off) settings fall back to the global app_settings row."""
    initial = api_client.get("/api/v1/settings").json()
    assert initial["notify_min_score"] == 0  # env default
    assert initial["notify_email"] is None
    assert initial["notify_enabled"] is False

    patched = api_client.patch(
        "/api/v1/settings", json={"notify_min_score": 40, "notify_email": "me@example.com"}
    )
    assert patched.status_code == 200
    assert patched.json() == {
        "notify_min_score": 40,
        "notify_email": "me@example.com",
        "notify_enabled": True,
    }
    assert api_client.get("/api/v1/settings").json()["notify_min_score"] == 40


def test_patch_validates_score_range(api_client):
    assert api_client.patch("/api/v1/settings", json={"notify_min_score": 500}).status_code == 422


def test_per_user_settings_are_isolated(api_client):
    def act_as(uid: str, email: str) -> None:
        app.dependency_overrides[get_current_user] = lambda: {
            "id": uid,
            "email": email,
            "role": "authenticated",
        }

    act_as("u1", "u1@example.com")
    s1 = api_client.get("/api/v1/settings").json()
    assert s1["notify_email"] == "u1@example.com"  # address is the account email
    assert s1["notify_enabled"] is True  # digests on by default
    api_client.patch("/api/v1/settings", json={"notify_enabled": False, "notify_min_score": 70})

    act_as("u2", "u2@example.com")
    s2 = api_client.get("/api/v1/settings").json()
    assert s2["notify_email"] == "u2@example.com"
    assert s2["notify_enabled"] is True  # u2 unaffected by u1's change

    act_as("u1", "u1@example.com")
    s1b = api_client.get("/api/v1/settings").json()
    assert s1b["notify_enabled"] is False
    assert s1b["notify_min_score"] == 70
