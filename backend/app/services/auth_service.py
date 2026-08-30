"""Thin wrapper over the Supabase GoTrue REST API for register / login.

The frontend could call Supabase directly, but routing these two calls through the API
keeps one auth surface and lets us attach the chosen username to the new user's metadata
server-side. Token *verification* still happens in ``app.api.deps``.
"""

import logging

import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(10.0)


def _endpoint(path: str) -> tuple[str, dict[str, str]]:
    settings = get_settings()
    if not (settings.supabase_url and settings.supabase_anon_key):
        logger.error("Auth endpoint hit but SUPABASE_URL / SUPABASE_ANON_KEY are not set")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Authentication is not configured on the server",
        )
    base = settings.supabase_url.rstrip("/")
    headers = {
        "apikey": settings.supabase_anon_key,
        "Authorization": f"Bearer {settings.supabase_anon_key}",
        "Content-Type": "application/json",
    }
    return f"{base}/auth/v1/{path}", headers


def register(username: str, email: str, password: str) -> dict:
    """Create a Supabase user with ``username`` in its metadata."""
    url, headers = _endpoint("signup")
    resp = _send(
        url,
        headers=headers,
        json={"email": email, "password": password, "data": {"username": username}},
    )
    return _unwrap(resp)


def login(email: str, password: str) -> dict:
    url, headers = _endpoint("token")
    resp = _send(
        url,
        headers=headers,
        params={"grant_type": "password"},
        json={"email": email, "password": password},
    )
    return _unwrap(resp)


def _send(url: str, **kwargs) -> httpx.Response:
    try:
        return httpx.post(url, timeout=_TIMEOUT, **kwargs)
    except httpx.HTTPError as exc:
        logger.warning("Supabase auth request failed: %s", exc)
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY, "Could not reach the authentication service"
        ) from exc


def _unwrap(resp: httpx.Response) -> dict:
    if resp.is_success:
        return resp.json()

    try:
        body = resp.json()
    except ValueError:
        body = {}
    message = (
        body.get("msg")
        or body.get("error_description")
        or body.get("error")
        or body.get("message")
        or "Authentication failed"
    )
    logger.info("GoTrue %s -> %s: %s", resp.request.url.path, resp.status_code, message)

    code = {
        400: status.HTTP_400_BAD_REQUEST,
        401: status.HTTP_401_UNAUTHORIZED,
        403: status.HTTP_403_FORBIDDEN,
        409: status.HTTP_409_CONFLICT,
        422: 422,
        429: status.HTTP_429_TOO_MANY_REQUESTS,
    }.get(resp.status_code, status.HTTP_502_BAD_GATEWAY)

    lowered = message.lower()
    if body.get("error") == "invalid_grant" or "invalid login credentials" in lowered:
        code, message = status.HTTP_401_UNAUTHORIZED, "Invalid email or password"
    elif "already registered" in lowered or "already been registered" in lowered:
        code, message = status.HTTP_409_CONFLICT, "That email is already registered"

    raise HTTPException(code, message)
