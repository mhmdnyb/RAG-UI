from app.common.config import Settings


def test_redelivery_waits_longer_than_the_slowest_task():
    s = Settings(
        pipeline_timeout_seconds=120,
        callback_timeout_seconds=30,
        callback_max_attempts=3,
    )
    # 3 x 30s + 1s + 2s backoff
    assert s.callback_worst_case_seconds == 93
    assert s.job_idle_timeout_seconds > s.pipeline_timeout_seconds
    assert s.job_idle_timeout_seconds > s.callback_worst_case_seconds


def test_slow_callback_extends_redelivery_timeout():
    s = Settings(
        pipeline_timeout_seconds=10,
        callback_timeout_seconds=60,
        callback_max_attempts=5,
    )
    assert s.job_idle_timeout_seconds > s.callback_worst_case_seconds
