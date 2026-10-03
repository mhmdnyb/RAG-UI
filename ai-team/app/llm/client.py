from openai import AsyncOpenAI, OpenAI


def create_async_openai_client(api_key: str, base_url: str | None = None, timeout: float = 30.0) -> AsyncOpenAI:
    return AsyncOpenAI(api_key=api_key, base_url=base_url or None, timeout=timeout)


def create_sync_openai_client(api_key: str, base_url: str | None = None, timeout: float = 30.0) -> OpenAI:
    return OpenAI(api_key=api_key, base_url=base_url or None, timeout=timeout)
