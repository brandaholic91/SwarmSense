from __future__ import annotations

from app.models.persona import PersonaBlueprint
from app.services.llm_client import LLMClient, LLMProviderError, TokenUsage

BLUEPRINT_SYSTEM_PROMPT = (
    "Te egy tapasztalt kutatási szakértő vagy, aki szintetikus persona profilokat készít. "
    "Kizárólag magyar nyelven válaszolj. "
    "A válasz legyen nyers JSON objektum a kért kulcsokkal, extra mezők nélkül. "
    "Ne használj markdown formázást, kód-blokkot vagy ```json jelölést — "
    "csak a nyers JSON objektumot add vissza."
)

BLUEPRINT_TEMPERATURE = 0.7


class BlueprintGenerationError(Exception):
    """A persona-leírások generálása elbukott.

    Szándékosan nincs benne szolgáltatói vagy LLM-szöveg, és a kivétellánc sem
    viszi tovább. A `usage` a hívás tokenje, ha a szolgáltató válaszolt.
    """

    def __init__(self, usage: TokenUsage | None = None) -> None:
        super().__init__("persona blueprint generation failed")
        self.usage = usage or TokenUsage()


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
    try:
        raw, usage = await llm_client.generate_json(
            system_prompt=BLUEPRINT_SYSTEM_PROMPT,
            user_prompt=prompt,
            temperature=BLUEPRINT_TEMPERATURE,
        )
    except LLMProviderError as exc:
        raise BlueprintGenerationError(usage=exc.usage) from None

    personas_raw = raw.get("personas")
    # a modell néha többet ad a kértnél: a felesleget levágjuk, a hiányt nem pótoljuk
    if not isinstance(personas_raw, list) or len(personas_raw) < count:
        raise BlueprintGenerationError()

    try:
        blueprints = [
            PersonaBlueprint.model_validate(item) for item in personas_raw[:count]
        ]
    except ValueError:  # a pydantic ValidationError is ValueError
        raise BlueprintGenerationError() from None
    return blueprints, usage
