from __future__ import annotations

import asyncio
from typing import Any

from pydantic import ValidationError

from app.models.persona import (
    PersonaBlueprint,
    PersonaFailure,
    PersonaResponse,
    PersonaRunResult,
)
from app.services.llm_client import LLMProviderError, OpenRouterClient

DEFAULT_PERSONA_COUNT = 18
MIN_PERSONA_COUNT = 15
MAX_PERSONA_COUNT = 20

HUNGARIAN_SYSTEM_PROMPT = (
    "Te egy magyar piacismerettel rendelkezo strategiai szemelyiseg vagy. "
    "Kizarlag magyar nyelven valaszolj. "
    "A valasz legyen pontos JSON objektum a kert kulcsokkal, extra mezok nelkul."
)

HUNGARIAN_MARKET_CONTEXT = (
    "Fokuszalj magyarorszagi vallalati valosagra, helyi vasarloi viselkedesre, "
    "magyar piaci sajatossagokra, es magyar uzleti nyelvezetre."
)

PERSONA_BLUEPRINT_DEFINITIONS: tuple[dict[str, str], ...] = (
    {
        "name": "Tibor, kockazatkerulo penzugyi igazgato",
        "role": "CFO",
        "risk_appetite": "alacsony",
        "decision_style": "adat- es bizonyitek alapu",
        "organizational_role": "penzugyi donteshozo",
        "price_sensitivity": "magas",
        "technology_adoption_curve": "kesoi tobbseg",
    },
    {
        "name": "Nora, opportunista growth vezeto",
        "role": "Growth Lead",
        "risk_appetite": "magas",
        "decision_style": "kiserletezo es gyors",
        "organizational_role": "novekedesi vezeto",
        "price_sensitivity": "kozepes",
        "technology_adoption_curve": "korai alkalmazo",
    },
    {
        "name": "Miklos, skeptikus operations manager",
        "role": "Operations Manager",
        "risk_appetite": "alacsony",
        "decision_style": "folyamatfegyelmet koveto",
        "organizational_role": "mukodesi vezeto",
        "price_sensitivity": "kozepes",
        "technology_adoption_curve": "kesoi tobbseg",
    },
    {
        "name": "Eszter, innovator termekvezeto",
        "role": "Product Lead",
        "risk_appetite": "kozepesen magas",
        "decision_style": "hipotezis-driven",
        "organizational_role": "termekdonteshozo",
        "price_sensitivity": "kozepes",
        "technology_adoption_curve": "innovator",
    },
    {
        "name": "Gergo, konzervativ IT-vezeto",
        "role": "Head of IT",
        "risk_appetite": "alacsony",
        "decision_style": "biztonsag-kozpontu",
        "organizational_role": "technologiai kapuor",
        "price_sensitivity": "alacsony",
        "technology_adoption_curve": "kesoi alkalmazo",
    },
    {
        "name": "Zsofia, ugyfelhangra erzekeny marketingvezeto",
        "role": "Marketing Director",
        "risk_appetite": "kozepes",
        "decision_style": "kutatasra tamaszkodo",
        "organizational_role": "marketing donteshozo",
        "price_sensitivity": "kozepesen magas",
        "technology_adoption_curve": "korai tobbseg",
    },
    {
        "name": "Bence, ROI-maximalo alapito",
        "role": "Founder",
        "risk_appetite": "kozepesen magas",
        "decision_style": "eredmeny-kozpontu",
        "organizational_role": "vegso donteshozo",
        "price_sensitivity": "magas",
        "technology_adoption_curve": "korai alkalmazo",
    },
    {
        "name": "Judit, compliance-fokuszu jogi vezeto",
        "role": "Legal Lead",
        "risk_appetite": "nagyon alacsony",
        "decision_style": "szabalyozas-koveto",
        "organizational_role": "jogi kontroll",
        "price_sensitivity": "kozepes",
        "technology_adoption_curve": "kesoi tobbseg",
    },
    {
        "name": "Aron, adatorientalt revenue ops manager",
        "role": "RevOps Manager",
        "risk_appetite": "kozepes",
        "decision_style": "metrika-kozpontu",
        "organizational_role": "beveteli folyamatfelelos",
        "price_sensitivity": "kozepes",
        "technology_adoption_curve": "korai tobbseg",
    },
    {
        "name": "Kata, munkaerohianyra reagalo HR vezeto",
        "role": "HR Director",
        "risk_appetite": "kozepes",
        "decision_style": "emberkozpontu",
        "organizational_role": "szervezeti tamogato",
        "price_sensitivity": "magas",
        "technology_adoption_curve": "korai tobbseg",
    },
    {
        "name": "Levente, skalahato rendszert kereso CTO",
        "role": "CTO",
        "risk_appetite": "kozepesen magas",
        "decision_style": "technikai trade-off alapu",
        "organizational_role": "technologiai vezeto",
        "price_sensitivity": "alacsony",
        "technology_adoption_curve": "innovator",
    },
    {
        "name": "Melinda, diszkontkereso beszerzesi menedzser",
        "role": "Procurement Manager",
        "risk_appetite": "alacsony",
        "decision_style": "alkuorientalt",
        "organizational_role": "beszerzesi donteshozo",
        "price_sensitivity": "nagyon magas",
        "technology_adoption_curve": "kesoi tobbseg",
    },
    {
        "name": "David, adatvedelemre erzekeny IT-biztonsagi vezeto",
        "role": "Security Lead",
        "risk_appetite": "nagyon alacsony",
        "decision_style": "kockazatminimalizalo",
        "organizational_role": "biztonsagi kontroll",
        "price_sensitivity": "alacsony",
        "technology_adoption_curve": "korai tobbseg",
    },
    {
        "name": "Reka, gyors piacra lepest szorgalmazo sales vezeto",
        "role": "Sales Director",
        "risk_appetite": "magas",
        "decision_style": "ugyfelszerzesi sebesseg alapu",
        "organizational_role": "beveteli hajtoero",
        "price_sensitivity": "kozepes",
        "technology_adoption_curve": "korai alkalmazo",
    },
    {
        "name": "Tamas, cashflow-fokuszu KKV ugyvezeto",
        "role": "Managing Director",
        "risk_appetite": "alacsony",
        "decision_style": "likviditasi fegyelem",
        "organizational_role": "kkv tulajdonos",
        "price_sensitivity": "nagyon magas",
        "technology_adoption_curve": "kesoi alkalmazo",
    },
    {
        "name": "Szilvia, adatminosegre koncentralo BI szakerto",
        "role": "BI Manager",
        "risk_appetite": "kozepes",
        "decision_style": "elemzes-kozpontu",
        "organizational_role": "adatgazda",
        "price_sensitivity": "kozepes",
        "technology_adoption_curve": "korai tobbseg",
    },
    {
        "name": "Gabor, partnerkapcsolatra epito channel manager",
        "role": "Channel Manager",
        "risk_appetite": "kozepes",
        "decision_style": "kapcsolat- es bizalom alapu",
        "organizational_role": "partneri novekedes felelos",
        "price_sensitivity": "kozepesen magas",
        "technology_adoption_curve": "korai tobbseg",
    },
    {
        "name": "Anita, ugyfelmegtartast priorizalo customer success vezeto",
        "role": "Customer Success Lead",
        "risk_appetite": "kozepes",
        "decision_style": "lemorzsolodas-csokkento",
        "organizational_role": "ugyfelkapcsolati vezeto",
        "price_sensitivity": "kozepes",
        "technology_adoption_curve": "korai tobbseg",
    },
)


def build_persona_blueprints(
    total_personas: int = DEFAULT_PERSONA_COUNT,
) -> list[PersonaBlueprint]:
    if total_personas < MIN_PERSONA_COUNT or total_personas > MAX_PERSONA_COUNT:
        raise ValueError(
            f"A szemelyisegek szama csak {MIN_PERSONA_COUNT}-{MAX_PERSONA_COUNT} lehet."
        )
    if total_personas > len(PERSONA_BLUEPRINT_DEFINITIONS):
        raise ValueError(
            f"Nincs eleg szemelyiseg-definicio: {total_personas} kert, "
            f"{len(PERSONA_BLUEPRINT_DEFINITIONS)} elerheto."
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
        "Keszits velemenyt a kovetkezo kutatasi kerdesrol, a megadott szemelyiseg nezetebol.\n"
        f"Kutatasi tema: {topic}\n"
        f"Celkozonseg: {audience}\n"
        "Szemelyiseg parameterei:\n"
        f"- Nev: {persona.name}\n"
        f"- Szervezeti szerep: {persona.organizational_role}\n"
        f"- Donto szerep: {persona.role}\n"
        f"- Kockazatvallalasi hajlandosag: {persona.risk_appetite}\n"
        f"- Dontesi stilus: {persona.decision_style}\n"
        f"- Arerzekenyseg: {persona.price_sensitivity}\n"
        f"- Technologiai adoptacio: {persona.technology_adoption_curve}\n"
        f"Piaci keret: {HUNGARIAN_MARKET_CONTEXT}\n"
        "Valaszolj JSON objektummal pontosan ezekkel a kulcsokkal:\n"
        "name, role, stance, primary_argument, change_condition\n"
        "A stance erteke kizarolag: support | reject | conditional"
    )


def normalize_persona_response(payload: dict[str, Any]) -> PersonaResponse:
    try:
        return PersonaResponse.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(
            "A provider valasz nem felel meg az elvart schema-nak."
        ) from exc


async def execute_persona_engine(
    *,
    topic: str,
    audience: str,
    llm_client: OpenRouterClient | None = None,
    concurrency_limit: int = 5,
    total_personas: int = DEFAULT_PERSONA_COUNT,
) -> PersonaRunResult:
    client = llm_client or OpenRouterClient()
    personas = build_persona_blueprints(total_personas)
    semaphore = asyncio.Semaphore(concurrency_limit)

    async def _run_persona(
        persona: PersonaBlueprint,
    ) -> PersonaResponse | PersonaFailure:
        async with semaphore:
            prompt = build_persona_user_prompt(
                persona=persona, topic=topic, audience=audience
            )
            try:
                raw = await client.generate_persona_response(
                    system_prompt=HUNGARIAN_SYSTEM_PROMPT,
                    user_prompt=prompt,
                )
                return normalize_persona_response(raw)
            except LLMProviderError as exc:
                return PersonaFailure(
                    persona_name=persona.name,
                    error_code=exc.error_code,
                    error_message=str(exc),
                )
            except ValueError as exc:
                return PersonaFailure(
                    persona_name=persona.name,
                    error_code="MALFORMED_PROVIDER_OUTPUT",
                    error_message=str(exc),
                )

    gathered = await asyncio.gather(
        *[_run_persona(persona) for persona in personas], return_exceptions=True
    )

    responses: list[PersonaResponse] = []
    failures: list[PersonaFailure] = []
    for persona, item in zip(personas, gathered):
        if isinstance(item, PersonaResponse):
            responses.append(item)
        elif isinstance(item, PersonaFailure):
            failures.append(item)
        else:
            failures.append(
                PersonaFailure(
                    persona_name=persona.name,
                    error_code="UNEXPECTED_ENGINE_ERROR",
                    error_message=str(item),
                )
            )

    handoff_payload = [response.model_dump() for response in responses]

    return PersonaRunResult(
        total_personas=len(personas),
        successful_count=len(responses),
        responses=responses,
        failures=failures,
        handoff_payload=handoff_payload,
    )
