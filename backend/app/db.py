"""Minden adatbázis-lekérdezés ide kerül. Nyers SQL, psycopg 3, ORM és pool nélkül:
minden függvény a saját kapcsolatát nyitja és zárja."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.core.config import get_settings

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema.sql"

UPDATABLE_RUN_COLUMNS = frozenset(
    {
        "status",
        "persona_count",
        "support_count",
        "reject_count",
        "conditional_count",
        "synthesis_summary",
        "synthesis_main_barriers",
        "synthesis_winning_conditions",
        "synthesis_best_target_segment",
        "synthesis_strategic_recommendation",
        "input_tokens",
        "output_tokens",
        "completed_at",
        "result",
    }
)

EVENT_COLUMNS = frozenset(
    {
        "persona_index",
        "persona_name",
        "attempt",
        "error_code",
        "duration_ms",
        "input_tokens",
        "output_tokens",
    }
)

# A `pdf` oszlop nagy, ezért a get_run nem kéri le.
_RUN_COLUMNS = sql.SQL(
    "id, topic, audience, status, persona_count, support_count, reject_count, "
    "conditional_count, synthesis_summary, synthesis_main_barriers, "
    "synthesis_winning_conditions, synthesis_best_target_segment, "
    "synthesis_strategic_recommendation, result, is_sample, ip_hash, "
    "input_tokens, output_tokens, created_at, completed_at"
)


def connect() -> psycopg.Connection:
    return psycopg.connect(get_settings().database_url, row_factory=dict_row)


def apply_schema() -> None:
    with connect() as conn:
        conn.execute(SCHEMA_PATH.read_text(encoding="utf-8"))


def create_run(
    *, topic: str, audience: str, ip_hash: str | None = None
) -> dict[str, Any]:
    with connect() as conn:
        row = conn.execute(
            "insert into runs (topic, audience, ip_hash) values (%s, %s, %s) "
            "returning id, status, created_at",
            (topic, audience, ip_hash),
        ).fetchone()
    row["id"] = str(row["id"])
    return row


def count_active_runs() -> int:
    with connect() as conn:
        return conn.execute(
            "select count(*) as n from runs "
            "where status in ('queued', 'running', 'composing') and not is_sample"
        ).fetchone()["n"]


def count_runs_since(*, hours: int = 24, ip_hash: str | None = None) -> int:
    query = (
        "select count(*) as n from runs "
        "where created_at > now() - make_interval(hours => %s) and not is_sample"
    )
    params: list[Any] = [hours]
    if ip_hash is not None:
        query += " and ip_hash = %s"
        params.append(ip_hash)
    with connect() as conn:
        return conn.execute(query, params).fetchone()["n"]


def get_run(run_id: str) -> dict[str, Any] | None:
    try:
        parsed = uuid.UUID(run_id)
    except (ValueError, AttributeError, TypeError):
        return None
    with connect() as conn:
        row = conn.execute(
            sql.SQL("select {} from runs where id = %s").format(_RUN_COLUMNS),
            (parsed,),
        ).fetchone()
    if row is None:
        return None
    row["id"] = str(row["id"])
    return row


def update_run(run_id: str, **fields: Any) -> None:
    unknown = set(fields) - UPDATABLE_RUN_COLUMNS
    if unknown:
        raise ValueError(f"ismeretlen oszlop: {', '.join(sorted(unknown))}")
    if not fields:
        return
    assignments = sql.SQL(", ").join(
        sql.SQL("{} = %s").format(sql.Identifier(name)) for name in fields
    )
    query = sql.SQL("update runs set {} where id = %s").format(assignments)
    values = [Jsonb(v) if name == "result" and v is not None else v
              for name, v in fields.items()]
    with connect() as conn:
        conn.execute(query, [*values, uuid.UUID(run_id)])


def insert_event(run_id: str, type: str, **fields: Any) -> int:
    unknown = set(fields) - EVENT_COLUMNS
    if unknown:
        raise ValueError(f"ismeretlen eseménymező: {', '.join(sorted(unknown))}")
    columns = ["run_id", "type", *fields]
    query = sql.SQL("insert into run_events ({}) values ({}) returning id").format(
        sql.SQL(", ").join(sql.Identifier(name) for name in columns),
        sql.SQL(", ").join(sql.Placeholder() for _ in columns),
    )
    with connect() as conn:
        row = conn.execute(query, [uuid.UUID(run_id), type, *fields.values()]).fetchone()
    return row["id"]


def list_events(run_id: str, *, after: int = 0) -> list[dict[str, Any]]:
    try:
        parsed = uuid.UUID(run_id)
    except (ValueError, AttributeError, TypeError):
        return []
    with connect() as conn:
        return conn.execute(
            "select id, type, persona_index, persona_name, attempt, error_code, "
            "duration_ms, input_tokens, output_tokens, created_at "
            "from run_events where run_id = %s and id > %s order by id",
            (parsed, after),
        ).fetchall()


def count_events(run_id: str, type: str) -> int:
    try:
        parsed = uuid.UUID(run_id)
    except (ValueError, AttributeError, TypeError):
        return 0
    with connect() as conn:
        return conn.execute(
            "select count(*) as n from run_events where run_id = %s and type = %s",
            (parsed, type),
        ).fetchone()["n"]
