from app.rate_limit import make_rate_limiter
from fastapi import HTTPException
from starlette.requests import Request


def _fake_request(client_host: str) -> Request:
    scope = {
        "type": "http",
        "client": (client_host, 12345),
        "headers": [],
    }
    return Request(scope)


def test_allows_requests_under_the_limit():
    limiter = make_rate_limiter(max_requests=3, window_seconds=60)
    request = _fake_request("1.2.3.4")

    for _ in range(3):
        limiter(request)  # should not raise


def test_blocks_requests_over_the_limit():
    limiter = make_rate_limiter(max_requests=3, window_seconds=60)
    request = _fake_request("1.2.3.4")

    for _ in range(3):
        limiter(request)

    try:
        limiter(request)
        assert False, "expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 429


def test_tracks_different_clients_independently():
    limiter = make_rate_limiter(max_requests=1, window_seconds=60)
    limiter(_fake_request("1.1.1.1"))
    limiter(_fake_request("2.2.2.2"))  # different client, should not raise


def test_returning_client_is_pruned_on_its_own_next_request():
    limiter = make_rate_limiter(max_requests=1, window_seconds=0)

    limiter(_fake_request("1.1.1.1"))
    assert limiter.tracked_client_count_for_tests() == 1

    # window_seconds=0 means the first hit is immediately stale, so the
    # client's own next request prunes and replaces it rather than growing.
    limiter(_fake_request("1.1.1.1"))
    assert limiter.tracked_client_count_for_tests() == 1


def test_one_off_visitors_do_not_grow_memory_forever():
    limiter = make_rate_limiter(max_requests=1, window_seconds=0)

    # Each of these is a distinct client that never comes back, so nothing
    # ever prunes their entry via the per-request path (test_returning_client_...
    # above); only a sweep can reclaim them.
    for i in range(5):
        limiter(_fake_request(f"10.0.0.{i}"))
    assert limiter.tracked_client_count_for_tests() == 5

    limiter.force_sweep_for_tests()
    assert limiter.tracked_client_count_for_tests() == 0


def test_sweep_runs_automatically_every_sweep_every_calls():
    limiter = make_rate_limiter(max_requests=1, window_seconds=0, sweep_every=3)

    for i in range(3):
        limiter(_fake_request(f"10.0.1.{i}"))
    # The 3rd call triggers the sweep, which runs before that call's own hit
    # is recorded (so it can't prune itself) but does clear the earlier ones.
    assert limiter.tracked_client_count_for_tests() == 1
