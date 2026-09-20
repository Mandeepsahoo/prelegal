def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_signup_success(client):
    response = client.post(
        "/api/auth/signup",
        json={"email": "Alice@Example.com", "password": "supersecret1"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == "alice@example.com"
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_signup_rejects_duplicate_email(client):
    client.post(
        "/api/auth/signup",
        json={"email": "bob@example.com", "password": "supersecret1"},
    )
    response = client.post(
        "/api/auth/signup",
        json={"email": "bob@example.com", "password": "anotherpassword"},
    )
    assert response.status_code == 409


def test_signup_rejects_short_password(client):
    response = client.post(
        "/api/auth/signup",
        json={"email": "short@example.com", "password": "123"},
    )
    assert response.status_code == 422


def test_login_success(client):
    client.post(
        "/api/auth/signup",
        json={"email": "carol@example.com", "password": "supersecret1"},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "carol@example.com", "password": "supersecret1"},
    )
    assert response.status_code == 200
    assert response.json()["user"]["email"] == "carol@example.com"


def test_login_rejects_wrong_password(client):
    client.post(
        "/api/auth/signup",
        json={"email": "dave@example.com", "password": "supersecret1"},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "dave@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_login_rejects_unknown_email(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "whatever1"},
    )
    assert response.status_code == 401


def test_me_requires_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_rejects_invalid_token(client):
    response = client.get(
        "/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


def test_me_returns_current_user(client):
    signup_response = client.post(
        "/api/auth/signup",
        json={"email": "erin@example.com", "password": "supersecret1"},
    )
    token = signup_response.json()["access_token"]

    response = client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "erin@example.com"
