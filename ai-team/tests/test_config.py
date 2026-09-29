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


def test_default_llm_settings_inherited_by_llm_and_router():
    s = Settings(
        _env_file=None,
        default_llm_api_key="default-key",
        default_llm_base_url="https://default.api/v1",
        default_llm_model="default-model",
    )
    assert s.resolved_llm_api_key == "default-key"
    assert s.resolved_llm_base_url == "https://default.api/v1"
    assert s.resolved_llm_model == "default-model"

    assert s.resolved_router_api_key == "default-key"
    assert s.resolved_router_base_url == "https://default.api/v1"
    assert s.resolved_router_model == "default-model"


def test_openai_api_key_acts_as_default_fallback():
    s = Settings(_env_file=None, openai_api_key="sk-test-openai")
    assert s.resolved_llm_api_key == "sk-test-openai"
    assert s.resolved_router_api_key == "sk-test-openai"


def test_module_specific_overrides_take_precedence():
    s = Settings(
        _env_file=None,
        default_llm_api_key="default-key",
        default_llm_base_url="https://default.api/v1",
        default_llm_model="default-model",
        router_api_key="router-key",
        router_base_url="https://router.api/v1",
        router_model="router-model",
        llm_model="custom-generator-model",
    )
    # Router uses its own overrides
    assert s.resolved_router_api_key == "router-key"
    assert s.resolved_router_base_url == "https://router.api/v1"
    assert s.resolved_router_model == "router-model"

    # Generator uses its custom model, but inherits default key and base_url
    assert s.resolved_llm_api_key == "default-key"
    assert s.resolved_llm_base_url == "https://default.api/v1"
    assert s.resolved_llm_model == "custom-generator-model"
