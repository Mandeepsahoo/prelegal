from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_is_not_plaintext():
    hashed = hash_password("correct horse battery staple")
    assert hashed != "correct horse battery staple"
    assert hashed.startswith("pbkdf2_sha256$")


def test_hash_password_uses_unique_salts():
    first = hash_password("same-password")
    second = hash_password("same-password")
    assert first != second


def test_verify_password_accepts_correct_password():
    hashed = hash_password("hunter2")
    assert verify_password("hunter2", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("hunter2")
    assert verify_password("wrong-password", hashed) is False


def test_verify_password_rejects_malformed_hash():
    assert verify_password("anything", "not-a-real-hash") is False


def test_access_token_round_trip():
    token = create_access_token(subject="42")
    assert decode_access_token(token) == "42"


def test_decode_access_token_rejects_garbage():
    assert decode_access_token("not-a-jwt") is None
