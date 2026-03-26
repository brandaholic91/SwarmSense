from __future__ import annotations

from datetime import UTC, datetime

from app.core.database import get_supabase_client


def _normalize_email(email: str) -> str:
    return email.lower().strip()


def is_marketing_email_allowed(*, user_id: str) -> bool:
    supabase = get_supabase_client()
    result = (
        supabase.table("users")
        .select("id,unsubscribed_at")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )
    rows = result.data or []
    if not rows:
        return False
    row = rows[0]
    if not isinstance(row, dict):
        return False
    return row.get("unsubscribed_at") is None


def mark_user_unsubscribed(*, user_id: str) -> None:
    now = datetime.now(UTC).isoformat()
    supabase = get_supabase_client()
    user_result = supabase.table("users").select("email").eq("id", user_id).limit(1).execute()
    (
        supabase.table("users")
        .update({"unsubscribed_at": now})
        .eq("id", user_id)
        .is_("unsubscribed_at", "null")
        .execute()
    )
    rows = user_result.data or []
    user_email = rows[0].get("email") if rows and isinstance(rows[0], dict) else None
    if isinstance(user_email, str) and user_email:
        normalized_email = _normalize_email(user_email)
        supabase.table("waitlist").delete().eq("email", normalized_email).execute()
        # Backward-compatible cleanup for legacy waitlist rows where normalization
        # constraints may have been missing at creation time.
        try:
            waitlist_rows = supabase.table("waitlist").select("email").execute()
            for row in waitlist_rows.data or []:
                row_email = row.get("email") if isinstance(row, dict) else None
                if (
                    isinstance(row_email, str)
                    and row_email
                    and _normalize_email(row_email) == normalized_email
                ):
                    supabase.table("waitlist").delete().eq("email", row_email).execute()
        except Exception:
            # Keep unsubscribe flow resilient even if legacy cleanup fails.
            pass
