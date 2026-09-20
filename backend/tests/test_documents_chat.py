import json
from types import SimpleNamespace

import pytest

import app.documents.llm as documents_llm


def _fake_completion(content: str):
    def _completion(**kwargs):
        message = SimpleNamespace(content=content)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])

    return _completion


def test_list_document_types_includes_mutual_nda_and_ten_generic_types(client):
    response = client.get("/api/documents/types")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 11
    keys = {entry["key"] for entry in body}
    assert "mutual-nda" in keys
    assert "sla" in keys
    special = [entry for entry in body if entry["is_special"]]
    assert [entry["key"] for entry in special] == ["mutual-nda"]


def test_chat_rejects_unknown_document_key(client):
    response = client.post(
        "/api/documents/chat",
        json={"document_key": "not-a-real-doc", "messages": [{"role": "user", "content": "hi"}], "fields": []},
    )
    assert response.status_code == 404


def test_chat_rejects_mutual_nda_key_since_it_has_its_own_dedicated_flow(client):
    response = client.post(
        "/api/documents/chat",
        json={"document_key": "mutual-nda", "messages": [{"role": "user", "content": "hi"}], "fields": []},
    )
    assert response.status_code == 404


def test_chat_requires_at_least_one_message(client):
    response = client.post(
        "/api/documents/chat", json={"document_key": "sla", "messages": [], "fields": []}
    )
    assert response.status_code == 400


def test_chat_happy_path_renders_document(client, monkeypatch: pytest.MonkeyPatch):
    reply_payload = {
        "reply": "Got it, who's the provider?",
        "fields": [{"label": "Customer", "value": "Acme Inc"}],
        "is_complete": False,
    }
    monkeypatch.setattr(documents_llm, "completion", _fake_completion(json.dumps(reply_payload)))

    response = client.post(
        "/api/documents/chat",
        json={
            "document_key": "sla",
            "messages": [{"role": "user", "content": "Acme Inc is the customer"}],
            "fields": [],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["reply"] == reply_payload["reply"]
    assert body["is_complete"] is False
    assert {"label": "Customer", "value": "Acme Inc"} in body["fields"]
    assert "Acme Inc" in body["document"]
    assert "Service Level Agreement" in body["document"]


def test_chat_keeps_previous_field_when_model_omits_it(client, monkeypatch: pytest.MonkeyPatch):
    reply_payload = {
        "reply": "And who's the provider?",
        "fields": [{"label": "Customer", "value": ""}],
        "is_complete": False,
    }
    monkeypatch.setattr(documents_llm, "completion", _fake_completion(json.dumps(reply_payload)))

    response = client.post(
        "/api/documents/chat",
        json={
            "document_key": "sla",
            "messages": [{"role": "user", "content": "what else do you need?"}],
            "fields": [{"label": "Customer", "value": "Acme Inc"}],
        },
    )

    assert response.status_code == 200
    fields_by_label = {f["label"]: f["value"] for f in response.json()["fields"]}
    assert fields_by_label["Customer"] == "Acme Inc"


def test_chat_returns_502_when_llm_call_fails(client, monkeypatch: pytest.MonkeyPatch):
    def _raise(**kwargs):
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr(documents_llm, "completion", _raise)

    response = client.post(
        "/api/documents/chat",
        json={"document_key": "sla", "messages": [{"role": "user", "content": "hi"}], "fields": []},
    )
    assert response.status_code == 502


def test_classify_returns_matched_key(client, monkeypatch: pytest.MonkeyPatch):
    reply_payload = {"matched_key": "dpa", "reply": "Let's set up a Data Processing Agreement."}
    monkeypatch.setattr(documents_llm, "completion", _fake_completion(json.dumps(reply_payload)))

    response = client.post("/api/documents/classify", json={"description": "I need a GDPR data processing doc"})

    assert response.status_code == 200
    assert response.json()["matched_key"] == "dpa"


def test_classify_rejects_hallucinated_key_defensively(client, monkeypatch: pytest.MonkeyPatch):
    reply_payload = {"matched_key": "totally-made-up-key", "reply": "Sure thing!"}
    monkeypatch.setattr(documents_llm, "completion", _fake_completion(json.dumps(reply_payload)))

    response = client.post("/api/documents/classify", json={"description": "something obscure"})

    assert response.status_code == 200
    assert response.json()["matched_key"] is None


def test_classify_returns_none_for_unsupported_request(client, monkeypatch: pytest.MonkeyPatch):
    reply_payload = {
        "matched_key": None,
        "reply": "We don't support wills, but a Partnership Agreement might be closest.",
    }
    monkeypatch.setattr(documents_llm, "completion", _fake_completion(json.dumps(reply_payload)))

    response = client.post("/api/documents/classify", json={"description": "I need a last will and testament"})

    assert response.status_code == 200
    assert response.json()["matched_key"] is None
