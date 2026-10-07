from __future__ import annotations

import asyncio
import json
import re
from typing import Any, cast

from app import db
from app.models.persona import (
    PersonaFailure,
    PersonaResponse,
    PersonaRunResult,
    SynthesisResult,
)
from app.services import run_processor
from app.services.blueprint_generator import BLUEPRINT_SYSTEM_PROMPT
from app.services.llm_client import LLMClient, TransportError
from app.services.persona_engine import HUNGARIAN_SYSTEM_PROMPT
from app.services.run_processor import (
    _build_result_payload,
    _resolve_final_status,
    dispatch_run_processing,
    process_run,
)
from app.services.synthesis_service import SYNTHESIS_SYSTEM_PROMPT

TOTAL = 18


def _stance_for(index: int) -> str:
    # 1-10 support, 11-15 reject, 16-18 conditional
    if index <= 10:
        return "support"
    if index <= 15:
        return "reject"
    return "conditional"


def _completion(content: dict[str, Any]) -> dict[str, Any]:
    return {
        "choices": [{"message": {"content": json.dumps(content)}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5},
    }


def make_fake_llm(
    *,
    failing_personas: frozenset[str] = frozenset(),
    synthesis_fails: bool = False,
    blueprint_fails: bool = False,
) -> LLMClient:
    """Hamis LLM: a system prompt alapján dönti el, melyik hívás jött.

    - blueprint-hívás: 18 personát ad vissza "Persona 1" ... "Persona 18" névvel
    - persona-hívás: érvényes választ ad a user promptban szereplő névvel;
      ha a név benne van a failing_personas-ban, TransportError(status_code=400)
    - szintézis-hívás: érvényes SynthesisResult-ot ad
    Minden sikeres válasz usage-e: prompt_tokens=10, completion_tokens=5.
    """

    async def transport(
        url: str, headers: dict[str, str], payload: dict[str, Any]
    ) -> dict[str, Any]:
        system_prompt = payload["messages"][0]["content"]
        user_prompt = payload["messages"][1]["content"]

        if system_prompt == BLUEPRINT_SYSTEM_PROMPT:
            if blueprint_fails:
                raise TransportError(status_code=400, body=None)
            return _completion(
                {
                    "personas": [
                        {
                            "name": f"Persona {i}",
                            "role": "vezető",
                            "risk_appetite": "közepes",
                            "decision_style": "adatvezérelt",
                            "organizational_role": "döntéshozó",
                            "price_sensitivity": "közepes",
                            "technology_adoption_curve": "korai többség",
                        }
                        for i in range(1, TOTAL + 1)
                    ]
                }
            )

        if system_prompt == HUNGARIAN_SYSTEM_PROMPT:
            match = re.search(r"- Név: (Persona (\d+))\n", user_prompt)
            assert match is not None, user_prompt
            name, index = match.group(1), int(match.group(2))
            if name in failing_personas:
                raise TransportError(status_code=400, body=None)
            return _completion(
                {
                    "name": name,
                    "role": "vezető",
                    "stance": _stance_for(index),
                    "primary_argument": f"Érv {index}.",
                    "change_condition": "Feltétel.",
                    "core_concern": "Aggodalom.",
                    "buying_trigger": "Trigger.",
                }
            )

        if system_prompt == SYNTHESIS_SYSTEM_PROMPT:
            if synthesis_fails:
                raise TransportError(status_code=400, body=None)
            return _completion(
                {
                    "summary": "Összefoglaló.",
                    "main_barriers": ["Ár.", "Bizalom."],
                    "winning_conditions": "Referenciák.",
                    "best_target_segment": "Növekvő KKV-k.",
                    "strategic_recommendation": "Pilot indítása.",
                }
            )

        raise AssertionError("ismeretlen system prompt")

    async def no_sleep(_: float) -> None:
        return None

    return LLMClient(session_id="test-session", transport=transport, sleep=no_sleep)


def _run(clean_db, **fake_kwargs):
    row = db.create_run(topic="Árazás", audience="KKV vezetők")
    dispatch_run_processing(
        run_id=row["id"],
        topic="Árazás",
        audience="KKV vezetők",
        llm_client=make_fake_llm(**fake_kwargs),
    )
    return db.get_run(row["id"])


def test_completed_run_stores_counts_synthesis_and_tokens(clean_db):
    run = _run(clean_db)
    assert run["status"] == "completed"
    assert run["persona_count"] == 18
    assert (run["support_count"], run["reject_count"], run["conditional_count"]) == (
        10,
        5,
        3,
    )
    assert run["synthesis_summary"]
    assert isinstance(run["synthesis_main_barriers"], list)
    assert (run["input_tokens"], run["output_tokens"]) == (200, 100)  # 20 hívás
    assert run["completed_at"] is not None


def test_partial_when_some_personas_fail(clean_db):
    run = _run(
        clean_db, failing_personas=frozenset({"Persona 1", "Persona 2", "Persona 3"})
    )
    assert run["status"] == "partial"
    assert run["persona_count"] == 15
    assert run["support_count"] == 7
    assert (run["input_tokens"], run["output_tokens"]) == (170, 85)  # 17 sikeres hívás


def test_failed_below_threshold_skips_synthesis(clean_db):
    failing = frozenset(f"Persona {i}" for i in range(1, 8))  # 11 marad
    run = _run(clean_db, failing_personas=failing)
    assert run["status"] == "failed"
    assert run["persona_count"] == 11
    assert run["synthesis_summary"] is None
    assert run["completed_at"] is not None


def test_exactly_threshold_is_not_failed(clean_db):
    failing = frozenset(f"Persona {i}" for i in range(1, 7))  # 12 marad
    assert _run(clean_db, failing_personas=failing)["status"] == "partial"


def test_partial_when_synthesis_fails(clean_db):
    run = _run(clean_db, synthesis_fails=True)
    assert run["status"] == "partial"
    assert run["persona_count"] == 18
    assert run["synthesis_summary"] is None
    assert run["support_count"] == 10


def test_failed_when_persona_generation_fails(clean_db):
    run = _run(clean_db, blueprint_fails=True)  # a dispatch nem dobhat
    assert run["status"] == "failed"
    assert run["completed_at"] is not None


def test_summary_log_has_no_topic_text(clean_db, caplog):
    with caplog.at_level("INFO", logger="swarmsense.run"):
        _run(clean_db)
    assert any("completed" in r.getMessage() for r in caplog.records)
    assert "Árazás" not in caplog.text


def test_default_llm_client_uses_run_session_id(clean_db, monkeypatch):
    created: list[dict[str, Any]] = []

    def recorder(**kwargs: Any) -> LLMClient:
        created.append(kwargs)
        return make_fake_llm()

    monkeypatch.setattr(run_processor, "LLMClient", recorder)
    row = db.create_run(topic="Árazás", audience="KKV vezetők")
    dispatch_run_processing(
        run_id=row["id"], topic="Árazás", audience="KKV vezetők"
    )
    assert created == [{"session_id": f"swarmsense-{row['id']}"}]
    assert db.get_run(row["id"])["status"] == "completed"


def test_client_configuration_error_marks_run_failed(clean_db, monkeypatch):
    def broken(**_: Any) -> LLMClient:
        raise RuntimeError("hibás konfiguráció")

    monkeypatch.setattr(run_processor, "LLMClient", broken)
    row = db.create_run(topic="Árazás", audience="KKV vezetők")
    dispatch_run_processing(  # nem dobhat
        run_id=row["id"], topic="Árazás", audience="KKV vezetők"
    )
    run = db.get_run(row["id"])
    assert run["status"] == "failed"
    assert run["completed_at"] is not None


def test_process_run_returns_engine_result(clean_db):
    row = db.create_run(topic="Árazás", audience="KKV vezetők")
    result = asyncio.run(
        process_run(
            run_id=row["id"],
            topic="Árazás",
            audience="KKV vezetők",
            llm_client=make_fake_llm(),
        )
    )
    assert result.successful_count == 18


def _result(*, successful: int, total: int) -> PersonaRunResult:
    responses = [
        PersonaResponse(
            name=f"Persona-{i}",
            role="Role",
            stance="support",
            primary_argument="Erv",
            change_condition="Feltetel",
            core_concern="Aggodalom",
            buying_trigger="Trigger",
        )
        for i in range(successful)
    ]
    failures = [
        PersonaFailure(persona_name=f"Missing-{i}", error_code="X", error_message="x")
        for i in range(total - successful)
    ]
    return PersonaRunResult(
        total_personas=total,
        successful_count=successful,
        responses=responses,
        failures=failures,
        handoff_payload=[r.model_dump() for r in responses],
    )


def test_resolve_final_status_matrix():
    synthesis = SynthesisResult(
        summary="s",
        main_barriers=["b"],
        winning_conditions="w",
        best_target_segment="t",
        strategic_recommendation="r",
    )
    full, missing = _result(successful=18, total=18), _result(successful=15, total=18)
    assert _resolve_final_status(result=full, synthesis=synthesis) == "completed"
    assert _resolve_final_status(result=full, synthesis=None) == "partial"
    assert _resolve_final_status(result=missing, synthesis=synthesis) == "partial"
    assert _resolve_final_status(result=missing, synthesis=None) == "partial"


def _build_result_with_stances(*, stances: list[str]) -> PersonaRunResult:
    responses = [
        PersonaResponse(
            name=f"Persona-{idx}",
            role="Role",
            stance=cast("Any", stance),
            primary_argument=f"Erv-{idx % 3}",
            change_condition="Feltetel",
            core_concern="Aggodalom",
            buying_trigger="Trigger",
        )
        for idx, stance in enumerate(stances)
    ]
    return PersonaRunResult(
        total_personas=len(stances),
        successful_count=len(stances),
        responses=responses,
        failures=[],
        handoff_payload=[item.model_dump() for item in responses],
    )


def _payload_for(stances: list[str]) -> dict[str, Any]:
    return _build_result_payload(
        run_id="run-1",
        result=_build_result_with_stances(stances=stances),
        final_status="completed",
        topic="Tema",
        audience="Kozonseg",
        synthesis=None,
    )


def test_result_payload_sets_consensus_for_15_of_15_support() -> None:
    payload = _payload_for(["support"] * 15)
    assert payload["aggregate_score"]["support_count"] == 15
    assert payload["aggregate_score"]["reject_count"] == 0
    assert payload["aggregate_score"]["conditional_count"] == 0
    assert (
        payload["aggregate_score_display"]
        == "Támogatja: 15 | Elutasítja: 0 | Feltételes: 0"
    )
    assert payload["consensus_flag"]["is_triggered"] is True
    assert payload["consensus_flag"]["direction"] == "support"
    assert payload["consensus_flag"]["count"] == 15
    assert payload["consensus_flag_display"] == "15 persona támogatja"


def test_result_payload_sets_consensus_for_15_of_18_reject() -> None:
    payload = _payload_for(["reject"] * 15 + ["support", "support", "support"])
    assert payload["aggregate_score"]["support_count"] == 3
    assert payload["aggregate_score"]["reject_count"] == 15
    assert payload["aggregate_score"]["conditional_count"] == 0
    assert payload["consensus_flag"]["is_triggered"] is True
    assert payload["consensus_flag"]["direction"] == "reject"
    assert payload["consensus_flag"]["count"] == 15
    assert payload["consensus_flag_display"] == "15 persona elutasítja"


def test_result_payload_no_consensus_for_14_of_18_support() -> None:
    payload = _payload_for(["support"] * 14 + ["reject"] * 4)
    assert payload["aggregate_score"]["support_count"] == 14
    assert payload["aggregate_score"]["reject_count"] == 4
    assert payload["aggregate_score"]["conditional_count"] == 0
    assert payload["consensus_flag"]["is_triggered"] is False
    assert payload["consensus_flag"]["direction"] is None
    assert payload["consensus_flag"]["count"] is None
    assert payload["consensus_flag_display"] is None


def test_result_payload_no_consensus_when_all_conditional() -> None:
    payload = _payload_for(["conditional"] * 18)
    assert payload["aggregate_score"]["support_count"] == 0
    assert payload["aggregate_score"]["reject_count"] == 0
    assert payload["aggregate_score"]["conditional_count"] == 18
    assert payload["consensus_flag"]["is_triggered"] is False
    assert payload["consensus_flag"]["direction"] is None
    assert payload["consensus_flag"]["count"] is None
    assert payload["consensus_flag_display"] is None
