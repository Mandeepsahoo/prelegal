def _signup_and_get_token(client, email="historyuser@example.com") -> str:
    response = client.post(
        "/api/auth/signup", json={"email": email, "password": "supersecret1"}
    )
    return response.json()["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_save_document_requires_auth(client):
    response = client.post(
        "/api/documents/history",
        json={"document_type_name": "SLA", "title": "My SLA", "content": "# SLA"},
    )
    assert response.status_code == 401


def test_save_and_list_document(client):
    token = _signup_and_get_token(client)

    save_response = client.post(
        "/api/documents/history",
        json={"document_type_name": "SLA", "title": "My SLA", "content": "# SLA"},
        headers=_auth_headers(token),
    )
    assert save_response.status_code == 201
    saved = save_response.json()
    assert saved["title"] == "My SLA"
    assert saved["content"] == "# SLA"

    list_response = client.get("/api/documents/history", headers=_auth_headers(token))
    assert list_response.status_code == 200
    summaries = list_response.json()
    assert len(summaries) == 1
    assert summaries[0]["id"] == saved["id"]
    assert "content" not in summaries[0]  # list view is a summary, not the full content


def test_list_is_scoped_to_the_current_user(client):
    token_a = _signup_and_get_token(client, email="user-a@example.com")
    token_b = _signup_and_get_token(client, email="user-b@example.com")

    client.post(
        "/api/documents/history",
        json={"document_type_name": "SLA", "title": "A's doc", "content": "# A"},
        headers=_auth_headers(token_a),
    )

    response = client.get("/api/documents/history", headers=_auth_headers(token_b))
    assert response.status_code == 200
    assert response.json() == []


def test_get_document_returns_full_content(client):
    token = _signup_and_get_token(client)
    saved = client.post(
        "/api/documents/history",
        json={"document_type_name": "DPA", "title": "My DPA", "content": "# DPA content"},
        headers=_auth_headers(token),
    ).json()

    response = client.get(f"/api/documents/history/{saved['id']}", headers=_auth_headers(token))
    assert response.status_code == 200
    assert response.json()["content"] == "# DPA content"


def test_get_document_rejects_access_by_a_different_user(client):
    token_a = _signup_and_get_token(client, email="owner@example.com")
    token_b = _signup_and_get_token(client, email="intruder@example.com")
    saved = client.post(
        "/api/documents/history",
        json={"document_type_name": "DPA", "title": "Owner's doc", "content": "# secret"},
        headers=_auth_headers(token_a),
    ).json()

    response = client.get(f"/api/documents/history/{saved['id']}", headers=_auth_headers(token_b))
    assert response.status_code == 404


def test_get_nonexistent_document_returns_404(client):
    token = _signup_and_get_token(client)
    response = client.get("/api/documents/history/999999", headers=_auth_headers(token))
    assert response.status_code == 404
