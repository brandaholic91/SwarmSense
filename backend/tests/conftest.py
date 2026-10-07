from __future__ import annotations

import os

import psycopg
import pytest

from app import db
from app.core.config import get_settings

TEST_DATABASE_URL = os.environ.get(
    "SWARMSENSE_TEST_DATABASE_URL",
    "postgresql://swarmsense:swarmsense@localhost:5433/swarmsense_test",
)


@pytest.fixture(autouse=True)
def settings_env(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("SWARMSENSE_DATABASE_URL", TEST_DATABASE_URL)
    monkeypatch.setenv("SWARMSENSE_INTERNAL_SECRET", "test-internal-secret")
    monkeypatch.setenv("SWARMSENSE_FRONTEND_ORIGIN", "http://localhost:3000")
    monkeypatch.setenv("SWARMSENSE_ENVIRONMENT", "development")
    monkeypatch.setenv("SWARMSENSE_LLM_API_KEY", "test-llm-key")
    monkeypatch.setenv("SWARMSENSE_IP_HASH_SECRET", "test-ip-secret")
    yield
    get_settings.cache_clear()


@pytest.fixture(scope="session")
def _schema():
    dbname = psycopg.conninfo.conninfo_to_dict(TEST_DATABASE_URL).get("dbname", "")
    if not dbname.endswith("_test"):
        pytest.exit(
            f"A teszt-adatbázis neve '_test'-re kell végződjön, nem: {dbname!r}",
            returncode=2,
        )
    with psycopg.connect(TEST_DATABASE_URL, autocommit=True) as conn:
        conn.execute(db.SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def clean_db(settings_env, _schema):
    with psycopg.connect(TEST_DATABASE_URL, autocommit=True) as conn:
        conn.execute(
            "truncate runs, run_events, email_requests restart identity cascade"
        )


@pytest.fixture(autouse=True)
def no_real_llm(monkeypatch):
    def _blocked(*args, **kwargs):
        raise AssertionError("valódi hálózati hívás tesztben")

    monkeypatch.setattr("app.services.llm_client._post_json_sync", _blocked)
