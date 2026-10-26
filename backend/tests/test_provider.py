import asyncio
import json

import httpx
import pytest

from app.core.config import Settings
from app.llm.errors import LLMNotConfigured, LLMProviderError, LLMRateLimited, LLMTimeout
from app.llm.provider import GroqProvider

URL = "postgresql://query_readonly:pw@localhost:5432/db"


def settings(**kw) -> Settings:
    base = dict(_env_file=None, database_url=URL, llm_model="test-model", llm_api_key="sk-secret")
    base.update(kw)
    return Settings(**base)


def provider(handler, **kw) -> GroqProvider:
    return GroqProvider(settings(**kw), transport=httpx.MockTransport(handler))


def run(coro):
    return asyncio.run(coro)


def ok_response(content: str) -> httpx.Response:
    return httpx.Response(200, json={"choices": [{"message": {"content": content}}]})


def test_success_returns_content_and_sends_expected_payload():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers["authorization"]
        seen["body"] = json.loads(request.content)
        return ok_response('{"status":"clarify"}')

    assert run(provider(handler).generate("sys JSON", "user")) == '{"status":"clarify"}'
    assert seen["auth"] == "Bearer sk-secret"
    assert seen["body"]["model"] == "test-model"
    assert seen["body"]["response_format"] == {"type": "json_object"}
    assert seen["body"]["temperature"] == 0.0


def test_json_schema_mode_sends_schema():
    seen = {}

    def handler(request):
        seen["body"] = json.loads(request.content)
        return ok_response("{}")

    run(provider(handler, llm_json_mode="json_schema").generate("s", "u"))
    rf = seen["body"]["response_format"]
    assert rf["type"] == "json_schema" and "status" in rf["json_schema"]["schema"]["properties"]


def test_rate_limit_maps_to_safe_error():
    with pytest.raises(LLMRateLimited):
        run(provider(lambda r: httpx.Response(429, text="slow down")).generate("s", "u"))


def test_server_error_does_not_leak_body():
    with pytest.raises(LLMProviderError) as ei:
        run(provider(lambda r: httpx.Response(500, text="SECRET INTERNAL TRACE")).generate("s", "u"))
    assert "SECRET" not in str(ei.value) and "SECRET" not in ei.value.public_message


def test_timeout_maps_to_llm_timeout():
    def handler(request):
        raise httpx.ReadTimeout("slow", request=request)

    with pytest.raises(LLMTimeout):
        run(provider(handler).generate("s", "u"))


def test_network_error_maps_to_provider_error():
    def handler(request):
        raise httpx.ConnectError("down", request=request)

    with pytest.raises(LLMProviderError):
        run(provider(handler).generate("s", "u"))


def test_unexpected_response_shape():
    with pytest.raises(LLMProviderError):
        run(provider(lambda r: httpx.Response(200, json={"oops": 1})).generate("s", "u"))


def test_missing_key_is_not_configured():
    with pytest.raises(LLMNotConfigured):
        GroqProvider(settings(llm_api_key=None))


def test_api_key_is_not_printed():
    assert "sk-secret" not in repr(settings())


def test_reasoning_effort_is_sent_only_when_configured():
    seen = []

    def handler(request):
        seen.append(json.loads(request.content))
        return ok_response("{}")

    run(provider(handler).generate("s", "u"))
    run(provider(handler, llm_reasoning_effort="low").generate("s", "u"))
    assert "reasoning_effort" not in seen[0]
    assert seen[1]["reasoning_effort"] == "low"