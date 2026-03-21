from __future__ import annotations

from pydantic import ValidationError

from app.models.persona import PersonaResponse, SynthesisResult
from app.services.llm_client import LLMProviderError, OpenRouterClient

SYNTHESIS_SYSTEM_PROMPT = (
    "Te egy tapasztalt magyar üzleti stratega vagy. "
    "Kizarólag magyar nyelven válaszolj. "
    "A válasz legyen pontos JSON objektum a kért kulcsokkal, extra mezők nélkül."
)


def build_synthesis_user_prompt(
    *,
    personas: list[PersonaResponse],
    topic: str,
    audience: str,
) -> str:
    personas_summary = "\n".join(
        f"- {p.name} ({p.role}): {p.stance} | erv: {p.primary_argument} | "
        f"aggodalom: {p.core_concern} | trigger: {p.buying_trigger}"
        for p in personas
    )
    return (
        f"Szintetikus piackutatás persona-összesítő:\n"
        f"Kutatási téma: {topic}\n"
        f"Célközönség: {audience}\n"
        f"Persona visszajelzések:\n{personas_summary}\n\n"
        "Elemezd az összes persona visszajelzését és azonosítsd az ismétlődő mintákat. "
        "Válaszolj JSON objektummal pontosan ezekkel a kulcsokkal:\n"
        "summary, main_barriers, winning_conditions, best_target_segment, strategic_recommendation\n"
        "Szabályok:\n"
        "- summary: 2-3 mondatos összefoglalás a legfontosabb mintákról és jelzésekről\n"
        "- main_barriers: pontosan 3 elemű lista, minden elem max 10 szó\n"
        "- winning_conditions: 1 mondat max 20 szó, mi kellene a széles elfogadáshoz\n"
        "- best_target_segment: 1 mondat max 20 szó, melyik persona típus a legreceptívebb\n"
        "- strategic_recommendation: 1 mondat max 20 szó, konkrét következő lépés javaslat"
    )


async def execute_synthesis(
    *,
    personas: list[PersonaResponse],
    topic: str,
    audience: str,
    llm_client: OpenRouterClient | None = None,
) -> SynthesisResult:
    client = llm_client or OpenRouterClient()
    prompt = build_synthesis_user_prompt(personas=personas, topic=topic, audience=audience)
    raw, _ = await client.generate_persona_response_with_meta(
        system_prompt=SYNTHESIS_SYSTEM_PROMPT,
        user_prompt=prompt,
    )
    try:
        return SynthesisResult.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(
            "A szintézis válasz nem felel meg az elvárásoknak."
        ) from exc
