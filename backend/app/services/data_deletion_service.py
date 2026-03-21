from __future__ import annotations

from dataclasses import dataclass

from pydantic import EmailStr, TypeAdapter, ValidationError

from app.core.database import get_supabase_client

_EMAIL_ADAPTER = TypeAdapter(EmailStr)


@dataclass(slots=True)
class DeletionExecutionResult:
    email: str
    user_found: bool
    dry_run: bool
    deleted_rows: dict[str, int]


def normalize_and_validate_email(email: str) -> str:
    normalized = email.lower().strip()
    try:
        validated = _EMAIL_ADAPTER.validate_python(normalized)
    except ValidationError as exc:
        raise ValueError("Invalid email format") from exc
    return str(validated)


def _count_by(supabase, table: str, field: str, value: str) -> int:
    """Return exact row count without fetching row data."""
    try:
        result = (
            supabase.table(table)
            .select("*", count="exact")
            .eq(field, value)
            .limit(0)
            .execute()
        )
        return result.count or 0
    except Exception as exc:
        raise RuntimeError(f"Failed to count rows in {table!r}: {exc}") from exc


def _delete_by(supabase, table: str, field: str, value: str) -> int:
    """Delete rows matching field=value and return the deleted row count."""
    try:
        result = (
            supabase.table(table)
            .delete()
            .eq(field, value)
            .execute()
        )
        return len(result.data or [])
    except Exception as exc:
        raise RuntimeError(f"Failed to delete rows from {table!r}: {exc}") from exc


def delete_user_data_by_email(
    *,
    email: str,
    confirm: bool,
    dry_run: bool = False,
) -> DeletionExecutionResult:
    normalized_email = normalize_and_validate_email(email)
    if not confirm:
        raise ValueError("Deletion requires explicit confirmation")

    try:
        supabase = get_supabase_client()
        user_result = (
            supabase.table("users")
            .select("id,email")
            .eq("email", normalized_email)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to look up user: {exc}") from exc

    users = user_result.data or []

    if not users:
        # P-2: clean waitlist PII even when no users row exists for this email
        waitlist_count = (
            _count_by(supabase, "waitlist", "email", normalized_email)
            if dry_run
            else _delete_by(supabase, "waitlist", "email", normalized_email)
        )
        return DeletionExecutionResult(
            email=normalized_email,
            user_found=False,
            dry_run=dry_run,
            deleted_rows={
                "qualifier_responses": 0,
                "runs": 0,
                "magic_link_tokens": 0,
                "waitlist": waitlist_count,
                "users": 0,
            },
        )

    user_id = users[0]["id"]

    if dry_run:
        return DeletionExecutionResult(
            email=normalized_email,
            user_found=True,
            dry_run=True,
            deleted_rows={
                "qualifier_responses": _count_by(
                    supabase, "qualifier_responses", "user_id", user_id
                ),
                "runs": _count_by(supabase, "runs", "user_id", user_id),
                "magic_link_tokens": _count_by(
                    supabase, "magic_link_tokens", "user_id", user_id
                ),
                "waitlist": _count_by(supabase, "waitlist", "email", normalized_email),
                "users": 1,
            },
        )

    # Live deletion — dependents first, then the user row
    qualifier_count = _delete_by(supabase, "qualifier_responses", "user_id", user_id)
    run_count = _delete_by(supabase, "runs", "user_id", user_id)
    token_count = _delete_by(supabase, "magic_link_tokens", "user_id", user_id)
    waitlist_count = _delete_by(supabase, "waitlist", "email", normalized_email)
    user_count = _delete_by(supabase, "users", "id", user_id)

    # P-4: verify the user row was actually removed (guards against silent RLS blocks)
    if user_count == 0:
        raise RuntimeError(
            f"User record for {normalized_email!r} was not deleted — "
            "a database policy may have silently blocked the operation"
        )

    return DeletionExecutionResult(
        email=normalized_email,
        user_found=True,
        dry_run=False,
        deleted_rows={
            "qualifier_responses": qualifier_count,
            "runs": run_count,
            "magic_link_tokens": token_count,
            "waitlist": waitlist_count,
            "users": user_count,
        },
    )
