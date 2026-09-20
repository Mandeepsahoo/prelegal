import json
from types import SimpleNamespace

import pytest

import app.nda_llm as nda_llm


def _fake_completion(content: str):
    def _completion(**kwargs):
        message = SimpleNamespace(content=content)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])

    return _completion


def test_chat_requires_at_least_one_message(client):
    response = client.post("/api/nda/chat", json={"messages": [], "fields": {}})
    assert response.status_code == 400


def test_chat_happy_path(client, monkeypatch: pytest.MonkeyPatch):
    reply_payload = {
        "reply": "Great, and what's the purpose of sharing information?",
        # The model restates its full current understanding each turn,
        # including the purpose it was already told about.
        "fields": {
            "purpose": "Evaluating a partnership",
            "partyA": {"name": "Alice", "company": "Acme"},
        },
        "is_complete": False,
    }
    monkeypatch.setattr(nda_llm, "completion", _fake_completion(json.dumps(reply_payload)))

    response = client.post(
        "/api/nda/chat",
        json={
            "messages": [{"role": "user", "content": "Alice from Acme is party A"}],
            "fields": {"purpose": "Evaluating a partnership"},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["reply"] == reply_payload["reply"]
    assert body["is_complete"] is False
    assert body["fields"]["partyA"]["name"] == "Alice"
    assert body["fields"]["partyA"]["company"] == "Acme"
    assert body["fields"]["purpose"] == "Evaluating a partnership"


def test_chat_keeps_previous_field_when_model_omits_it(client, monkeypatch: pytest.MonkeyPatch):
    reply_payload = {
        "reply": "Got it, and what's the governing law?",
        # Model forgets to restate the purpose this turn.
        "fields": {"purpose": ""},
        "is_complete": False,
    }
    monkeypatch.setattr(nda_llm, "completion", _fake_completion(json.dumps(reply_payload)))

    response = client.post(
        "/api/nda/chat",
        json={
            "messages": [{"role": "user", "content": "Delaware, please"}],
            "fields": {"purpose": "Evaluating a partnership"},
        },
    )

    assert response.status_code == 200
    assert response.json()["fields"]["purpose"] == "Evaluating a partnership"


def test_chat_reports_is_complete(client, monkeypatch: pytest.MonkeyPatch):
    reply_payload = {
        "reply": "Your NDA is ready to download!",
        "fields": {},
        "is_complete": True,
    }
    monkeypatch.setattr(nda_llm, "completion", _fake_completion(json.dumps(reply_payload)))

    response = client.post(
        "/api/nda/chat",
        json={"messages": [{"role": "user", "content": "That's everything"}], "fields": {}},
    )

    assert response.status_code == 200
    assert response.json()["is_complete"] is True


def test_chat_returns_502_when_llm_call_fails(client, monkeypatch: pytest.MonkeyPatch):
    def _raise(**kwargs):
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr(nda_llm, "completion", _raise)

    response = client.post(
        "/api/nda/chat",
        json={"messages": [{"role": "user", "content": "hello"}], "fields": {}},
    )

    assert response.status_code == 502


def test_chat_returns_502_on_malformed_llm_response(client, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(nda_llm, "completion", _fake_completion("not valid json"))

    response = client.post(
        "/api/nda/chat",
        json={"messages": [{"role": "user", "content": "hello"}], "fields": {}},
    )

    assert response.status_code == 502


def test_chat_rejects_oversized_message_content(client):
    response = client.post(
        "/api/nda/chat",
        json={"messages": [{"role": "user", "content": "x" * 5000}], "fields": {}},
    )

    assert response.status_code == 422


def test_chat_rejects_too_many_messages(client):
    messages = [{"role": "user", "content": "hi"} for _ in range(41)]

    response = client.post("/api/nda/chat", json={"messages": messages, "fields": {}})

    assert response.status_code == 422


def test_chat_rate_limits_after_too_many_requests(client, monkeypatch: pytest.MonkeyPatch):
    reply_payload = {"reply": "ok", "fields": {}, "is_complete": False}
    monkeypatch.setattr(nda_llm, "completion", _fake_completion(json.dumps(reply_payload)))

    body = {"messages": [{"role": "user", "content": "hi"}], "fields": {}}
    for _ in range(20):
        response = client.post("/api/nda/chat", json=body)
        assert response.status_code == 200

    response = client.post("/api/nda/chat", json=body)
    assert response.status_code == 429
