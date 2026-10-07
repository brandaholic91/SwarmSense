from __future__ import annotations

from pydantic import ValidationError

from app.models.persona import PersonaBlueprint
from app.services.llm_client import LLMClient, TokenUsage

BLUEPRINT_SYSTEM_PROMPT = (
    "Te egy tapasztalt kutatási szakértő vagy, aki szintetikus persona profilokat készít. "
    "Kizárólag magyar nyelven válaszolj. "
    "A válasz legyen nyers JSON objektum a kért kulcsokkal, extra mezők nélkül. "
    "Ne használj markdown formázást, kód-blokkot vagy ```json jelölést — "
    "csak a nyers JSON objektumot add vissza."
)

BLUEPRINT_TEMPERATURE = 0.7


def build_blueprint_user_prompt(*, topic: str, audience: str, count: int) -> str:
    return (
        f"Kutatási téma: {topic}\n"
        f"Célközönség: {audience}\n\n"
        f"Generálj pontosan {count} különböző személyt, akik hitelesen reprezentálják ezt a célközönséget.\n"
        "A személyek legyenek attitűdben, háttérben és nézőpontban minél változatosabbak — "
        "képviseljék a célközönség belső sokszínűségét (konzervatív és progresszív, "
        "tapasztalt és kezdő, szkeptikus és lelkes stb.).\n\n"
        f"Válaszolj JSON objektummal, amely tartalmaz egy 'personas' kulcsot, "
        f"amelynek értéke pontosan {count} objektumból álló tömb. "
        "Minden objektumban ezek a kulcsok legyenek:\n"
        "name, role, risk_appetite, decision_style, organizational_role, "
        "price_sensitivity, technology_adoption_curve\n\n"
        "Szabályok:\n"
        "- name: teljes név, a célközönség kulturális kontextusának megfelelően\n"
        "- role: szerepkör vagy foglalkozás (max 5 szó)\n"
        "- risk_appetite: az egyik: nagyon alacsony | alacsony | közepes | közepesen magas | magas | nagyon magas\n"
        "- decision_style: döntési vagy gondolkodási stílus (max 6 szó)\n"
        "- organizational_role: funkció vagy pozíció a saját kontextusában (max 6 szó)\n"
        "- price_sensitivity: az egyik: nagyon alacsony | alacsony | közepes | közepesen magas | magas | nagyon magas\n"
        "- technology_adoption_curve: az egyik: innovátor | korai alkalmazó | korai többség | késői többség | késlekedő\n\n"
        "Fontos: a mezők értelmezése legyen a célközönség kontextusának megfelelő "
        "(pl. 'risk_appetite' egy vállalkozónál pénzügyi kockázatot, "
        "egy kutatónál intellektuális merészséget jelent)."
    )


async def generate_persona_blueprints(
    *,
    topic: str,
    audience: str,
    count: int,
    llm_client: LLMClient,
) -> tuple[list[PersonaBlueprint], TokenUsage]:
    prompt = build_blueprint_user_prompt(topic=topic, audience=audience, count=count)
    raw, usage = await llm_client.generate_json(
        system_prompt=BLUEPRINT_SYSTEM_PROMPT,
        user_prompt=prompt,
        temperature=BLUEPRINT_TEMPERATURE,
    )

    personas_raw = raw.get("personas")
    if not isinstance(personas_raw, list):
        raise ValueError(
            "A blueprint generátor nem adott vissza érvényes 'personas' listát."
        )
    if len(personas_raw) == 0:
        raise ValueError("A blueprint generátor üres persona listát adott vissza.")

    try:
        blueprints = [PersonaBlueprint.model_validate(item) for item in personas_raw]
    except ValidationError as exc:
        raise ValueError(
            "A generált persona blueprint nem felel meg az elvárásoknak."
        ) from exc
    return blueprints, usage
