from pydantic import BaseModel, ConfigDict, Field

# username: letters, digits and . _ - ; email: a loose sanity check (Supabase does the
# authoritative validation). Both request models forbid extra fields so the API accepts
# exactly the three documented inputs and nothing else.
_USERNAME_RE = r"^[A-Za-z0-9._-]+$"
_EMAIL_RE = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=3, max_length=32, pattern=_USERNAME_RE)
    email: str = Field(max_length=254, pattern=_EMAIL_RE)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(max_length=254, pattern=_EMAIL_RE)
    password: str = Field(min_length=1, max_length=128)


class SessionResponse(BaseModel):
    """Tokens for the browser to install as its Supabase session.

    ``access_token`` / ``refresh_token`` are absent only when the Supabase project still
    requires email confirmation — then ``confirmation_required`` is true and the client
    should tell the user to check their inbox.
    """

    access_token: str | None = None
    refresh_token: str | None = None
    expires_in: int | None = None
    token_type: str = "bearer"
    username: str | None = None
    email: str | None = None
    confirmation_required: bool = False
