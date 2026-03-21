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


def delete_user_data_by_email(
    *,
    email: str,
    confirm: bool,
    dry_run: bool = False,
) -> DeletionExecutionResult:
    normalized_email = normalize_and_validate_email(email)
    if not confirm:
        raise ValueError("Deletion requires explicit confirmation")

    supabase = get_supabase_client()

    user_result = (
        supabase.table("users")
        .select("id,email")
        .eq("email", normalized_email)
        .limit(1)
        .execute()
    )
    users = user_result.data or []
    if not users:
        return DeletionExecutionResult(
            email=normalized_email,
            user_found=False,
            dry_run=dry_run,
            deleted_rows={
                "qualifier_responses": 0,
                "runs": 0,
                "magic_link_tokens": 0,
                "waitlist": 0,
                "users": 0,
            },
        )

    user_id = users[0]["id"]

    qualifier_rows = (
        supabase.table("qualifier_responses")
        .select("id")
        .eq("user_id", user_id)
        .execute()
        .data
        or []
    )
    run_rows = (
        supabase.table("runs").select("id").eq("user_id", user_id).execute().data or []
    )
    token_rows = (
        supabase.table("magic_link_tokens")
        .select("token")
        .eq("user_id", user_id)
        .execute()
        .data
        or []
    )
    waitlist_rows = (
        supabase.table("waitlist")
        .select("id")
        .eq("email", normalized_email)
        .execute()
        .data
        or []
    )

    if dry_run:
        return DeletionExecutionResult(
            email=normalized_email,
            user_found=True,
            dry_run=True,
            deleted_rows={
                "qualifier_responses": len(qualifier_rows),
                "runs": len(run_rows),
                "magic_link_tokens": len(token_rows),
                "waitlist": len(waitlist_rows),
                "users": 1,
            },
        )

    deleted_qualifier_rows = (
        supabase.table("qualifier_responses")
        .delete()
        .eq("user_id", user_id)
        .execute()
        .data
        or []
    )
    deleted_run_rows = (
        supabase.table("runs").delete().eq("user_id", user_id).execute().data or []
    )
    deleted_token_rows = (
        supabase.table("magic_link_tokens")
        .delete()
        .eq("user_id", user_id)
        .execute()
        .data
        or []
    )
    deleted_waitlist_rows = (
        supabase.table("waitlist").delete().eq("email", normalized_email).execute().data
        or []
    )
    deleted_user_rows = (
        supabase.table("users").delete().eq("id", user_id).execute().data or []
    )

    return DeletionExecutionResult(
        email=normalized_email,
        user_found=True,
        dry_run=False,
        deleted_rows={
            "qualifier_responses": len(deleted_qualifier_rows),
            "runs": len(deleted_run_rows),
            "magic_link_tokens": len(deleted_token_rows),
            "waitlist": len(deleted_waitlist_rows),
            "users": len(deleted_user_rows),
        },
    )
