import json

import pytest
from fastapi.testclient import TestClient

from app.api import health as health_module
from app.api.queries import get_query_service
from app.core.config import Settings, get_settings
from app.llm.errors import LLMRateLimited, LLMTimeout
from app.llm.provider import FakeProvider
from app.main import create_app
from app.services.query_service import QueryService

URL = "postgresql://query_readonly:pw@localhost:5432/db"
GOOD = json.dumps({"status": "ready", "sql": "SELECT 1", "explanation": "demo", "assumptions": ["a"]})
CLARIFY = json.dumps({"status": "clarify", "clarification_question": "Which metric?", "explanation": "ambiguous"})
UNSUPPORTED = json.dumps({"status": "unsupported", "explanation": "no profit data"})


def make_client(responses=None, **settings_kw) -> TestClient:
    app = create_app()
    settings = Settings(_env_file=None, database_url=URL, llm_provider="fake", **settings_kw)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_query_service] = lambda: QueryService(FakeProvider(responses))
    return TestClient(app, raise_server_exceptions=False)


def test_health():
    r = make_client().get("/health")
    assert r.status_code == 200 and r.json() == {"status": "ok"}
    assert r.headers["X-Request-ID"]


def test_ready_ok(monkeypatch):
    monkeypatch.setattr(health_module, "check_connection", lambda: {"db_user": "query_readonly"})
    r = make_client().get("/ready")
    assert r.status_code == 200 and r.json()["checks"] == {"llm_configured": True, "database": True}


def test_ready_reports_db_down_without_details(monkeypatch):
    def boom():
        raise RuntimeError("password=hunter2 host=10.0.0.5")

    monkeypatch.setattr(health_module, "check_connection", boom)
    r = make_client().get("/ready")
    assert r.status_code == 503 and r.json()["checks"]["database"] is False
    assert "hunter2" not in r.text and "10.0.0.5" not in r.text


def test_query_ready():
    r = make_client([GOOD]).post("/api/v1/query", json={"question": "Show top 5 products by revenue"})
    body = r.json()
    assert r.status_code == 200
    assert body["status"] == "ready" and body["sql"] == "SELECT 1" and body["executed"] is False
    assert body["request_id"] == r.headers["X-Request-ID"]


def test_query_clarify_has_no_sql():
    body = make_client([CLARIFY]).post("/api/v1/query", json={"question": "Show me the best customers"}).json()
    assert body["status"] == "clarify" and body["sql"] is None
    assert body["clarification_question"] == "Which metric?"


def test_query_unsupported():
    body = make_client([UNSUPPORTED]).post("/api/v1/query", json={"question": "What is our profit margin?"}).json()
    assert body["status"] == "unsupported" and body["sql"] is None


@pytest.mark.parametrize("payload", [{}, {"question": ""}, {"question": "  "}, {"question": "x" * 501},
                                      {"question": 5}, {"question": "valid question", "extra": 1}])
def test_invalid_requests_return_422(payload):
    r = make_client([GOOD]).post("/api/v1/query", json=payload)
    assert r.status_code == 422 and r.json()["error_code"] == "invalid_request"


def test_validation_error_does_not_echo_input():
    r = make_client([GOOD]).post("/api/v1/query", json={"question": "x" * 600})
    assert "xxxxxxxxxx" not in r.text


def test_llm_timeout_maps_to_504():
    r = make_client([LLMTimeout()]).post("/api/v1/query", json={"question": "Show top products"})
    assert r.status_code == 504 and r.json()["error_code"] == "llm_timeout"


def test_llm_rate_limit_maps_to_503():
    r = make_client([LLMRateLimited()]).post("/api/v1/query", json={"question": "Show top products"})
    assert r.status_code == 503 and r.json()["error_code"] == "llm_rate_limited"


def test_malformed_output_twice_maps_to_safe_502():
    r = make_client(["garbage", "more garbage"]).post("/api/v1/query", json={"question": "Show top products"})
    assert r.status_code == 502 and r.json()["error_code"] == "llm_bad_output"
    assert "garbage" not in r.text


def test_unexpected_exception_returns_generic_500():
    client = make_client([RuntimeError("db password is hunter2")])
    r = client.post("/api/v1/query", json={"question": "Show top products"})
    assert r.status_code == 500 and r.json()["error_code"] == "internal_error"
    assert "hunter2" not in r.text and "Traceback" not in r.text


def test_request_ids_are_unique_and_server_generated():
    c = make_client()
    ids = {c.get("/health", headers={"X-Request-ID": "attacker"}).headers["X-Request-ID"] for _ in range(5)}
    assert len(ids) == 5 and "attacker" not in ids