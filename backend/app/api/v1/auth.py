from fastapi import APIRouter, status

from app.schemas.auth import LoginRequest, RegisterRequest, SessionResponse
from app.services import auth_service

# NB: mounted outside the authenticated /api/v1 router (see app.main) — these endpoints
# are how a caller *obtains* a session, so they must stay open.
router = APIRouter(prefix="/auth", tags=["auth"])


def _to_session(data: dict) -> SessionResponse:
    # /token nests the user under "user"; an unconfirmed /signup returns the user inline.
    user = data.get("user") if isinstance(data.get("user"), dict) else data
    metadata = user.get("user_metadata") or {} if isinstance(user, dict) else {}
    return SessionResponse(
        access_token=data.get("access_token"),
        refresh_token=data.get("refresh_token"),
        expires_in=data.get("expires_in"),
        username=metadata.get("username"),
        email=user.get("email") if isinstance(user, dict) else None,
        confirmation_required="access_token" not in data,
    )


@router.post(
    "/register",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest) -> SessionResponse:
    """Create an account from a username, email and password.

    Returns a ready-to-use session unless the Supabase project requires email
    confirmation, in which case ``confirmation_required`` is true and there are no tokens.
    """
    return _to_session(
        auth_service.register(payload.username, payload.email, payload.password)
    )


@router.post("/login", response_model=SessionResponse)
def login(payload: LoginRequest) -> SessionResponse:
    return _to_session(auth_service.login(payload.email, payload.password))
