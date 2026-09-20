from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db
from .routers import auth, nda
from .static_frontend import build_static_frontend_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Prelegal API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(nda.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# Serve the statically-exported Next.js frontend, if it has been built.
# Included last, and only when present, so backend-only development/tests
# aren't broken by a missing frontend/out directory, and so this catch-all
# route can never shadow the /api/* routes above.
_static_dir = Path(settings.static_dir)
if _static_dir.exists():
    app.include_router(build_static_frontend_router(_static_dir))
