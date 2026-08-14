from __future__ import annotations

from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta
from threading import Lock

from fastapi import HTTPException, Request, status


class SlidingWindowLimiter:
    """Small single-instance limiter for demo protection.

    Render can run one free instance for the public demo. A production scale-out
    deployment should replace this with a shared Redis or database limiter.
    """

    def __init__(self) -> None:
        self._events: dict[str, deque[datetime]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, limit: int, window: timedelta) -> None:
        if limit <= 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Live demo disabled."
            )
        now = datetime.now(UTC)
        cutoff = now - window
        with self._lock:
            events = self._events[key]
            while events and events[0] < cutoff:
                events.popleft()
            if len(events) >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Public demo quota reached. The cached research workspace remains available.",
                )
            events.append(now)


limiter = SlidingWindowLimiter()


def client_key(request: Request, namespace: str) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    ip = forwarded.split(",", 1)[0].strip() or (
        request.client.host if request.client else "unknown"
    )
    return f"{namespace}:{ip}"
