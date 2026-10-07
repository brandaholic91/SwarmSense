from __future__ import annotations

from app import db
from app.core.config import get_settings
from app.core.errors import ErrorCode
from app.services import limits


def _make_runs(
    n: int, *, status: str = "completed", ip_hash: str | None = None
) -> list[str]:
    ids = []
    for _ in range(n):
        row = db.create_run(topic="a", audience="b", ip_hash=ip_hash)
        db.update_run(row["id"], status=status)
        ids.append(row["id"])
    return ids


def _age(run_id: str, hours: int) -> None:
    with db.connect() as conn:
        conn.execute(
            "update runs set created_at = now() - make_interval(hours => %s) "
            "where id = %s",
            (hours, run_id),
        )


def test_hash_ip_is_stable_and_not_the_ip():
    assert limits.hash_ip("203.0.113.7") == limits.hash_ip("203.0.113.7")
    assert limits.hash_ip("203.0.113.7") != limits.hash_ip("203.0.113.8")
    assert "203.0.113.7" not in limits.hash_ip("203.0.113.7")


def test_two_running_runs_is_busy(clean_db):
    _make_runs(2, status="running")
    assert limits.check_run_limits("h") is ErrorCode.BUSY


def test_two_completed_runs_pass(clean_db):
    _make_runs(2, status="completed")
    assert limits.check_run_limits("h") is None


def test_ip_limit_counts_same_hash_only(clean_db):
    _make_runs(3, ip_hash="same")
    assert limits.check_run_limits("same") is ErrorCode.IP_LIMIT_REACHED
    assert limits.check_run_limits("other") is None


def test_daily_limit(clean_db):
    _make_runs(20)
    assert limits.check_run_limits("h") is ErrorCode.DAILY_LIMIT_REACHED


def test_old_runs_do_not_count(clean_db):
    for run_id in _make_runs(20, ip_hash="same"):
        _age(run_id, 25)
    assert limits.check_run_limits("same") is None


def test_failed_runs_count(clean_db):
    _make_runs(3, status="failed", ip_hash="same")
    assert limits.check_run_limits("same") is ErrorCode.IP_LIMIT_REACHED


def test_sample_runs_do_not_count(clean_db):
    _make_runs(20, status="running", ip_hash="same")
    with db.connect() as conn:
        conn.execute("update runs set is_sample = true")
    assert limits.check_run_limits("same") is None


def test_no_ip_hash_skips_ip_check(clean_db):
    _make_runs(5)
    assert limits.check_run_limits(None) is None


def test_order_concurrent_before_ip_before_daily(clean_db):
    _make_runs(2, status="running", ip_hash="same")
    _make_runs(18, ip_hash="same")
    assert limits.check_run_limits("same") is ErrorCode.BUSY
    with db.connect() as conn:
        conn.execute("update runs set status = 'completed'")
    assert limits.check_run_limits("same") is ErrorCode.IP_LIMIT_REACHED
    assert limits.check_run_limits("other") is ErrorCode.DAILY_LIMIT_REACHED


def test_limits_come_from_environment(clean_db, monkeypatch):
    monkeypatch.setenv("SWARMSENSE_RUNS_PER_DAY", "1")
    get_settings.cache_clear()
    _make_runs(1)
    assert limits.check_run_limits("h") is ErrorCode.DAILY_LIMIT_REACHED
