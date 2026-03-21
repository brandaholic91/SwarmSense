from __future__ import annotations

import hashlib
import hmac as _hmac
import html
import logging
from datetime import UTC, datetime, timedelta
from urllib.parse import quote
from typing import Any

import resend
import sentry_sdk

from app.core.config import get_settings
from app.core.database import get_supabase_client

logger = logging.getLogger(__name__)

RESULT_EMAIL_SUBJECT = "A SwarmSense elemzésed elkészült"
FOLLOW_UP_SUBJECTS = {
    "day1": "Mit tanultunk 24 óra után?",
    "day3": "Új nézőpontok a SwarmSense eredményedhez",
    "day7": "Egy hét után: mit tesztelnél következőnek?",
}
_VALID_DAYS = frozenset(FOLLOW_UP_SUBJECTS)


def _generate_unsubscribe_token(user_id: str, secret: str) -> str:
    return _hmac.new(
        secret.encode(),
        user_id.encode(),
        hashlib.sha256,
    ).hexdigest()


def _verify_unsubscribe_token(user_id: str, token: str, secret: str) -> bool:
    expected = _generate_unsubscribe_token(user_id, secret)
    return _hmac.compare_digest(expected, token)


def _resolve_reply_to(*, email_reply_to: str, email_from: str) -> str:
    normalized_reply_to = email_reply_to.strip()
    if normalized_reply_to:
        return normalized_reply_to
    return email_from


def _build_result_email_props(
    *,
    recipient_email: str,
    result_payload: dict[str, Any],
    frontend_origin: str,
    unsubscribe_url: str | None,
) -> dict[str, Any]:
    personas_payload = result_payload.get("personas")
    personas: list[dict[str, str]] = []
    if isinstance(personas_payload, list):
        for item in personas_payload:
            if not isinstance(item, dict):
                continue
            stance = str(item.get("stance", "conditional"))
            personas.append(
                {
                    "name": str(item.get("name", "")),
                    "role": str(item.get("role", "")),
                    "stance": stance,
                    "stance_label": _stance_label_from_value(stance=stance),
                    "primary_argument": str(item.get("primary_argument", "")),
                    "change_condition": str(item.get("change_condition", "")),
                }
            )

    persona_count_header = str(
        result_payload.get(
            "persona_count_header_display",
            result_payload.get("persona_count_label", ""),
        )
    )

    return {
        "topic": str(result_payload.get("topic", "")),
        "audience": str(result_payload.get("audience", "")),
        "personas": personas,
        "persona_count": persona_count_header,
        "aggregate_score": str(result_payload.get("aggregate_score_display", "")),
        "consensus_flag": str(result_payload.get("consensus_flag_display", "")) or None,
        "user_email": recipient_email,
        "unsubscribe_url": unsubscribe_url,
    }


def _stance_label_from_value(*, stance: str) -> str:
    if stance == "support":
        return "Támogatja"
    if stance == "reject":
        return "Elutasítja"
    return "Feltételes"


def _render_result_email_via_frontend_api(
    *, props: dict[str, Any], frontend_origin: str
) -> str:
    import httpx

    url = f"{frontend_origin.rstrip('/')}/api/emails/render-result"
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, json=props)
        response.raise_for_status()
        data = response.json()
        html_content = data.get("html")
        if not isinstance(html_content, str):
            raise ValueError(f"render-result API returned unexpected payload: {data!r}")
        return html_content


def _render_followup_email_via_frontend_api(
    *, day: str, props: dict[str, Any], frontend_origin: str
) -> str:
    import httpx

    url = f"{frontend_origin.rstrip('/')}/api/emails/render-followup"
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, json={"day": day, **props})
        response.raise_for_status()
        data = response.json()
        html_content = data.get("html")
        if not isinstance(html_content, str):
            raise ValueError(
                f"render-followup API returned unexpected payload: {data!r}"
            )
        return html_content


def _render_magic_link_email_via_frontend_api(
    *, props: dict[str, Any], frontend_origin: str
) -> str:
    import httpx

    url = f"{frontend_origin.rstrip('/')}/api/emails/render-magic-link"
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, json=props)
        response.raise_for_status()
        data = response.json()
        html_content = data.get("html")
        if not isinstance(html_content, str):
            raise ValueError(
                f"render-magic-link API returned unexpected payload: {data!r}"
            )
        return html_content


def _build_result_email_html(props: dict[str, Any]) -> str:
    consensus_flag = str(props.get("consensus_flag", "")).strip()
    persona_rows = ""
    for persona in props.get("personas", []):
        if not isinstance(persona, dict):
            continue
        persona_rows += (
            "<tr><td style='padding:12px 0;border-top:1px solid #e2e8f0;'>"
            f"<p style='margin:0;color:#0f172a;font-size:14px;line-height:20px;font-weight:700;'>{html.escape(str(persona.get('name', '')))}</p>"
            f"<p style='margin:2px 0 0 0;color:#475569;font-size:13px;line-height:20px;'>{html.escape(str(persona.get('role', '')))}</p>"
            f"<p style='margin:8px 0 0 0;color:#0f172a;font-size:13px;line-height:20px;'><strong>Allaspont:</strong> {html.escape(str(persona.get('stance_label', '')))}</p>"
            f"<p style='margin:6px 0 0 0;color:#0f172a;font-size:13px;line-height:20px;'><strong>Elsodleges erv:</strong> {html.escape(str(persona.get('primary_argument', '')))}</p>"
            f"<p style='margin:6px 0 0 0;color:#0f172a;font-size:13px;line-height:20px;'><strong>Mi valtoztatna meg a velemenyet:</strong> {html.escape(str(persona.get('change_condition', '')))}</p>"
            "</td></tr>"
        )

    consensus_section = ""
    if consensus_flag:
        consensus_section = (
            "<tr><td style='padding:16px 0 0 0;'>"
            f"<p style='margin:0;color:#0f172a;font-size:14px;line-height:22px;font-weight:700;'>⚠ Konszenzus jelzes: {html.escape(consensus_flag)}</p>"
            "</td></tr>"
        )

    return (
        "<div style='margin:0;padding:0;background:#f8fafc;color:#0f172a;font-family:Arial,sans-serif;'>"
        "<table role='presentation' width='100%' cellpadding='0' cellspacing='0' style='width:100%;padding:24px 12px;background:#f8fafc;'><tbody><tr><td align='center'>"
        "<table role='presentation' width='100%' cellpadding='0' cellspacing='0' style='width:100%;max-width:640px;border:1px solid #e2e8f0;background:#ffffff;'><tbody>"
        "<tr><td style='padding:28px 24px 8px 24px;'>"
        "<h1 style='margin:0;color:#0f172a;font-size:28px;line-height:34px;font-weight:700;'>Itt van a SwarmSense eredmenyed</h1>"
        "<p style='margin:12px 0 0 0;color:#475569;font-size:15px;line-height:24px;'>A szemelyek lefutottak, az osszefoglalo kesz.</p>"
        "</td></tr>"
        "<tr><td style='padding:4px 24px 0 24px;'><div style='border-top:2px solid #3b82f6;height:2px;line-height:0;font-size:0;'>&nbsp;</div></td></tr>"
        f"{consensus_section}"
        "<tr><td style='padding:16px 24px 0 24px;'>"
        "<p style='margin:0;color:#475569;font-size:12px;line-height:18px;'>Aggregalt tamogatasi arany</p>"
        f"<p style='margin:4px 0 0 0;color:#0f172a;font-size:20px;line-height:30px;font-weight:700;'>{html.escape(str(props.get('aggregate_score', '')))}</p>"
        "</td></tr>"
        "<tr><td style='padding:16px 24px 0 24px;'>"
        "<p style='margin:0;color:#475569;font-size:12px;line-height:18px;'>Kutatasi tema</p>"
        f"<p style='margin:4px 0 0 0;color:#0f172a;font-size:16px;line-height:24px;font-weight:600;'>{html.escape(str(props.get('topic', '')))}</p>"
        "</td></tr>"
        "<tr><td style='padding:8px 24px 0 24px;'>"
        "<p style='margin:0;color:#475569;font-size:12px;line-height:18px;'>Celkozonseg</p>"
        f"<p style='margin:4px 0 0 0;color:#0f172a;font-size:16px;line-height:24px;font-weight:600;'>{html.escape(str(props.get('audience', '')))}</p>"
        "</td></tr>"
        "<tr><td style='padding:8px 24px 0 24px;'>"
        "<p style='margin:0;color:#475569;font-size:12px;line-height:18px;'>Lefutott szemelyek</p>"
        f"<p style='margin:4px 0 0 0;color:#0f172a;font-size:16px;line-height:24px;font-weight:700;'>{html.escape(str(props.get('persona_count', '')))}</p>"
        "</td></tr>"
        "<tr><td style='padding:20px 24px 0 24px;'>"
        "<h2 style='margin:0;color:#0f172a;font-size:18px;line-height:24px;font-weight:700;'>Persona visszajelzesek</h2>"
        "<table role='presentation' width='100%' cellpadding='0' cellspacing='0' style='width:100%;margin-top:12px;'><tbody>"
        f"{persona_rows}"
        "</tbody></table>"
        "</td></tr>"
        "<tr><td style='padding:20px 24px 0 24px;'>"
        f"<p style='margin:0;color:#0f172a;font-size:16px;line-height:24px;font-weight:700;'>Mit tennel maskepp ennek alapjan?</p>"
        f"<p style='margin:8px 0 0 0;color:#475569;font-size:13px;line-height:20px;'>Jelentkezz a varolistara, hogy elso korben kapj ertesitest a nyitasrol.</p>"
        f"<p style='margin:12px 0 0 0;'><a href='{str(props.get('reflection_cta_href', '#'))}' style='display:inline-block;background:#3b82f6;color:#ffffff;text-decoration:none;font-size:14px;line-height:20px;font-weight:700;padding:10px 16px;'>Feliratkozas a Pro varolistara</a></p>"
        "</td></tr>"
        "<tr><td style='padding:16px 24px 24px 24px;'>"
        f"<p style='margin:0;color:#475569;font-size:12px;line-height:20px;'>Erre a cimre kuldtuk: {html.escape(str(props.get('user_email', '')))}</p>"
        "</td></tr>"
        "</tbody></table></td></tr></tbody></table></div>"
    )


def send_magic_link_email(recipient_email: str, verify_url: str) -> None:
    settings = get_settings()
    resend.api_key = settings.resend_api_key
    reply_to = _resolve_reply_to(
        email_reply_to=settings.email_reply_to,
        email_from=settings.email_from,
    )
    rendered_html = _render_magic_link_email_via_frontend_api(
        props={"verify_url": verify_url},
        frontend_origin=str(settings.frontend_origin),
    )

    resend.Emails.send(
        {
            "from": settings.email_from,
            "to": [recipient_email],
            "reply_to": reply_to,
            "subject": "SwarmSense – Bejelentkezési link",
            "html": rendered_html,
        }
    )


def send_run_result_email(
    *, recipient_email: str, result_payload: dict[str, Any], user_id: str | None = None
) -> None:
    settings = get_settings()
    resend.api_key = settings.resend_api_key

    reply_to = _resolve_reply_to(
        email_reply_to=settings.email_reply_to,
        email_from=settings.email_from,
    )
    unsubscribe_url: str | None = None
    if user_id:
        unsubscribe_url = _resolve_unsubscribe_url(
            backend_origin=str(settings.backend_origin),
            user_id=user_id,
            secret=settings.internal_secret,
        )

    template_props = _build_result_email_props(
        recipient_email=recipient_email,
        result_payload=result_payload,
        frontend_origin=str(settings.frontend_origin),
        unsubscribe_url=unsubscribe_url,
    )
    rendered_html = _render_result_email_via_frontend_api(
        props=template_props,
        frontend_origin=str(settings.frontend_origin),
    )

    resend.Emails.send(
        {
            "from": settings.email_from,
            "to": [recipient_email],
            "reply_to": reply_to,
            "subject": RESULT_EMAIL_SUBJECT,
            "html": rendered_html,
        }
    )


def _resolve_unsubscribe_url(*, backend_origin: str, user_id: str, secret: str) -> str:
    base = str(backend_origin).rstrip("/")
    token = _generate_unsubscribe_token(user_id, secret)
    return f"{base}/api/v1/unsubscribe?user_id={quote(user_id)}&token={quote(token)}"


def send_followup_email(*, recipient_email: str, day: str, user_id: str) -> None:
    if day not in _VALID_DAYS:
        raise ValueError(f"Invalid follow-up day: {day!r}")
    settings = get_settings()
    resend.api_key = settings.resend_api_key

    reply_to = _resolve_reply_to(
        email_reply_to=settings.email_reply_to,
        email_from=settings.email_from,
    )
    unsubscribe_url = _resolve_unsubscribe_url(
        backend_origin=str(settings.backend_origin),
        user_id=user_id,
        secret=settings.internal_secret,
    )
    rendered_html = _render_followup_email_via_frontend_api(
        day=day,
        props={"unsubscribe_url": unsubscribe_url},
        frontend_origin=str(settings.frontend_origin),
    )

    resend.Emails.send(
        {
            "from": settings.email_from,
            "to": [recipient_email],
            "reply_to": reply_to,
            "subject": FOLLOW_UP_SUBJECTS[day],
            "html": rendered_html,
            "headers": {
                "List-Unsubscribe": f"<{unsubscribe_url}>",
                "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
            },
        }
    )


def _fetch_followup_candidates(
    *, threshold_days: int, day_field: str
) -> list[dict[str, Any]]:
    supabase = get_supabase_client()
    cutoff = datetime.now(UTC) - timedelta(days=threshold_days)
    result = (
        supabase.table("runs")
        .select("id,user_id,completed_at,day1_sent,day3_sent,day7_sent,status")
        .lt("completed_at", cutoff.isoformat())
        .eq(day_field, False)
        .in_("status", ["completed", "partial"])
        .limit(100)
        .execute()
    )
    rows = result.data or []
    return [row for row in rows if isinstance(row, dict)]


def _load_user_for_followup(*, user_id: str) -> dict[str, Any] | None:
    supabase = get_supabase_client()
    result = (
        supabase.table("users")
        .select("id,email,unsubscribed_at")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )
    rows = result.data or []
    if not rows:
        return None
    row = rows[0]
    return row if isinstance(row, dict) else None


def _mark_followup_sent(*, run_id: str, day_field: str) -> bool:
    supabase = get_supabase_client()
    updated = (
        supabase.table("runs")
        .update({day_field: True})
        .eq("id", run_id)
        .eq(day_field, False)
        .execute()
    )
    rows = updated.data or []
    return len(rows) > 0


def _reset_followup_flag(*, run_id: str, day_field: str) -> None:
    supabase = get_supabase_client()
    (
        supabase.table("runs")
        .update({day_field: False})
        .eq("id", run_id)
        .eq(day_field, True)
        .execute()
    )


def dispatch_followup_sequence() -> int:
    sent = 0
    day_plan: tuple[tuple[str, int, str], ...] = (
        ("day1", 1, "day1_sent"),
        ("day3", 3, "day3_sent"),
        ("day7", 7, "day7_sent"),
    )

    for day, threshold_days, day_field in day_plan:
        candidates = _fetch_followup_candidates(
            threshold_days=threshold_days,
            day_field=day_field,
        )

        for candidate in candidates:
            raw_id = candidate.get("id")
            raw_user_id = candidate.get("user_id")
            if not raw_id or not raw_user_id:
                continue
            run_id = str(raw_id)
            user_id = str(raw_user_id)
            timestamp = datetime.now(UTC).isoformat()

            user_row = _load_user_for_followup(user_id=user_id)
            if user_row is None:
                with sentry_sdk.push_scope() as scope:
                    scope.set_tag("error_code", "FOLLOWUP_RECIPIENT_NOT_FOUND")
                    scope.set_extra("run_id", run_id)
                    scope.set_extra("user_id", user_id)
                    scope.set_extra("day", day)
                    scope.set_extra("timestamp", timestamp)
                    sentry_sdk.capture_message(
                        "Follow-up recipient not found", level="warning"
                    )
                continue

            if user_row.get("unsubscribed_at") is not None:
                logger.info(
                    "Follow-up skipped (unsubscribed): run_id=%s user_id=%s day=%s",
                    run_id,
                    user_id,
                    day,
                )
                continue

            recipient_email = user_row.get("email")
            if not isinstance(recipient_email, str) or not recipient_email:
                continue

            # Claim the send slot before dispatching to prevent duplicate sends
            if not _mark_followup_sent(run_id=run_id, day_field=day_field):
                continue  # already claimed by a concurrent worker

            try:
                send_followup_email(
                    recipient_email=recipient_email,
                    day=day,
                    user_id=user_id,
                )
                sent += 1
                logger.info(
                    "Follow-up sent: run_id=%s user_id=%s day=%s",
                    run_id,
                    user_id,
                    day,
                )
            except Exception as exc:
                _reset_followup_flag(run_id=run_id, day_field=day_field)
                with sentry_sdk.push_scope() as scope:
                    scope.set_tag("error_code", "FOLLOWUP_SEND_FAILED")
                    scope.set_extra("run_id", run_id)
                    scope.set_extra("user_id", user_id)
                    scope.set_extra("day", day)
                    scope.set_extra("timestamp", timestamp)
                    sentry_sdk.capture_exception(exc)

    return sent
