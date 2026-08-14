from __future__ import annotations

from uuid import UUID

import httpx
from fastapi import Header, HTTPException, status

from app.config import get_settings
from app.schemas import AuthUser

DEMO_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


async def get_current_user(
    authorization: str | None = Header(default=None),
    x_evidencepilot_demo: str | None = Header(default=None),
) -> AuthUser:
    """Validate a Supabase session or return the isolated local demo identity.

    Production requests are validated by Supabase Auth's user endpoint. The
    backend never trusts a user id supplied by the browser.
    """

    settings = get_settings()
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        if not settings.supabase_enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Supabase authentication is not configured.",
            )
        headers = {
            "apikey": settings.supabase_publishable_key,
            "Authorization": f"Bearer {token}",
        }
        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
                response = await client.get(
                    f"{settings.supabase_url}/auth/v1/user", headers=headers
                )
            response.raise_for_status()
            payload = response.json()
            return AuthUser(
                id=UUID(payload["id"]),
                email=payload.get("email"),
                access_token=token,
                is_demo=False,
            )
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired Supabase session.",
            ) from exc

    if settings.demo_mode and x_evidencepilot_demo == "1":
        return AuthUser(id=DEMO_USER_ID, email=None, is_demo=True)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sign in with Supabase or use the public demo.",
        headers={"WWW-Authenticate": "Bearer"},
    )
