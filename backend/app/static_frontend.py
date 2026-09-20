"""Serves the statically-exported Next.js frontend (frontend/out).

Next.js's static export writes each route as a flat `<route>.html` file
(e.g. `login.html`) rather than `<route>/index.html`, so a plain
`StaticFiles(html=True)` mount 404s on clean URLs like `/login`. This router
resolves a request path against the export directory, trying an exact file
match, then a `.html` suffix, then `index.html`, falling back to the
exported `404.html`.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse


def _safe_join(root: Path, request_path: str) -> Path | None:
    candidate = (root / request_path).resolve()
    if candidate != root and root not in candidate.parents:
        return None  # attempted path traversal (e.g. "../../etc/passwd")
    return candidate


def build_static_frontend_router(static_dir: Path) -> APIRouter:
    router = APIRouter()
    root = static_dir.resolve()

    @router.get("/{full_path:path}")
    async def serve_frontend(full_path: str) -> FileResponse:
        if full_path in ("", "/"):
            index_path = root / "index.html"
            if index_path.is_file():
                return FileResponse(index_path)

        candidate = _safe_join(root, full_path)
        if candidate is not None:
            if candidate.is_file():
                return FileResponse(candidate)

            html_candidate = candidate.with_name(candidate.name + ".html")
            if html_candidate.is_file():
                return FileResponse(html_candidate)

            index_candidate = candidate / "index.html"
            if index_candidate.is_file():
                return FileResponse(index_candidate)

        not_found = root / "404.html"
        if not_found.is_file():
            return FileResponse(not_found, status_code=status.HTTP_404_NOT_FOUND)

        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return router
