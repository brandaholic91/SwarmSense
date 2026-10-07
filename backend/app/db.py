"""Minden adatbázis-lekérdezés ide kerül. Nyers SQL, psycopg 3, ORM és pool nélkül:
minden függvény a saját kapcsolatát nyitja és zárja."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

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


def create_run(*, topic: str, audience: str) -> dict[str, Any]:
    with connect() as conn:
        row = conn.execute(
            "insert into runs (topic, audience) values (%s, %s) "
            "returning id, status, created_at",
            (topic, audience),
        ).fetchone()
    row["id"] = str(row["id"])
    return row


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
    with connect() as conn:
        conn.execute(query, [*fields.values(), uuid.UUID(run_id)])
