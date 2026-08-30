"""Authentication behaviour for the /api/v1 routes.

``get_settings`` is cached, so tests that change auth env vars clear the cache on the
way in and out via the ``auth_enabled`` fixture.
"""

import datetime as dt

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app

_SECRET = "test-jwt-secret"
_SERVICE_TOKEN = "test-service-token"

# Any authenticated route works to probe the dependency; the request never reaches a
# database because auth runs first.
_PROTECTED = "/api/v1/stats"


def _client() -> TestClient:
    # A request that clears auth then hits the DB-less test config raises inside the
    # route; we only care about the auth outcome, so let the 500 come back as a response.
    return TestClient(app, raise_server_exceptions=False)


def _make_token(**overrides) -> str:
    now = dt.datetime.now(tz=dt.UTC)
    claims = {
        "sub": "11111111-1111-1111-1111-111111111111",
        "email": "owner@example.com",
        "aud": "authenticated",
        "role": "authenticated",
        "iat": now,
        "exp": now + dt.timedelta(hours=1),
    }
    claims.update(overrides)
    return jwt.encode(claims, _SECRET, algorithm="HS256")


@pytest.fixture
def auth_enabled(monkeypatch):
    monkeypatch.setenv("AUTH_ENABLED", "true")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", _SECRET)
    monkeypatch.setenv("SERVICE_TOKEN", _SERVICE_TOKEN)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_routes_open_when_auth_disabled():
    """Default config: no token needed, the request gets past auth."""
    assert _client().get(_PROTECTED).status_code != 401


def test_missing_token_is_rejected(auth_enabled):
    res = _client().get(_PROTECTED)
    assert res.status_code == 401
    assert res.headers["www-authenticate"] == "Bearer"


def test_garbage_token_is_rejected(auth_enabled):
    res = _client().get(_PROTECTED, headers={"Authorization": "Bearer not-a-jwt"})
    assert res.status_code == 401


def test_expired_token_is_rejected(auth_enabled):
    stale = _make_token(
        iat=dt.datetime.now(tz=dt.UTC) - dt.timedelta(hours=2),
        exp=dt.datetime.now(tz=dt.UTC) - dt.timedelta(hours=1),
    )
    res = _client().get(_PROTECTED, headers={"Authorization": f"Bearer {stale}"})
    assert res.status_code == 401


def test_token_signed_with_wrong_secret_is_rejected(auth_enabled):
    forged = jwt.encode(
        {"sub": "x", "aud": "authenticated"}, "attacker-secret", algorithm="HS256"
    )
    res = _client().get(_PROTECTED, headers={"Authorization": f"Bearer {forged}"})
    assert res.status_code == 401


def test_valid_token_passes_auth(auth_enabled):
    res = _client().get(
        _PROTECTED, headers={"Authorization": f"Bearer {_make_token()}"}
    )
    assert res.status_code != 401


def test_valid_service_token_passes_auth(auth_enabled):
    res = _client().get(_PROTECTED, headers={"X-Service-Token": _SERVICE_TOKEN})
    assert res.status_code != 401


def test_wrong_service_token_is_rejected(auth_enabled):
    res = _client().get(_PROTECTED, headers={"X-Service-Token": "nope"})
    assert res.status_code == 401


def test_asymmetric_es256_token_passes_auth(monkeypatch):
    """A token signed with an EC key is verified against the project's JWKS."""
    from cryptography.hazmat.primitives.asymmetric import ec

    private_key = ec.generate_private_key(ec.SECP256R1())

    monkeypatch.setenv("AUTH_ENABLED", "true")
    monkeypatch.setenv("SUPABASE_URL", "https://ref.supabase.co")
    get_settings.cache_clear()

    class _FakeJwksClient:
        def get_signing_key_from_jwt(self, _token):
            return type("_Key", (), {"key": private_key.public_key()})

    monkeypatch.setattr("app.api.deps._jwks_client", lambda _url: _FakeJwksClient())

    token = jwt.encode(
        {"sub": "u2", "aud": "authenticated", "role": "authenticated"},
        private_key,
        algorithm="ES256",
    )
    try:
        res = _client().get(_PROTECTED, headers={"Authorization": f"Bearer {token}"})
        assert res.status_code != 401
    finally:
        get_settings.cache_clear()
