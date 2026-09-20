from app.middleware import MAX_BODY_BYTES


def test_rejects_request_with_oversized_content_length_header(client):
    # The middleware decides from the declared Content-Length, so a tiny
    # actual body with a lying oversized header is enough to exercise it
    # without actually allocating a huge payload in the test.
    response = client.post(
        "/api/nda/chat",
        content=b"{}",
        headers={"Content-Length": str(MAX_BODY_BYTES + 1), "Content-Type": "application/json"},
    )

    assert response.status_code == 413


def test_allows_request_with_content_length_under_the_cap(client):
    response = client.get("/api/health", headers={"Content-Length": "10"})

    assert response.status_code == 200
