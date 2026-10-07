from __future__ import annotations

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

from app.core import pricing

APP_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = APP_DIR / "templates"
FONTS_DIR = APP_DIR / "assets" / "fonts"

PDF_TIMEOUT_SECONDS: float = 60

STANCE_LABELS = {
    "support": "Támogatja",
    "reject": "Elutasítja",
    "conditional": "Feltételes",
}

# Ugyanaz az állítás, mint az eredményoldal „Mire nem jó” bekezdése
# (frontend/lib/messages.ts, result.limitsText).
LIMITS_TEXT = (
    "Az eredmény szintetikus personák válasza, nem valódi megkérdezés. "
    "Hipotézisek gyors előszűrésére való; döntést megalapozó piackutatást nem vált ki."
)

_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)


def _int_hu(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def _cost_hu(input_tokens: int, output_tokens: int) -> str:
    usd = (
        input_tokens * pricing.INPUT_PRICE_PER_MILLION_USD
        + output_tokens * pricing.OUTPUT_PRICE_PER_MILLION_USD
    ) / 1_000_000
    if usd < 0.01:
        return "< 0,01 USD"
    return f"{usd:.2f}".replace(".", ",") + " USD"


def _date_hu(value: datetime | None) -> str:
    return value.strftime("%Y. %m. %d.") if value is not None else ""


def render_report_html(run: dict[str, Any]) -> str:
    """A futás sora (`db.get_run`) alapján önálló HTML-t ad; tiszta függvény."""
    result = run.get("result") or {}
    personas = [
        {**persona, "stance_label": STANCE_LABELS.get(persona.get("stance"), "")}
        for persona in result.get("personas", [])
    ]
    completed_at = run.get("completed_at")
    duration = (
        f"{round((completed_at - run['created_at']).total_seconds())} mp"
        if completed_at is not None
        else None
    )
    input_tokens = run.get("input_tokens") or 0
    output_tokens = run.get("output_tokens") or 0
    context = {
        "topic": run["topic"],
        "audience": run["audience"],
        "date": _date_hu(run.get("created_at")),
        "stance_counts": result.get("stance_counts", {}),
        "aggregate_display": result.get("aggregate_score_display"),
        "consensus_display": result.get("consensus_flag_display"),
        "top_arguments": result.get("top_arguments", []),
        "synthesis": result.get("synthesis"),
        "personas": personas,
        "persona_label": (
            f"{result.get('completed_persona_count', len(personas))}"
            f"/{result.get('total_persona_count', 18)}"
        ),
        "failed_personas": result.get("failed_personas", []),
        "duration": duration,
        "input_tokens": _int_hu(input_tokens),
        "output_tokens": _int_hu(output_tokens),
        "cost": _cost_hu(input_tokens, output_tokens),
        "limits_text": LIMITS_TEXT,
        "font_regular_url": (FONTS_DIR / "IBMPlexSans-Regular.ttf").as_uri(),
        "font_bold_url": (FONTS_DIR / "IBMPlexSans-Bold.ttf").as_uri(),
    }
    return _env.get_template("report.html.j2").render(**context)


async def html_to_pdf(html: str) -> bytes:
    """Hívásonként indít és zár le egy Chromiumot: a futás saját event loopban
    megy, és egy Playwright-böngésző csak a létrehozó loopjából használható."""
    with tempfile.TemporaryDirectory() as tmp:
        # Fájlból töltjük be: az `about:blank` oldal nem érheti el a `file://` fontot.
        page_path = Path(tmp) / "report.html"
        page_path.write_text(html, encoding="utf-8")
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            try:
                page = await browser.new_page()
                await page.goto(page_path.as_uri(), wait_until="load")
                await page.evaluate("document.fonts.ready")
                return await page.pdf(format="A4", print_background=True)
            finally:
                await browser.close()


async def generate_pdf(run: dict[str, Any]) -> bytes:
    return await asyncio.wait_for(
        html_to_pdf(render_report_html(run)), timeout=PDF_TIMEOUT_SECONDS
    )
