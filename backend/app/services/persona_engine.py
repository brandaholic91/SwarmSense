from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

from pydantic import ValidationError

from app.models.persona import (
    PersonaBlueprint,
    PersonaFailure,
    PersonaResponse,
    PersonaRunResult,
    SynthesisResult,
)
from app.services.llm_client import LLMProviderError, OpenRouterClient

DEFAULT_PERSONA_COUNT = 18
MIN_PERSONA_COUNT = 15
MAX_PERSONA_COUNT = 20

HUNGARIAN_SYSTEM_PROMPT = (
    "Te egy magyar piacismerettel rendelkező stratégiai személyiség vagy. "
    "Kizárólag magyar nyelven válaszolj. "
    "A válasz legyen pontos JSON objektum a kért kulcsokkal, extra mezők nélkül."
)

HUNGARIAN_MARKET_CONTEXT = (
    "Fókuszálj magyarországi vállalati valóságra, helyi vásárlói viselkedésre, "
    "magyar piaci sajátosságokra, és magyar üzleti nyelvezetre."
)

PERSONA_BLUEPRINT_DEFINITIONS: tuple[dict[str, str], ...] = (
    {
        "name": "Varga Tibor",
        "role": "CFO",
        "risk_appetite": "alacsony",
        "decision_style": "adat- és bizonyíték alapú",
        "organizational_role": "pénzügyi döntéshozó",
        "price_sensitivity": "magas",
        "technology_adoption_curve": "késői többség",
    },
    {
        "name": "Fekete Nóra",
        "role": "Growth Lead",
        "risk_appetite": "magas",
        "decision_style": "kísérletező és gyors",
        "organizational_role": "növekedési vezető",
        "price_sensitivity": "közepes",
        "technology_adoption_curve": "korai alkalmazó",
    },
    {
        "name": "Tóth Miklós",
        "role": "Operations Manager",
        "risk_appetite": "alacsony",
        "decision_style": "folyamatfegyelmet követő",
        "organizational_role": "működési vezető",
        "price_sensitivity": "közepes",
        "technology_adoption_curve": "késői többség",
    },
    {
        "name": "Horváth Eszter",
        "role": "Product Lead",
        "risk_appetite": "közepesen magas",
        "decision_style": "hipotézis-alapú",
        "organizational_role": "termék döntéshozó",
        "price_sensitivity": "közepes",
        "technology_adoption_curve": "innovator",
    },
    {
        "name": "Szabó Gergő",
        "role": "Head of IT",
        "risk_appetite": "alacsony",
        "decision_style": "biztonság-központú",
        "organizational_role": "technológiai kapuőr",
        "price_sensitivity": "alacsony",
        "technology_adoption_curve": "késői alkalmazó",
    },
    {
        "name": "Nagy Zsófia",
        "role": "Marketing Director",
        "risk_appetite": "közepes",
        "decision_style": "kutatásra támaszkodó",
        "organizational_role": "marketing döntéshozó",
        "price_sensitivity": "közepesen magas",
        "technology_adoption_curve": "korai többség",
    },
    {
        "name": "Kiss Bence",
        "role": "Founder",
        "risk_appetite": "közepesen magas",
        "decision_style": "eredmény-központú",
        "organizational_role": "végső döntéshozó",
        "price_sensitivity": "magas",
        "technology_adoption_curve": "korai alkalmazó",
    },
    {
        "name": "Molnár Judit",
        "role": "Legal Lead",
        "risk_appetite": "nagyon alacsony",
        "decision_style": "szabályozás-követő",
        "organizational_role": "jogi kontroll",
        "price_sensitivity": "közepes",
        "technology_adoption_curve": "késői többség",
    },
    {
        "name": "Simon Áron",
        "role": "RevOps Manager",
        "risk_appetite": "közepes",
        "decision_style": "metrika-központú",
        "organizational_role": "bevételi folyamatfelelős",
        "price_sensitivity": "közepes",
        "technology_adoption_curve": "korai többség",
    },
    {
        "name": "Farkas Kata",
        "role": "HR Director",
        "risk_appetite": "közepes",
        "decision_style": "emberközpontú",
        "organizational_role": "szervezeti támogató",
        "price_sensitivity": "magas",
        "technology_adoption_curve": "korai többség",
    },
    {
        "name": "Kovács Levente",
        "role": "CTO",
        "risk_appetite": "közepesen magas",
        "decision_style": "technikai trade-off alapú",
        "organizational_role": "technológiai vezető",
        "price_sensitivity": "alacsony",
        "technology_adoption_curve": "innovator",
    },
    {
        "name": "Takács Melinda",
        "role": "Procurement Manager",
        "risk_appetite": "alacsony",
        "decision_style": "alkuorientált",
        "organizational_role": "beszerzési döntéshozó",
        "price_sensitivity": "nagyon magas",
        "technology_adoption_curve": "késői többség",
    },
    {
        "name": "Balogh Dávid",
        "role": "Security Lead",
        "risk_appetite": "nagyon alacsony",
        "decision_style": "kockázatminimalizáló",
        "organizational_role": "biztonsági kontroll",
        "price_sensitivity": "alacsony",
        "technology_adoption_curve": "korai többség",
    },
    {
        "name": "Papp Réka",
        "role": "Sales Director",
        "risk_appetite": "magas",
        "decision_style": "ügyfélszerzési sebesség alapú",
        "organizational_role": "bevételi hajtóerő",
        "price_sensitivity": "közepes",
        "technology_adoption_curve": "korai alkalmazó",
    },
    {
        "name": "Németh Tamás",
        "role": "Managing Director",
        "risk_appetite": "alacsony",
        "decision_style": "likviditási fegyelem",
        "organizational_role": "kkv tulajdonos",
        "price_sensitivity": "nagyon magas",
        "technology_adoption_curve": "késői alkalmazó",
    },
    {
        "name": "Halász Szilvia",
        "role": "BI Manager",
        "risk_appetite": "közepes",
        "decision_style": "elemzés-központú",
        "organizational_role": "adatgazda",
        "price_sensitivity": "közepes",
        "technology_adoption_curve": "korai többség",
    },
    {
        "name": "Szűcs Gábor",
        "role": "Channel Manager",
        "risk_appetite": "közepes",
        "decision_style": "kapcsolat- és bizalom alapú",
        "organizational_role": "partneri növekedés felelős",
        "price_sensitivity": "közepesen magas",
        "technology_adoption_curve": "korai többség",
    },
    {
        "name": "Erdős Anita",
        "role": "Customer Success Lead",
        "risk_appetite": "közepes",
        "decision_style": "lemorzsolódás-csökkentő",
        "organizational_role": "ügyfélkapcsolati vezető",
        "price_sensitivity": "közepes",
        "technology_adoption_curve": "korai többség",
    },
)


def build_persona_blueprints(
    total_personas: int = DEFAULT_PERSONA_COUNT,
) -> list[PersonaBlueprint]:
    if total_personas < MIN_PERSONA_COUNT or total_personas > MAX_PERSONA_COUNT:
        raise ValueError(
            f"A személyiségek száma csak {MIN_PERSONA_COUNT}-{MAX_PERSONA_COUNT} lehet."
        )
    if total_personas > len(PERSONA_BLUEPRINT_DEFINITIONS):
        raise ValueError(
            f"Nincs elég személyiség-definíció: {total_personas} kért, "
            f"{len(PERSONA_BLUEPRINT_DEFINITIONS)} elérhető."
        )

    selected = PERSONA_BLUEPRINT_DEFINITIONS[:total_personas]
    return [PersonaBlueprint.model_validate(item) for item in selected]


def build_persona_user_prompt(
    *,
    persona: PersonaBlueprint,
    topic: str,
    audience: str,
) -> str:
    return (
        "Készíts véleményt a következő kutatási kérdésről, a megadott személyiség nézetéből.\n"
        f"Kutatási téma: {topic}\n"
        f"Célközönség: {audience}\n"
        "Személyiség paraméterei:\n"
        f"- Név: {persona.name}\n"
        f"- Szervezeti szerep: {persona.organizational_role}\n"
        f"- Döntő szerep: {persona.role}\n"
        f"- Kockázatvállalási hajlandóság: {persona.risk_appetite}\n"
        f"- Döntési stílus: {persona.decision_style}\n"
        f"- Árérzékenység: {persona.price_sensitivity}\n"
        f"- Technológiai adoptáció: {persona.technology_adoption_curve}\n"
        f"Piaci keret: {HUNGARIAN_MARKET_CONTEXT}\n"
        "Válaszolj JSON objektummal pontosan ezekkel a kulcsokkal:\n"
        "name, role, stance, primary_argument, change_condition, core_concern, buying_trigger\n"
        "A stance értéke kizárólag: support | reject | conditional\n"
        "Hosszúsági szabályok – minden szöveges mező PONTOSAN 1 teljes, lezárt mondat, maximum 25 szó:\n"
        "- primary_argument: az elsődleges érv, max 25 szó\n"
        "- change_condition: mi változtatná meg a véleményét, max 25 szó\n"
        "- core_concern: a mélyebb, mögöttes aggodalom, max 25 szó\n"
        "- buying_trigger: konkrét trigger ami elfogadáshoz vezetne, max 25 szó"
    )


def normalize_persona_response(payload: dict[str, Any]) -> PersonaResponse:
    try:
        return PersonaResponse.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(
            "A provider válasz nem felel meg az elvárt sémának."
        ) from exc


async def execute_persona_engine(
    *,
    topic: str,
    audience: str,
    llm_client: OpenRouterClient | None = None,
    concurrency_limit: int = 5,
    total_personas: int = DEFAULT_PERSONA_COUNT,
    on_persona_completed: Callable[[int, int], None] | None = None,
) -> PersonaRunResult:
    client = llm_client or OpenRouterClient()
    personas = build_persona_blueprints(total_personas)
    semaphore = asyncio.Semaphore(concurrency_limit)

    async def _run_persona(
        persona: PersonaBlueprint,
    ) -> tuple[PersonaBlueprint, PersonaResponse | PersonaFailure, float]:
        async with semaphore:
            prompt = build_persona_user_prompt(
                persona=persona, topic=topic, audience=audience
            )
            try:
                raw, cost_usd = await client.generate_persona_response_with_meta(
                    system_prompt=HUNGARIAN_SYSTEM_PROMPT,
                    user_prompt=prompt,
                )
                return persona, normalize_persona_response(raw), cost_usd
            except LLMProviderError as exc:
                return (
                    persona,
                    PersonaFailure(
                        persona_name=persona.name,
                        error_code=exc.error_code,
                        error_message=str(exc),
                    ),
                    0.0,
                )
            except ValueError as exc:
                return (
                    persona,
                    PersonaFailure(
                        persona_name=persona.name,
                        error_code="MALFORMED_PROVIDER_OUTPUT",
                        error_message=str(exc),
                    ),
                    0.0,
                )

    tasks = [asyncio.create_task(_run_persona(persona)) for persona in personas]

    responses: list[PersonaResponse] = []
    failures: list[PersonaFailure] = []
    handoff_pairs: list[tuple[PersonaResponse, dict[str, str]]] = []
    total_cost_usd = 0.0

    processed_count = 0
    try:
        for task in asyncio.as_completed(tasks):
            persona_name = "unknown"
            try:
                item = await task
            except Exception as exc:  # pragma: no cover - defensive fallback
                item = exc

            persona_blueprint: PersonaBlueprint | None = None
            if isinstance(item, tuple) and len(item) == 3:
                persona_blueprint, result_item, cost_usd = item
                if isinstance(result_item, PersonaResponse):
                    persona_name = result_item.name
                elif isinstance(result_item, PersonaFailure):
                    persona_name = result_item.persona_name
            else:
                result_item, cost_usd = (
                    PersonaFailure(
                        persona_name=persona_name,
                        error_code="UNEXPECTED_ENGINE_ERROR",
                        error_message=str(item),
                    ),
                    0.0,
                )

            total_cost_usd += max(cost_usd, 0.0)

            if isinstance(result_item, PersonaResponse):
                responses.append(result_item)
                blueprint_attrs: dict[str, str] = {}
                if persona_blueprint is not None:
                    blueprint_attrs = {
                        "risk_appetite": persona_blueprint.risk_appetite,
                        "decision_style": persona_blueprint.decision_style,
                        "price_sensitivity": persona_blueprint.price_sensitivity,
                        "technology_adoption_curve": persona_blueprint.technology_adoption_curve,
                    }
                handoff_pairs.append((result_item, blueprint_attrs))
            elif isinstance(result_item, PersonaFailure):
                failures.append(result_item)
            else:
                failures.append(
                    PersonaFailure(
                        persona_name=persona_name,
                        error_code="UNEXPECTED_ENGINE_ERROR",
                        error_message=str(result_item),
                    )
                )

            processed_count += 1
            if on_persona_completed is not None:
                await asyncio.to_thread(on_persona_completed, processed_count, len(personas))
    except BaseException:
        for t in tasks:
            if not t.done():
                t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise

    handoff_payload = [
        {**resp.model_dump(), **attrs} for resp, attrs in handoff_pairs
    ]

    return PersonaRunResult(
        total_personas=len(personas),
        successful_count=len(responses),
        responses=responses,
        failures=failures,
        handoff_payload=handoff_payload,
        cost_usd=total_cost_usd,
    )
