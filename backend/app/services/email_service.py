from __future__ import annotations

import html
from urllib.parse import quote
from typing import Any

import resend

from app.core.config import get_settings

RESULT_EMAIL_SUBJECT = "A SwarmSense elemzesed elkeszult"


def _resolve_reply_to(*, email_reply_to: str, email_from: str) -> str:
    normalized_reply_to = email_reply_to.strip()
    if normalized_reply_to:
        return normalized_reply_to
    return email_from


def _build_result_email_props(
    *, recipient_email: str, result_payload: dict[str, Any], frontend_origin: str
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
    }


def _stance_label_from_value(*, stance: str) -> str:
    if stance == "support":
        return "Tamogatja"
    if stance == "reject":
        return "Elutasitja"
    return "Felteteles"


def _render_result_email_via_frontend_api(
    *, props: dict[str, Any], frontend_origin: str
) -> str:
    import httpx

    url = f"{frontend_origin.rstrip('/')}/api/emails/render-result"
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, json=props)
        response.raise_for_status()
        return response.json()["html"]


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

    resend.Emails.send(
        {
            "from": settings.email_from,
            "to": [recipient_email],
            "reply_to": reply_to,
            "subject": "SwarmSense – Bejelentkezési link",
            "html": (
                "<div style='font-family:Arial,sans-serif;line-height:1.6;'>"
                "<h2>Folytasd a SwarmSense elemzést</h2>"
                "<p>Kattints a lenti gombra az azonosításhoz.</p>"
                f"<p><a href='{verify_url}'>Bejelentkezés magic linkkel</a></p>"
                "<p>Ez a link 24 órán belül lejár.</p>"
                "</div>"
            ),
        }
    )


def send_run_result_email(
    *, recipient_email: str, result_payload: dict[str, Any]
) -> None:
    settings = get_settings()
    resend.api_key = settings.resend_api_key

    reply_to = _resolve_reply_to(
        email_reply_to=settings.email_reply_to,
        email_from=settings.email_from,
    )
    template_props = _build_result_email_props(
        recipient_email=recipient_email,
        result_payload=result_payload,
        frontend_origin=str(settings.frontend_origin),
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
