from app.core.observability.metrics import MetricsRegistry, NoOpMetricsProvider
from app.core.observability.resource_guard import ResourceGuard


def create_guard():
    provider = NoOpMetricsProvider()
    metrics = MetricsRegistry(provider)
    return ResourceGuard(metrics=metrics)


def test_resource_guard_creation():
    guard = create_guard()

    assert guard is not None
    assert guard.memory_limit_mb > 0
    assert guard.pressure_threshold > 0


def test_get_current_usage_mb_returns_float():
    guard = create_guard()

    usage = guard.get_current_usage_mb()

    assert isinstance(usage, float)
    assert usage > 0


def test_is_under_pressure_returns_bool():
    guard = create_guard()

    result = guard.is_under_pressure()

    assert isinstance(result, bool)


def test_should_reject_task_returns_bool():
    guard = create_guard()

    assert isinstance(guard.should_reject_task("low"), bool)
    assert isinstance(guard.should_reject_task("default"), bool)
    assert isinstance(guard.should_reject_task("high"), bool)
