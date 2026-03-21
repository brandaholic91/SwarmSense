from __future__ import annotations

import sentry_sdk

from app.core.config import get_settings
from app.core.database import get_supabase_client


def seed_env(monkeypatch) -> None:
    monkeypatch.setenv("SWARMSENSE_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SWARMSENSE_SUPABASE_SERVICE_KEY", "service-key")
    monkeypatch.setenv("SWARMSENSE_KIMI_API_KEY", "kimi-key")
    monkeypatch.setenv("SWARMSENSE_OPENROUTER_API_KEY", "or_test")
    monkeypatch.setenv("SWARMSENSE_OPERATOR_API_KEY", "operator-key")
    monkeypatch.setenv("SWARMSENSE_INTERNAL_SECRET", "test-internal-secret")
    monkeypatch.setenv("SWARMSENSE_FRONTEND_ORIGIN", "https://swarmsense.vercel.app")
    monkeypatch.setenv("SWARMSENSE_RESEND_API_KEY", "re_test")
    get_settings.cache_clear()
    get_supabase_client.cache_clear()


def test_sentry_init_called_when_dsn_set(monkeypatch) -> None:
    calls = {}

    def fake_init(*, dsn=None, **_kwargs):
        calls["dsn"] = dsn

    # Patch before any create_app invocation within this test scope
    monkeypatch.setattr(sentry_sdk, "init", fake_init)
    monkeypatch.setattr(sentry_sdk, "is_initialized", lambda: False)
    seed_env(monkeypatch)
    monkeypatch.setenv(
        "SWARMSENSE_SENTRY_DSN",
        "https://examplePublicKey@o0.ingest.sentry.io/0",
    )

    # Test _init_sentry directly — avoids re-running module-level app = create_app()
    from app.main import _init_sentry

    _init_sentry("https://examplePublicKey@o0.ingest.sentry.io/0")

    assert calls.get("dsn") == "https://examplePublicKey@o0.ingest.sentry.io/0"


def test_sentry_init_skipped_without_dsn(monkeypatch) -> None:
    called = {"value": False}

    def fake_init(*_args, **_kwargs):
        called["value"] = True

    monkeypatch.setattr(sentry_sdk, "init", fake_init)
    monkeypatch.setattr(sentry_sdk, "is_initialized", lambda: False)
    seed_env(monkeypatch)
    monkeypatch.delenv("SWARMSENSE_SENTRY_DSN", raising=False)

    # create_app() with no DSN must not call sentry_sdk.init
    from app.main import create_app

    create_app()

    assert called["value"] is False
