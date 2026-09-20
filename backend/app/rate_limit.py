"""A minimal in-memory, per-IP rate limiter.

Deliberately not backed by Redis or similar: this app runs as a single
process in a single container (see Dockerfile / scripts), so an in-memory
window is sufficient and avoids adding infrastructure this "foundation"
stage doesn't otherwise need. It resets on every restart, same as the
database (see database.init_db).
"""

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status


def make_rate_limiter(max_requests: int, window_seconds: float):
    """Build a FastAPI dependency that allows at most `max_requests` calls per
    client IP in a rolling `window_seconds` window."""

    hits_by_client: dict[str, deque[float]] = defaultdict(deque)

    def enforce(request: Request) -> None:
        client_id = request.client.host if request.client else "unknown"
        now = time.monotonic()
        hits = hits_by_client[client_id]

        while hits and now - hits[0] > window_seconds:
            hits.popleft()

        if len(hits) >= max_requests:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "Too many requests. Please wait a moment and try again.",
            )

        hits.append(now)

    enforce.reset_for_tests = hits_by_client.clear  # type: ignore[attr-defined]
    return enforce
