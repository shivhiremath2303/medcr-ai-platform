from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.observability.middleware import ObservabilityMiddleware


def create_app(success: bool = True) -> FastAPI:
    app = FastAPI()
    app.add_middleware(ObservabilityMiddleware)

    if success:

        @app.get("/ping")
        async def ping():
            return {"status": "ok"}

    else:

        @app.get("/ping")
        async def ping():
            raise RuntimeError("boom")

    return app


def test_request_headers_are_added():
    client = TestClient(create_app())

    response = client.get(
        "/ping",
        headers={"X-Correlation-ID": "test-correlation-id"},
    )

    assert response.status_code == 200

    assert response.headers["X-Correlation-ID"] == "test-correlation-id"
    assert "X-Request-ID" in response.headers
    assert "X-Process-Time" in response.headers


def test_generates_correlation_id_when_missing():
    client = TestClient(create_app())

    response = client.get("/ping")

    assert response.status_code == 200

    assert "X-Correlation-ID" in response.headers
    assert response.headers["X-Correlation-ID"] != ""
    assert "X-Request-ID" in response.headers


def test_request_id_is_unique():
    client = TestClient(create_app())

    r1 = client.get("/ping")
    r2 = client.get("/ping")

    assert r1.headers["X-Request-ID"] != r2.headers["X-Request-ID"]


def test_process_time_is_numeric():
    client = TestClient(create_app())

    response = client.get("/ping")

    process_time = float(response.headers["X-Process-Time"])

    assert process_time >= 0.0


def test_exception_is_propagated():
    client = TestClient(create_app(success=False))

    try:
        client.get("/ping")
        raise AssertionError("Expected RuntimeError")
    except RuntimeError as exc:
        assert str(exc) == "boom"
