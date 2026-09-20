"""ASGI-level request guards that run before FastAPI/Pydantic body parsing.

Per-field caps like `Field(max_length=...)` only apply after Starlette has
already read and JSON-decoded the whole request body into Python objects -
an oversized raw body still costs memory/CPU to parse before validation ever
rejects it. This middleware rejects based on the declared Content-Length
before that parsing happens.

Doesn't defend against a client that omits Content-Length and streams an
unbounded chunked-encoded body; a fully airtight guard would need to enforce
a cap while reading the ASGI receive() stream itself. Combined with the
per-IP rate limit in front of the routes that actually cost money (see
rate_limit.py), this is a proportionate mitigation for this project's stage,
not a claim of bulletproof anti-DoS protection.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Generous relative to the largest legitimate payload today (the NDA chat
# endpoint caps at 40 messages * 4000 chars = ~160KB of content).
MAX_BODY_BYTES = 300_000


class MaxBodySizeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                too_large = int(content_length) > MAX_BODY_BYTES
            except ValueError:
                too_large = False
            if too_large:
                return JSONResponse({"detail": "Request body too large."}, status_code=413)
        return await call_next(request)
