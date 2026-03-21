from __future__ import annotations

import importlib

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.database import get_supabase_client


def build_client(monkeypatch) -> TestClient:
    monkeypatch.setenv("SWARMSENSE_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SWARMSENSE_SUPABASE_SERVICE_KEY", "service-key")
    monkeypatch.setenv("SWARMSENSE_KIMI_API_KEY", "kimi-key")
    monkeypatch.setenv("SWARMSENSE_OPENROUTER_API_KEY", "or_test")
    monkeypatch.setenv("SWARMSENSE_OPERATOR_API_KEY", "operator-key")
    monkeypatch.setenv("SWARMSENSE_INTERNAL_SECRET", "test-internal-secret")
    monkeypatch.setenv("SWARMSENSE_ENVIRONMENT", "development")
    monkeypatch.setenv("SWARMSENSE_FRONTEND_ORIGIN", "https://swarmsense.vercel.app")
    monkeypatch.setenv("SWARMSENSE_RESEND_API_KEY", "re_key")
    monkeypatch.setenv("SWARMSENSE_EMAIL_FROM", "SwarmSense <noreply@swarmsense.ai>")
    monkeypatch.setenv("SWARMSENSE_EMAIL_REPLY_TO", "support@swarmsense.ai")

    get_settings.cache_clear()
    get_supabase_client.cache_clear()
    import app.main as main
    import app.routers.operator as operator_router

    importlib.reload(operator_router)
    importlib.reload(main)

    return TestClient(main.app)


def test_send_followups_requires_valid_bearer(monkeypatch):
    client = build_client(monkeypatch)

    response = client.post("/api/v1/operator/send-followups")
    assert response.status_code == 403

    response = client.post(
        "/api/v1/operator/send-followups",
        headers={"Authorization": "Bearer wrong-key"},
    )
    assert response.status_code == 403


def test_send_followups_returns_sent_count(monkeypatch):
    client = build_client(monkeypatch)

    import app.routers.operator as operator_router

    monkeypatch.setattr(operator_router, "dispatch_followup_sequence", lambda: 3)

    response = client.post(
        "/api/v1/operator/send-followups",
        headers={"Authorization": "Bearer operator-key"},
    )

    assert response.status_code == 200
    assert response.json() == {"sent": 3}
