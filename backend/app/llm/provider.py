"""LLM provider adapter. Baqi app sirf LLMProvider interface jaanti hai, Groq/Ollama/fake nahi."""
import json
import logging
from typing import Protocol

import httpx

from app.core.config import Settings
from app.llm.errors import (
    LLMNotConfigured,
    LLMProviderError,
    LLMRateLimited,
    LLMTimeout,
)
from app.schemas.llm_outputs import SQLProposal

logger = logging.getLogger(__name__)


class LLMProvider(Protocol):
    name: str

    async def generate(self, system: str, user: str) -> str:
        """Model ka raw text (JSON string) wapas karo."""
        ...


class GroqProvider:
    """Groq OpenAI-compatible chat completions API."""

    name = "groq"

    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        if not settings.llm_configured:
            raise LLMNotConfigured()
        self._s = settings
        self._transport = transport  # tests mein httpx.MockTransport

    def _payload(self, system: str, user: str) -> dict:
        s = self._s
        if s.llm_json_mode == "json_schema":
            response_format = {
                "type": "json_schema",
                "json_schema": {"name": "sql_proposal", "strict": False,
                                "schema": SQLProposal.model_json_schema()},
            }
        else:
            response_format = {"type": "json_object"}   # prompt mein lafz "JSON" hona zaroori hai
        return {
            "model": s.llm_model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": s.llm_temperature,
            "max_completion_tokens": s.llm_max_output_tokens,
            "response_format": response_format,
        }

    async def generate(self, system: str, user: str) -> str:
        s = self._s
        headers = {"Authorization": f"Bearer {s.llm_api_key.get_secret_value()}",  # type: ignore[union-attr]
                   "Content-Type": "application/json"}
        url = s.llm_base_url.rstrip("/") + "/chat/completions"
        try:
            async with httpx.AsyncClient(timeout=s.llm_timeout_seconds, transport=self._transport) as client:
                resp = await client.post(url, headers=headers, json=self._payload(system, user))
        except httpx.TimeoutException as e:
            logger.warning("LLM timeout")
            raise LLMTimeout() from e
        except httpx.RequestError as e:
            logger.warning("LLM network error: %s", type(e).__name__)
            raise LLMProviderError() from e

        if resp.status_code == 429:
            logger.warning("LLM rate limited")
            raise LLMRateLimited()
        if resp.status_code >= 400:
            logger.error("LLM provider returned HTTP %s", resp.status_code)  # body log nahi karte
            raise LLMProviderError()
        try:
            return resp.json()["choices"][0]["message"]["content"] or ""
        except (ValueError, KeyError, IndexError, TypeError) as e:
            logger.error("LLM response had unexpected shape")
            raise LLMProviderError() from e


_DEFAULT_FAKE = json.dumps({
    "status": "ready",
    "sql": ("SELECT p.product_name, SUM(oi.quantity*oi.unit_price - oi.discount_amount) AS revenue "
            "FROM products p JOIN order_items oi ON oi.product_id=p.id JOIN orders o ON o.id=oi.order_id "
            "WHERE o.status='completed' GROUP BY p.id, p.product_name ORDER BY revenue DESC LIMIT 5"),
    "clarification_question": None,
    "explanation": "Top five products by completed-order net revenue (demo fake provider).",
    "assumptions": ["Revenue excludes cancelled and pending orders."],
})


class FakeProvider:
    """Deterministic provider: tests aur LLM_PROVIDER=fake dev mode ke liye (live API ki zarurat nahi)."""

    name = "fake"

    def __init__(self, responses: list[str | Exception] | None = None):
        self._responses = list(responses) if responses is not None else None
        self.calls: list[tuple[str, str]] = []

    async def generate(self, system: str, user: str) -> str:
        self.calls.append((system, user))
        if self._responses is None:
            return _DEFAULT_FAKE
        item = self._responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def get_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "fake":
        return FakeProvider()
    return GroqProvider(settings)