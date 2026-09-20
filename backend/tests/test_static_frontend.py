from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.static_frontend import _safe_join, build_static_frontend_router


def _make_client(static_dir) -> TestClient:
    app = FastAPI()
    app.include_router(build_static_frontend_router(static_dir))
    return TestClient(app)


def test_serves_index_at_root(tmp_path):
    (tmp_path / "index.html").write_text("<h1>home</h1>")
    client = _make_client(tmp_path)

    response = client.get("/")
    assert response.status_code == 200
    assert "home" in response.text


def test_serves_flat_html_file_for_clean_route(tmp_path):
    (tmp_path / "login.html").write_text("<h1>login</h1>")
    (tmp_path / "login").mkdir()
    (tmp_path / "login" / "payload.txt").write_text("rsc-payload")
    client = _make_client(tmp_path)

    response = client.get("/login")
    assert response.status_code == 200
    assert "login" in response.text


def test_serves_exact_asset_file(tmp_path):
    (tmp_path / "_next").mkdir()
    (tmp_path / "_next" / "app.js").write_text("console.log('hi')")
    client = _make_client(tmp_path)

    response = client.get("/_next/app.js")
    assert response.status_code == 200
    assert "console.log" in response.text


def test_falls_back_to_404_page(tmp_path):
    (tmp_path / "404.html").write_text("<h1>not found</h1>")
    client = _make_client(tmp_path)

    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert "not found" in response.text


def test_safe_join_blocks_path_traversal(tmp_path):
    root = tmp_path / "out"
    root.mkdir()

    assert _safe_join(root, "../secret.txt") is None
    assert _safe_join(root, "../../etc/passwd") is None


def test_safe_join_allows_paths_within_root(tmp_path):
    root = tmp_path / "out"
    root.mkdir()

    resolved = _safe_join(root, "_next/static/app.js")
    assert resolved == (root / "_next" / "static" / "app.js").resolve()
