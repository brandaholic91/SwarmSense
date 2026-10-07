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


def _run_assignments(fields: dict[str, Any]) -> tuple[sql.Composed, list[Any]]:
    unknown = set(fields) - UPDATABLE_RUN_COLUMNS
    if unknown:
        raise ValueError(f"ismeretlen oszlop: {', '.join(sorted(unknown))}")
    assignments = sql.SQL(", ").join(
        sql.SQL("{} = %s").format(sql.Identifier(name)) for name in fields
    )
    values = [Jsonb(v) if name == "result" and v is not None else v
              for name, v in fields.items()]
    return assignments, values


def update_run(run_id: str, **fields: Any) -> None:
    assignments, values = _run_assignments(fields)
    if not fields:
        return
    query = sql.SQL("update runs set {} where id = %s").format(assignments)
    with connect() as conn:
        conn.execute(query, [*values, uuid.UUID(run_id)])


def transition_run(
    run_id: str, *, from_statuses: tuple[str, ...], **fields: Any
) -> bool:
    """Mint az `update_run`, de csak akkor ír, ha a sor státusza a `from_statuses`
    egyike (egy közben lezárt futást nem éleszt újra). Igaz, ha írt."""
    assignments, values = _run_assignments(fields)
    if not fields:
        return False
    query = sql.SQL("update runs set {} where id = %s and status = any(%s)").format(
        assignments
    )
    with connect() as conn:
        return (
            conn.execute(
                query, [*values, uuid.UUID(run_id), list(from_statuses)]
            ).rowcount
            > 0
        )


def finalize_run(run_id: str, **fields: Any) -> bool:
    """Végső írás: csak `running` vagy `composing` sorra."""
    return transition_run(
        run_id, from_statuses=("running", "composing"), **fields
    )


def delete_old_email_requests(*, days: int = 14) -> int:
    with connect() as conn:
        return conn.execute(
            "delete from email_requests "
            "where created_at < now() - make_interval(days => %s)",
            (days,),
        ).rowcount


def fail_stuck_runs(*, minutes: int = 10) -> list[str]:
    """A régóta nem záruló futásokat `failed`-re állítja; az azonosítóikat adja."""
    with connect() as conn:
        rows = conn.execute(
            "update runs set status = 'failed', completed_at = now() "
            "where status in ('queued', 'running', 'composing') and not is_sample "
            "and created_at < now() - make_interval(mins => %s) "
            "returning id",
            (minutes,),
        ).fetchall()
    return [str(row["id"]) for row in rows]


def save_pdf(run_id: str, pdf: bytes) -> None:
    with connect() as conn:
        conn.execute("update runs set pdf = %s where id = %s", (pdf, uuid.UUID(run_id)))


def get_pdf(run_id: str) -> bytes | None:
    try:
        parsed = uuid.UUID(run_id)
    except (ValueError, AttributeError, TypeError):
        return None
    with connect() as conn:
        row = conn.execute("select pdf from runs where id = %s", (parsed,)).fetchone()
    if row is None or row["pdf"] is None:
        return None
    return bytes(row["pdf"])


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


def create_email_request(run_id: str, email: str) -> int:
    with connect() as conn:
        row = conn.execute(
            "insert into email_requests (run_id, email) values (%s, %s) returning id",
            (uuid.UUID(run_id), email),
        ).fetchone()
    return row["id"]


def mark_email_sent(request_id: int) -> None:
    with connect() as conn:
        conn.execute(
            "update email_requests set sent_at = now() where id = %s", (request_id,)
        )


def count_email_requests(*, run_id: str | None = None, hours: int | None = None) -> int:
    query = "select count(*) as n from email_requests where true"
    params: list[Any] = []
    if run_id is not None:
        try:
            params.append(uuid.UUID(run_id))
        except (ValueError, AttributeError, TypeError):
            return 0
        query += " and run_id = %s"
    if hours is not None:
        query += " and created_at > now() - make_interval(hours => %s)"
        params.append(hours)
    with connect() as conn:
        return conn.execute(query, params).fetchone()["n"]


SEED_PATH = Path(__file__).resolve().parent.parent / "seed" / "sample_run.sql"

# A minta exportja ezeket az oszlopokat viszi át. Az `ip_hash` és a `pdf` szándékosan
# kimarad: a fájl nyilvános repóba kerül.
_SAMPLE_RUN_COLUMNS = (
    "id",
    "topic",
    "audience",
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
    "result",
    "input_tokens",
    "output_tokens",
    "created_at",
    "completed_at",
)
# oszlopnév → Postgres-típus; a típus a seed `values` listájának oszlopait rögzíti
# (egy csupa-NULL oszlop különben `text` lenne)
_SAMPLE_EVENT_COLUMN_TYPES = {
    "type": "text",
    "persona_index": "integer",
    "persona_name": "text",
    "attempt": "integer",
    "error_code": "text",
    "duration_ms": "integer",
    "input_tokens": "integer",
    "output_tokens": "integer",
    "created_at": "timestamptz",
}
_SAMPLE_EVENT_COLUMNS = tuple(_SAMPLE_EVENT_COLUMN_TYPES)


def get_sample_run_id() -> str | None:
    with connect() as conn:
        row = conn.execute(
            "select id from runs where is_sample order by created_at desc limit 1"
        ).fetchone()
    return None if row is None else str(row["id"])


def seed_sample_if_missing() -> bool:
    """Ha nincs minta és van seed fájl, lefuttatja. Igaz, ha ettől lett minta.

    A fájl lefutása önmagában nem elég: ha a seed azonosítója közönséges futásként
    már megvan, a seed semmit nem ír, és ilyenkor az eredmény hamis."""
    if not SEED_PATH.is_file() or get_sample_run_id() is not None:
        return False
    with connect() as conn:
        conn.execute(SEED_PATH.read_text(encoding="utf-8"))
    return get_sample_run_id() is not None


def export_sample_sql(run_id: str) -> str:
    """A futás és eseményei beszúró SQL-ként, mintának jelölve, `ip_hash` és PDF nélkül.

    Egyetlen utasítás: az események csak akkor kerülnek be, ha a futás sorát ez a
    végrehajtás szúrta be. Ha az azonosító már létezik (pl. a forrásfutás közönséges
    sorként), a seed semmit nem ír."""
    parsed = uuid.UUID(run_id)
    columns = sql.SQL(", ").join(sql.Identifier(c) for c in _SAMPLE_RUN_COLUMNS)
    event_columns = sql.SQL(", ").join(sql.Identifier(c) for c in _SAMPLE_EVENT_COLUMNS)
    with connect() as conn:
        run = conn.execute(
            sql.SQL("select {} from runs where id = %s").format(columns), (parsed,)
        ).fetchone()
        if run is None:
            raise LookupError("run not found")
        events = conn.execute(
            sql.SQL("select {} from run_events where run_id = %s order by id").format(
                event_columns
            ),
            (parsed,),
        ).fetchall()

        run_values = [
            Jsonb(run[c]) if c == "result" and run[c] is not None else run[c]
            for c in _SAMPLE_RUN_COLUMNS
        ]
        insert_run = sql.SQL(
            "insert into {} ({}) values ({}) on conflict ({}) do nothing"
        ).format(
            sql.Identifier("runs"),
            sql.SQL(", ").join(
                sql.Identifier(c) for c in (*_SAMPLE_RUN_COLUMNS, "is_sample", "ip_hash")
            ),
            sql.SQL(", ").join(sql.Literal(v) for v in [*run_values, True, None]),
            sql.Identifier("id"),
        )
        if not events:
            query = insert_run
        else:
            # az `n` sorszám őrzi meg az események eredeti sorrendjét
            rows = sql.SQL(",\n").join(
                sql.SQL("({})").format(
                    sql.SQL(", ").join(
                        sql.Literal(v)
                        for v in (n, *(event[c] for c in _SAMPLE_EVENT_COLUMNS))
                    )
                )
                for n, event in enumerate(events, start=1)
            )
            query = sql.SQL(
                "with {ins} as (\n{insert_run} returning {id}\n)\n"
                "insert into {events} ({run_id}, {columns})\n"
                "select {ins}.{id}, {typed}\n"
                "from {ins} cross join (values\n{rows}\n) as {e} ({n}, {columns})\n"
                "order by {e}.{n}"
            ).format(
                ins=sql.Identifier("ins"),
                insert_run=insert_run,
                id=sql.Identifier("id"),
                events=sql.Identifier("run_events"),
                run_id=sql.Identifier("run_id"),
                columns=event_columns,
                typed=sql.SQL(", ").join(
                    sql.SQL("{}.{}::{}").format(
                        sql.Identifier("e"), sql.Identifier(c), sql.SQL(pg_type)
                    )
                    for c, pg_type in _SAMPLE_EVENT_COLUMN_TYPES.items()
                ),
                rows=rows,
                e=sql.Identifier("e"),
                n=sql.Identifier("n"),
            )
        # a kapcsolat csak a literálok formázásához kell
        return query.as_string(conn) + ";\n"
