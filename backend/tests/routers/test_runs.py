from __future__ import annotations

import importlib

from fastapi.testclient import TestClient

from app.core import cost_enforcement
from app.core.config import get_settings
from app.core.database import get_supabase_client


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeSupabase:
    def __init__(self, data):
        self._data = data

    def table(self, name):
        return self

    def select(self, fields):
        return self

    def eq(self, field, value):
        return self

    def limit(self, n):
        return self

    def execute(self):
        return FakeResponse(self._data)


def build_client(monkeypatch, total_usd):
    monkeypatch.setenv("SWARMSENSE_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SWARMSENSE_SUPABASE_SERVICE_KEY", "service-key")
    monkeypatch.setenv("SWARMSENSE_KIMI_API_KEY", "kimi-key")
    monkeypatch.setenv("SWARMSENSE_OPERATOR_API_KEY", "operator-key")
    monkeypatch.setenv("SWARMSENSE_ENVIRONMENT", "development")
    monkeypatch.setenv("SWARMSENSE_FRONTEND_ORIGIN", "https://swarmsense.vercel.app")
    monkeypatch.setenv("SWARMSENSE_RESEND_API_KEY", "re_test")

    get_settings.cache_clear()
    get_supabase_client.cache_clear()
    import app.main as main

    importlib.reload(main)

    fake_data = [] if total_usd is None else [{"total_usd": total_usd}]
    monkeypatch.setattr(
        cost_enforcement,
        "get_supabase_client",
        lambda: FakeSupabase(fake_data),
    )
    return TestClient(main.app)


def test_run_blocked_at_cap(monkeypatch):
    client = build_client(monkeypatch, "50.00")

    response = client.post("/api/v1/runs")

    assert response.status_code == 402
    assert response.json() == {
        "detail": "A havi ingyenes kapacitás elérte a határát.",
        "code": "COST_LIMIT_REACHED",
    }


def test_run_allowed_below_cap(monkeypatch):
    client = build_client(monkeypatch, "12.34")

    response = client.post("/api/v1/runs")

    assert response.status_code == 200
    assert response.json()["status"] == "queued"


def test_run_allowed_when_no_month_row(monkeypatch):
    client = build_client(monkeypatch, None)

    response = client.post("/api/v1/runs")

    assert response.status_code == 200
    assert response.json()["status"] == "queued"


def test_non_run_endpoints_not_blocked(monkeypatch):
    client = build_client(monkeypatch, "100.00")

    response = client.get("/api/v1/status")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_trailing_slash_still_enforced(monkeypatch):
    client = build_client(monkeypatch, "50.00")

    response = client.post("/api/v1/runs/")

    assert response.status_code == 402


def test_cost_check_failure_returns_503(monkeypatch):
    client = build_client(monkeypatch, None)

    def raise_error():
        from app.core.cost_enforcement import CostCheckError
        raise CostCheckError("db unreachable")

    monkeypatch.setattr(cost_enforcement, "get_supabase_client", raise_error)

    response = client.post("/api/v1/runs")

    assert response.status_code == 503
    assert response.json()["code"] == "COST_CHECK_FAILED"


def test_docs_disabled_in_production(monkeypatch):
    monkeypatch.setenv("SWARMSENSE_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SWARMSENSE_SUPABASE_SERVICE_KEY", "service-key")
    monkeypatch.setenv("SWARMSENSE_KIMI_API_KEY", "kimi-key")
    monkeypatch.setenv("SWARMSENSE_OPERATOR_API_KEY", "operator-key")
    monkeypatch.setenv("SWARMSENSE_ENVIRONMENT", "production")
    monkeypatch.setenv("SWARMSENSE_FRONTEND_ORIGIN", "https://swarmsense.vercel.app")
    monkeypatch.setenv("SWARMSENSE_RESEND_API_KEY", "re_test")

    get_settings.cache_clear()
    get_supabase_client.cache_clear()
    import app.main as main

    importlib.reload(main)

    client = TestClient(main.app, raise_server_exceptions=False)
    assert client.get("/docs").status_code == 404
    assert client.get("/redoc").status_code == 404


def test_cors_allows_frontend_origin(monkeypatch):
    client = build_client(monkeypatch, None)

    response = client.get("/", headers={"Origin": "https://swarmsense.vercel.app"})

    assert response.headers.get("access-control-allow-origin") == "https://swarmsense.vercel.app"


def test_cors_blocks_unknown_origin(monkeypatch):
    client = build_client(monkeypatch, None)

    response = client.get("/", headers={"Origin": "https://evil.example.com"})

    assert "access-control-allow-origin" not in response.headers
