"""Shared FastAPI dependencies for authenticating requests.

The app started life single-user with every route open. Authentication is therefore
opt-in: with ``settings.auth_enabled`` False the dependency waves every request through
as a synthetic local user, so local development and the existing test suite keep working
untouched. Set ``AUTH_ENABLED=true`` together with ``SUPABASE_JWT_SECRET`` to enforce
Supabase-issued access tokens.
"""

import hmac
import logging
from functools import lru_cache
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.requests import Request

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def _jwks_client(supabase_url: str) -> jwt.PyJWKClient:
    """Cached JWKS client for a Supabase project's asymmetric signing keys."""
    return jwt.PyJWKClient(f"{supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json")

# auto_error=False: we decide the response ourselves (401, not the default 403) and we
# must be able to skip the check entirely when auth is disabled.
_bearer = HTTPBearer(auto_error=False, description="Supabase access token")
_BearerCreds = Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)]

# Returned when auth is disabled, so downstream code can always assume a user dict.
_LOCAL_USER = {"id": "local-dev", "email": None, "role": "owner"}


def _verify_supabase_jwt(token: str) -> dict:
    """Decode and validate a Supabase access token, returning a user dict.

    Supports both signing schemes: the legacy shared HS256 secret
    (``SUPABASE_JWT_SECRET``) and the newer asymmetric keys resolved from the
    project's JWKS endpoint (``SUPABASE_URL``).
    """
    settings = get_settings()
    try:
        alg = jwt.get_unverified_header(token).get("alg", "")
        if alg == "HS256":
            if not settings.supabase_jwt_secret:
                raise _misconfigured("SUPABASE_JWT_SECRET")
            key = settings.supabase_jwt_secret
        else:
            if not settings.supabase_url:
                raise _misconfigured("SUPABASE_URL")
            key = _jwks_client(settings.supabase_url).get_signing_key_from_jwt(token).key

        payload = jwt.decode(
            token,
            key,
            algorithms=["HS256", "ES256", "RS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as exc:
        logger.info("Rejected access token: %s", exc)
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return {
        "id": payload["sub"],
        "email": payload.get("email"),
        "role": payload.get("role", "authenticated"),
    }


def _misconfigured(missing: str) -> HTTPException:
    logger.error("AUTH_ENABLED is true but %s is not set", missing)
    return HTTPException(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "Authentication is misconfigured on the server",
    )


def get_current_user(request: Request, credentials: _BearerCreds) -> dict:
    """Resolve the caller.

    * auth disabled -> synthetic local user.
    * valid ``X-Service-Token`` header -> synthetic service user (used by the cron job).
    * otherwise -> a verified Supabase access token is required.
    """
    settings = get_settings()

    if not settings.auth_enabled:
        return _LOCAL_USER

    service_token = request.headers.get("x-service-token")
    if service_token and settings.service_token:
        if hmac.compare_digest(service_token, settings.service_token):
            return {"id": "service", "email": None, "role": "service"}
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid service token")

    if credentials is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not (settings.supabase_jwt_secret or settings.supabase_url):
        raise _misconfigured("SUPABASE_JWT_SECRET or SUPABASE_URL")

    return _verify_supabase_jwt(credentials.credentials)


# Use as: ``def endpoint(user: CurrentUser): ...`` when a route needs the caller's identity.
CurrentUser = Annotated[dict, Depends(get_current_user)]
