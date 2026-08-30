"""POST /api/v1/auth/register and /login — request validation and GoTrue error mapping.

The Supabase call is stubbed via ``auth_service.httpx.post``; these tests never hit the
network.
"""

import httpx
import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.services import auth_service


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload
        self.request = httpx.Request("POST", "https://ref.supabase.co/auth/v1/x")

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300

    def json(self) -> dict:
        return self._payload


@pytest.fixture
def configured(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://ref.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "anon-key")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _stub(monkeypatch, response: _FakeResponse, capture: dict | None = None):
    def fake_post(url, **kwargs):
        if capture is not None:
            capture["url"] = url
            capture["json"] = kwargs.get("json")
            capture["params"] = kwargs.get("params")
        return response

    monkeypatch.setattr(auth_service.httpx, "post", fake_post)


_SESSION = {
    "access_token": "at",
    "refresh_token": "rt",
    "expires_in": 3600,
    "user": {"email": "neo@example.com", "user_metadata": {"username": "neo"}},
}


def test_register_returns_session_and_sends_username(configured, monkeypatch, client):
    seen: dict = {}
    _stub(monkeypatch, _FakeResponse(200, _SESSION), seen)

    res = client.post(
        "/api/v1/auth/register",
        json={"username": "neo", "email": "neo@example.com", "password": "trinity99"},
    )

    assert res.status_code == 201
    body = res.json()
    assert (body["access_token"], body["refresh_token"]) == ("at", "rt")
    assert body["username"] == "neo"
    assert body["confirmation_required"] is False
    assert seen["json"]["data"] == {"username": "neo"}
    assert seen["url"].endswith("/auth/v1/signup")


def test_register_confirmation_required(configured, monkeypatch, client):
    _stub(monkeypatch, _FakeResponse(200, {"email": "neo@example.com", "user_metadata": {}}))

    res = client.post(
        "/api/v1/auth/register",
        json={"username": "neo", "email": "neo@example.com", "password": "trinity99"},
    )

    assert res.status_code == 201
    body = res.json()
    assert body["access_token"] is None
    assert body["confirmation_required"] is True


def test_register_duplicate_email_is_409(configured, monkeypatch, client):
    _stub(monkeypatch, _FakeResponse(422, {"msg": "User already registered"}))

    res = client.post(
        "/api/v1/auth/register",
        json={"username": "neo", "email": "neo@example.com", "password": "trinity99"},
    )
    assert res.status_code == 409


@pytest.mark.parametrize(
    "payload",
    [
        {"username": "no", "email": "a@b.com", "password": "longenough"},  # username too short
        {"username": "ok", "email": "a@b.com", "password": "longenough", "x": 1},  # short + extra
        {"username": "valid", "email": "not-an-email", "password": "longenough"},
        {"username": "valid", "email": "a@b.com", "password": "short"},
        {"username": "valid", "email": "a@b.com", "password": "longenough", "full_name": "Neo"},
    ],
)
def test_register_rejects_bad_input(configured, monkeypatch, client, payload):
    _stub(monkeypatch, _FakeResponse(200, _SESSION))  # never reached
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 422


def test_login_returns_session(configured, monkeypatch, client):
    seen: dict = {}
    _stub(monkeypatch, _FakeResponse(200, _SESSION), seen)

    res = client.post(
        "/api/v1/auth/login",
        json={"email": "neo@example.com", "password": "trinity99"},
    )

    assert res.status_code == 200
    assert res.json()["access_token"] == "at"
    assert seen["params"] == {"grant_type": "password"}


def test_login_bad_credentials_is_401(configured, monkeypatch, client):
    _stub(
        monkeypatch,
        _FakeResponse(
            400,
            {"error": "invalid_grant", "error_description": "Invalid login credentials"},
        ),
    )
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "neo@example.com", "password": "wrong"},
    )
    assert res.status_code == 401


def test_auth_endpoints_500_when_not_configured(client):
    # No SUPABASE_URL / SUPABASE_ANON_KEY in the test env.
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "neo@example.com", "password": "trinity99"},
    )
    assert res.status_code == 500


def test_auth_endpoints_are_not_gated_by_bearer_auth(configured, monkeypatch, client):
    # Even with AUTH_ENABLED, register/login must not require a token.
    monkeypatch.setenv("AUTH_ENABLED", "true")
    get_settings.cache_clear()
    _stub(monkeypatch, _FakeResponse(200, _SESSION))
    try:
        res = client.post(
            "/api/v1/auth/login",
            json={"email": "neo@example.com", "password": "trinity99"},
        )
        assert res.status_code == 200
    finally:
        get_settings.cache_clear()
