from __future__ import annotations

import pytest

from app import db
from app.core.config import get_settings
from app.services import notifier

WEBHOOK = "https://discord.example.test/api/webhooks/1/token"


@pytest.fixture
def posted(monkeypatch) -> list[str]:
    calls: list[str] = []
    monkeypatch.setattr(notifier, "_post_discord", calls.append)
    return calls


@pytest.fixture
def webhook(monkeypatch):
    monkeypatch.setenv("SWARMSENSE_DISCORD_WEBHOOK_URL", WEBHOOK)
    get_settings.cache_clear()


def test_empty_webhook_posts_nothing(posted):
    notifier.notify_run_failed("abc", "TOO_FEW_PERSONAS")
    notifier.notify_daily_limit_reached()
    assert posted == []


def test_run_failed_message_has_id_code_and_link_but_not_the_topic(
    clean_db, posted, webhook
):
    run = db.create_run(topic="TITKOS-TEMA", audience="TITKOS-KOZONSEG")
    notifier.notify_run_failed(run["id"], "TOO_FEW_PERSONAS")
    assert len(posted) == 1
    message = posted[0]
    assert run["id"] in message
    assert "TOO_FEW_PERSONAS" in message
    assert f"http://localhost:3000/eredmeny/{run['id']}" in message
    assert "TITKOS" not in message
    assert WEBHOOK not in message


def test_daily_limit_message_is_posted(posted, webhook):
    notifier.notify_daily_limit_reached()
    assert len(posted) == 1
    assert "20" in posted[0]


def test_post_failure_is_swallowed_and_only_the_type_is_logged(
    monkeypatch, webhook, caplog
):
    def broken(content: str) -> None:
        raise OSError("nyers")

    monkeypatch.setattr(notifier, "_post_discord", broken)
    with caplog.at_level("INFO", logger="swarmsense.notify"):
        notifier.notify_run_failed("abc", "INTERNAL_ERROR")  # nem dobhat
    assert "OSError" in caplog.text
    assert "nyers" not in caplog.text
