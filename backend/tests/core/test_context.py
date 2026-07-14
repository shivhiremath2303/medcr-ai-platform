from app.core.observability.context import (
    get_correlation_id,
    get_request_id,
    get_user_id,
    set_correlation_id,
    set_request_id,
    set_user_id,
)


def test_request_id_round_trip():
    set_request_id("req-123")
    assert get_request_id() == "req-123"


def test_correlation_id_round_trip():
    set_correlation_id("corr-456")
    assert get_correlation_id() == "corr-456"


def test_user_id_round_trip():
    set_user_id("user-789")
    assert get_user_id() == "user-789"


def test_context_values_are_independent():
    set_request_id("request")
    set_correlation_id("correlation")
    set_user_id("user")

    assert get_request_id() == "request"
    assert get_correlation_id() == "correlation"
    assert get_user_id() == "user"