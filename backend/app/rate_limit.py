"""A minimal in-memory, per-IP rate limiter.

Deliberately not backed by Redis or similar: this app runs as a single
process in a single container (see Dockerfile / scripts), so an in-memory
window is sufficient and avoids adding infrastructure this "foundation"
stage doesn't otherwise need. It resets on every restart, same as the
database (see database.init_db).
"""

import time
from collections import deque

from fastapi import HTTPException, Request, status


def make_rate_limiter(max_requests: int, window_seconds: float, sweep_every: int = 1000):
    """Build a FastAPI dependency that allows at most `max_requests` calls per
    client IP in a rolling `window_seconds` window.

    A client's own entry is pruned/evicted the next time that same client is
    seen, but a one-off visitor who never returns would otherwise leave a
    stale entry behind forever. To bound memory regardless of how many
    distinct IPs ever pass through, every `sweep_every` calls a full pass
    removes every entry that's gone stale, so worst-case extra memory is a
    small, constant number of stale entries between sweeps - not unbounded
    growth over the process's lifetime.
    """

    hits_by_client: dict[str, deque[float]] = {}
    calls_since_sweep = 0

    def _prune(client_id: str, now: float) -> deque[float] | None:
        hits = hits_by_client.get(client_id)
        if hits is None:
            return None
        while hits and now - hits[0] > window_seconds:
            hits.popleft()
        if not hits:
            del hits_by_client[client_id]
            return None
        return hits

    def _sweep(now: float) -> None:
        stale = [
            client_id
            for client_id, hits in hits_by_client.items()
            if not hits or now - hits[-1] > window_seconds
        ]
        for client_id in stale:
            del hits_by_client[client_id]

    def enforce(request: Request) -> None:
        nonlocal calls_since_sweep
        client_id = request.client.host if request.client else "unknown"
        now = time.monotonic()

        hits = _prune(client_id, now)

        calls_since_sweep += 1
        if calls_since_sweep >= sweep_every:
            _sweep(now)
            calls_since_sweep = 0

        if hits is not None and len(hits) >= max_requests:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "Too many requests. Please wait a moment and try again.",
            )

        hits_by_client.setdefault(client_id, deque()).append(now)

    def _reset_for_tests() -> None:
        nonlocal calls_since_sweep
        hits_by_client.clear()
        calls_since_sweep = 0

    enforce.reset_for_tests = _reset_for_tests  # type: ignore[attr-defined]
    enforce.tracked_client_count_for_tests = lambda: len(hits_by_client)  # type: ignore[attr-defined]
    enforce.force_sweep_for_tests = lambda: _sweep(time.monotonic())  # type: ignore[attr-defined]
    return enforce
