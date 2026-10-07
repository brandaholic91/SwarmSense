from __future__ import annotations

import asyncio
import time
from typing import Any

from pydantic import ValidationError

from app.models.persona import (
    PersonaBlueprint,
    PersonaFailure,
    PersonaResponse,
    PersonaRunResult,
    SynthesisResult,
)
from app.services.blueprint_generator import generate_persona_blueprints
from app.services.events import EventSink, safe_emit
from app.services.llm_client import LLMClient, LLMProviderError, TokenUsage

DEFAULT_PERSONA_COUNT = 18
MIN_PERSONA_COUNT = 15
MAX_PERSONA_COUNT = 20

HUNGARIAN_MARKET_CONTEXT = (
    "Fókuszálj magyarországi vállalati valóságra, helyi vásárlói viselkedésre, "
    "magyar piaci sajátosságokra, és magyar üzleti nyelvezetre."
)

HUNGARIAN_SYSTEM_PROMPT = (
    "Te egy magyar piacismerettel rendelkező stratégiai üzleti elemző vagy. "
    f"{HUNGARIAN_MARKET_CONTEXT} "
    "Kizárólag magyar nyelven válaszolj. "
    "A válasz legyen nyers JSON objektum a kért kulcsokkal, extra mezők nélkül. "
    "Ne használj markdown formázást, kód-blokkot vagy ```json jelölést — "
    "csak a nyers JSON objektumot add vissza."
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
        "technology_adoption_curve": "késlekedő",
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
        "technology_adoption_curve": "késlekedő",
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


def _elapsed_ms(started: float) -> int:
    return int((time.monotonic() - started) * 1000)


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
        "Válaszolj JSON objektummal pontosan ezekkel a kulcsokkal:\n"
        "name, role, stance, primary_argument, change_condition, core_concern, buying_trigger\n"
        "A stance értéke kizárólag: support | reject | conditional\n"
        "Hosszúsági szabályok – minden szöveges mező PONTOSAN 1 teljes, lezárt mondat, maximum 25 szó:\n"
        "- primary_argument: az elsődleges érv, max 25 szó\n"
        "- change_condition: mi változtatná meg a véleményét, max 25 szó\n"
        "- core_concern: a mélyebb, mögöttes aggodalom, max 25 szó\n"
        "- buying_trigger: ha stance=support/conditional: mi erősítené meg az elfogadást; "
        "ha stance=reject: az egyetlen feltétel ami megváltoztathatná az álláspontot, max 25 szó"
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
    llm_client: LLMClient,
    concurrency_limit: int = 5,
    total_personas: int = DEFAULT_PERSONA_COUNT,
    blueprints: list[PersonaBlueprint] | None = None,
    on_event: EventSink | None = None,
) -> PersonaRunResult:
    total_usage = TokenUsage()
    if blueprints is not None:
        personas = blueprints
    else:
        generation_started = time.monotonic()
        personas, blueprint_usage = await generate_persona_blueprints(
            topic=topic,
            audience=audience,
            count=total_personas,
            llm_client=llm_client,
        )
        total_usage += blueprint_usage
        await safe_emit(
            on_event,
            "personas_generated",
            duration_ms=_elapsed_ms(generation_started),
            input_tokens=blueprint_usage.input_tokens,
            output_tokens=blueprint_usage.output_tokens,
        )
    semaphore = asyncio.Semaphore(concurrency_limit)

    async def _run_persona(
        index: int,
        persona: PersonaBlueprint,
    ) -> tuple[PersonaBlueprint, PersonaResponse | PersonaFailure, TokenUsage]:
        # A befejező eseményt még a szemafor elengedése előtt írjuk ki, különben
        # a sorrendben több mint 5 persona látszana egyszerre futónak.
        async with semaphore:
            persona_started = time.monotonic()
            attempt = 1
            await safe_emit(
                on_event,
                "persona_started",
                persona_index=index,
                persona_name=persona.name,
            )

            async def on_retry(next_attempt: int, error_code: str) -> None:
                nonlocal attempt
                attempt = next_attempt
                await safe_emit(
                    on_event,
                    "persona_retry",
                    persona_index=index,
                    persona_name=persona.name,
                    attempt=next_attempt,
                    error_code=error_code,
                )

            prompt = build_persona_user_prompt(
                persona=persona, topic=topic, audience=audience
            )
            usage = TokenUsage()
            response: PersonaResponse | None = None
            error_code = ""
            try:
                raw, usage = await llm_client.generate_json(
                    system_prompt=HUNGARIAN_SYSTEM_PROMPT,
                    user_prompt=prompt,
                    on_retry=on_retry,
                )
                response = normalize_persona_response(raw)
            except LLMProviderError as exc:
                error_code, usage = exc.error_code, exc.usage
            except ValueError:
                error_code = "MALFORMED_PROVIDER_OUTPUT"
            except Exception:
                error_code = "UNEXPECTED_ENGINE_ERROR"

            outcome: PersonaResponse | PersonaFailure
            if response is not None:
                outcome = response
                await safe_emit(
                    on_event,
                    "persona_completed",
                    persona_index=index,
                    persona_name=persona.name,
                    attempt=attempt,
                    duration_ms=_elapsed_ms(persona_started),
                    input_tokens=usage.input_tokens,
                    output_tokens=usage.output_tokens,
                )
            else:
                outcome = PersonaFailure(
                    persona_name=persona.name, error_code=error_code
                )
                await safe_emit(
                    on_event,
                    "persona_failed",
                    persona_index=index,
                    persona_name=persona.name,
                    attempt=attempt,
                    error_code=error_code,
                    duration_ms=_elapsed_ms(persona_started),
                    input_tokens=usage.input_tokens,
                    output_tokens=usage.output_tokens,
                )
            return persona, outcome, usage

    tasks = [
        asyncio.create_task(_run_persona(index, persona))
        for index, persona in enumerate(personas)
    ]

    responses: list[PersonaResponse] = []
    failures: list[PersonaFailure] = []
    handoff_pairs: list[tuple[PersonaResponse, dict[str, str]]] = []

    try:
        for task in asyncio.as_completed(tasks):
            persona_name = "unknown"
            try:
                item = await task
            except Exception as exc:  # pragma: no cover - defensive fallback
                item = exc

            persona_blueprint: PersonaBlueprint | None = None
            if isinstance(item, tuple) and len(item) == 3:
                persona_blueprint, result_item, usage = item
                if isinstance(result_item, PersonaResponse):
                    persona_name = result_item.name
                elif isinstance(result_item, PersonaFailure):
                    persona_name = result_item.persona_name
            else:
                result_item, usage = (
                    PersonaFailure(
                        persona_name=persona_name,
                        error_code="UNEXPECTED_ENGINE_ERROR",
                    ),
                    TokenUsage(),
                )

            total_usage += usage

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
                    )
                )
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
        input_tokens=total_usage.input_tokens,
        output_tokens=total_usage.output_tokens,
    )
