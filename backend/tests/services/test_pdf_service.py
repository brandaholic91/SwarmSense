from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from app.services import pdf_service

MARKER = "NYERS-SZOLGALTATOI-UZENET-42"


def make_persona(index: int, stance: str = "support") -> dict[str, Any]:
    return {
        "name": f"Persona {index}",
        "role": "pénzügyi vezető",
        "stance": stance,
        "primary_argument": f"Fő érv {index}.",
        "change_condition": f"Változtató feltétel {index}.",
        "core_concern": f"Fő aggodalom {index}.",
        "buying_trigger": f"Vásárlási kiváltó ok {index}.",
        "risk_appetite": "közepes",
        "decision_style": "adatvezérelt",
        "organizational_role": "döntéshozó",
        "price_sensitivity": "magas",
        "technology_adoption_curve": "korai többség",
    }


def make_run(**overrides: Any) -> dict[str, Any]:
    """A `db.get_run` sora, a `_build_result_payload` alakú `result`-tal."""
    topic = overrides.pop("topic", "Árazás")
    synthesis = overrides.pop(
        "synthesis",
        {
            "summary": "Összefoglaló szöveg.",
            "main_barriers": ["Ár.", "Bizalom."],
            "winning_conditions": "Referenciák.",
            "best_target_segment": "Növekvő KKV-k.",
            "strategic_recommendation": "Pilot indítása.",
        },
    )
    failed = overrides.pop("failed_personas", [])
    personas = [
        make_persona(i, ("support", "reject", "conditional")[i % 3])
        for i in range(1, 19 - len(failed))
    ]
    created = datetime(2026, 10, 7, 12, 0, tzinfo=UTC)
    run: dict[str, Any] = {
        "id": "3f1c2a52-8a54-4c3e-9d57-0a6c6f9b1e11",
        "topic": topic,
        "audience": overrides.pop("audience", "KKV vezetők"),
        "status": "partial" if failed or synthesis is None else "completed",
        "created_at": created,
        "completed_at": created + timedelta(seconds=95),
        "input_tokens": 120_000,
        "output_tokens": 30_000,
        "result": {
            "stance_counts": {"support": 6, "reject": 6, "conditional": 6},
            "aggregate_score_display": "Támogatja: 6 | Elutasítja: 6 | Feltételes: 6",
            "consensus_flag_display": None,
            "top_arguments": ["Első érv.", "Második érv."],
            "completed_persona_count": len(personas),
            "total_persona_count": 18,
            "personas": personas,
            "synthesis": synthesis,
            "failed_personas": failed,
        },
    }
    run.update(overrides)
    return run


def test_html_contains_sections_and_hungarian_text():
    html = pdf_service.render_report_html(make_run(topic="Őszi árazás"))
    for needle in [
        "Őszi árazás",
        "KKV vezetők",
        "Szintetikus elemzés",
        "Szintézis",
        "Hogyan futott",
        "Módszertan és korlátok",
        "Persona 1",
        "Fő érv 1.",
        "Első érv.",
        "Pilot indítása.",
    ]:
        assert needle in html


def test_html_sections_come_in_spec_order():
    html = pdf_service.render_report_html(make_run())
    order = [
        "Szintetikus elemzés",
        "Konszenzus",
        "Szintézis",
        "Persona 1",
        "Hogyan futott",
        "Módszertan és korlátok",
    ]
    positions = [html.index(needle) for needle in order]
    assert positions == sorted(positions)


def test_html_escapes_user_text():
    html = pdf_service.render_report_html(
        make_run(topic='<script>alert(1)</script> & "idézet"')
    )
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_html_without_synthesis_says_so():
    html = pdf_service.render_report_html(make_run(synthesis=None))
    assert "A szintézis nem készült el." in html


def test_html_with_synthesis_has_no_missing_note():
    html = pdf_service.render_report_html(make_run())
    assert "A szintézis nem készült el." not in html


def test_html_lists_failed_personas_with_code_only():
    failed = [
        {"name": "Kiesett Kata", "error_code": "MALFORMED_PROVIDER_OUTPUT"},
        {"name": "Kiesett Béla", "error_code": "TIMEOUT"},
    ]
    html = pdf_service.render_report_html(make_run(failed_personas=failed))
    assert "Kiesett Kata" in html and "MALFORMED_PROVIDER_OUTPUT" in html
    assert "Kiesett Béla" in html and "TIMEOUT" in html
    assert "16/18" in html
    assert MARKER not in html


def test_html_shows_run_data_with_cost_marked_as_estimate():
    html = pdf_service.render_report_html(make_run())
    assert "95 mp" in html
    assert "120 000" in html and "30 000" in html
    # 120 000 * 0,30 / 1M + 30 000 * 1,20 / 1M = 0,072 USD
    assert "0,07" in html
    assert "becslés" in html


def test_html_states_the_limits_like_the_result_page():
    html = pdf_service.render_report_html(make_run())
    assert "nem valódi megkérdezés" in html
    assert "döntést megalapozó piackutatást nem vált ki" in html


def test_html_embeds_bundled_font():
    html = pdf_service.render_report_html(make_run())
    assert "@font-face" in html
    assert "file://" in html
    assert "Outfit.ttf" in html and "SpaceGrotesk.ttf" in html
    for name in ("Outfit.ttf", "SpaceGrotesk.ttf", "OFL-Outfit.txt", "OFL-SpaceGrotesk.txt"):
        assert pdf_service.FONTS_DIR.joinpath(name).is_file()


def test_html_has_no_external_network_reference():
    html = pdf_service.render_report_html(make_run())
    assert "http://" not in html and "https://" not in html


def test_generate_pdf_smoke():
    # valódi Chromium: az egyetlen hely, ahol a tesztben böngésző indul
    pdf = asyncio.run(
        pdf_service.generate_pdf(make_run(topic="Árvíztűrő tükörfúrógép"))
    )
    assert pdf.startswith(b"%PDF-") and len(pdf) > 10_000
    # a becsomagolt betűtípus (JavaScript nélkül is) bekerült a PDF-be
    assert b"Outfit" in pdf and b"SpaceGrotesk" in pdf


def test_generate_pdf_times_out(monkeypatch):
    async def slow(html: str) -> bytes:
        await asyncio.sleep(5)
        return b"%PDF-"

    monkeypatch.setattr(pdf_service, "html_to_pdf", slow)
    monkeypatch.setattr(pdf_service, "PDF_TIMEOUT_SECONDS", 0.05)
    with pytest.raises(asyncio.TimeoutError):
        asyncio.run(pdf_service.generate_pdf(make_run()))


def test_html_from_a_real_run_payload_shows_the_organizational_role(
    clean_db, monkeypatch
):
    from app import db
    from app.services import run_processor
    from tests.services.test_run_processor import AUDIENCE, TOPIC, make_fake_llm

    async def fake_pdf(run: dict[str, Any]) -> bytes:
        return b"%PDF-fake"

    monkeypatch.setattr(pdf_service, "generate_pdf", fake_pdf)
    row = db.create_run(topic=TOPIC, audience=AUDIENCE)
    asyncio.run(
        run_processor.process_run(
            run_id=row["id"],
            topic=TOPIC,
            audience=AUDIENCE,
            llm_client=make_fake_llm(),
        )
    )

    html = pdf_service.render_report_html(db.get_run(row["id"]))

    # a fake LLM blueprintjeiben az organizational_role "döntéshozó"
    assert "Szervezeti szerep: döntéshozó" in html


def test_persona_without_organizational_role_has_no_role_label():
    run = make_run()
    for persona in run["result"]["personas"]:
        del persona["organizational_role"]

    html = pdf_service.render_report_html(run)

    assert "Szervezeti szerep" not in html
    assert "Kockázatvállalás" in html


def test_html_to_pdf_makes_no_external_request():
    import http.server
    import threading

    hits: list[str] = []

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            hits.append(self.path)
            self.send_response(200)
            self.end_headers()

        def log_message(self, *args: Any) -> None:
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/kep.png"
        html = f'<!doctype html><html><body><p>Szia</p><img src="{url}"></body></html>'
        pdf = asyncio.run(pdf_service.html_to_pdf(html))
    finally:
        server.shutdown()

    assert pdf.startswith(b"%PDF-")
    assert hits == []
