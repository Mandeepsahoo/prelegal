import os
from pathlib import Path

import pytest

_TEST_DB_PATH = Path(__file__).resolve().parent / "test.db"
_MISSING_STATIC_DIR = Path(__file__).resolve().parent / "_no_static_here"

# Must be set before `app.config` is first imported anywhere, so tests never
# touch the real dev database and never try to serve a (nonexistent) frontend.
os.environ.setdefault("DATABASE_PATH", str(_TEST_DB_PATH))
os.environ.setdefault("STATIC_DIR", str(_MISSING_STATIC_DIR))
os.environ.setdefault("SECRET_KEY", "test-secret-key-thats-at-least-32-bytes-long")

from fastapi.testclient import TestClient  # noqa: E402

from app.database import engine  # noqa: E402
from app.main import app  # noqa: E402
from app.routers import documents as documents_router  # noqa: E402
from app.routers.nda import chat_rate_limit  # noqa: E402


@pytest.fixture()
def client():
    chat_rate_limit.reset_for_tests()
    documents_router.chat_rate_limit.reset_for_tests()
    documents_router.classify_rate_limit.reset_for_tests()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session", autouse=True)
def _cleanup_test_database():
    yield
    engine.dispose()
    if _TEST_DB_PATH.exists():
        _TEST_DB_PATH.unlink(missing_ok=True)
