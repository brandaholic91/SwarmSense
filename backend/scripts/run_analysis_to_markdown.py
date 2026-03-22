#!/usr/bin/env python3
"""
Test script: run a full analysis (persona engine + synthesis) and save results as markdown.

Usage:
    cd backend
    python scripts/run_analysis_to_markdown.py \
        --topic "SaaS árazási stratégia" \
        --audience "Magyar KKV pénzügyi vezetők" \
        --out "../docs/analysis-sample.md"
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.persona_engine import execute_persona_engine
from app.services.synthesis_service import execute_synthesis

STANCE_HU = {
    "support": "✅ Támogatja",
    "reject": "❌ Elutasítja",
    "conditional": "⚠️ Feltételes",
}


def to_markdown(topic: str, audience: str, result, synthesis) -> str:
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = []

    lines += [
        f"# SwarmSense elemzés",
        f"",
        f"**Kutatási téma:** {topic}  ",
        f"**Célközönség:** {audience}  ",
        f"**Generálva:** {now}  ",
        f"**Personák:** {result.successful_count}/{result.total_personas}  ",
        f"**Becsült költség:** ${result.cost_usd:.4f}",
        f"",
    ]

    # Stance summary
    stance_counts: dict[str, int] = {"support": 0, "reject": 0, "conditional": 0}
    for r in result.responses:
        stance_counts[r.stance] += 1

    lines += [
        "## Összefoglaló",
        "",
        f"| Álláspont | Darab |",
        f"|-----------|-------|",
        f"| ✅ Támogatja | {stance_counts['support']} |",
        f"| ❌ Elutasítja | {stance_counts['reject']} |",
        f"| ⚠️ Feltételes | {stance_counts['conditional']} |",
        "",
    ]

    # Synthesis
    if synthesis:
        lines += [
            "## Szintézis",
            "",
            f"**Összefoglaló:** {synthesis.summary}",
            "",
            f"**Fő akadályok:**",
        ]
        for barrier in synthesis.main_barriers:
            lines.append(f"- {barrier}")
        lines += [
            "",
            f"**Nyerési feltételek:** {synthesis.winning_conditions}",
            f"",
            f"**Legjobb célszegmens:** {synthesis.best_target_segment}",
            f"",
            f"**Stratégiai ajánlás:** {synthesis.strategic_recommendation}",
            "",
        ]

    # Persona cards
    lines += ["## Persona válaszok", ""]

    for r in result.responses:
        # Find blueprint attrs from handoff_payload
        attrs = next(
            (p for p in result.handoff_payload if p.get("name") == r.name), {}
        )
        stance_label = STANCE_HU.get(r.stance, r.stance)
        lines += [
            f"### {r.name} — {r.role}",
            f"",
            f"**Álláspont:** {stance_label}  ",
        ]
        if attrs.get("risk_appetite"):
            lines.append(
                f"Kockázatvállalás: {attrs['risk_appetite']} · "
                f"Döntési stílus: {attrs.get('decision_style', '–')} · "
                f"Árérzékenység: {attrs.get('price_sensitivity', '–')} · "
                f"Tech adoptáció: {attrs.get('technology_adoption_curve', '–')}  "
            )
        lines += [
            f"",
            f"**Elsődleges érv:** {r.primary_argument}",
            f"",
            f"**Mi változtatná meg:** {r.change_condition}",
            f"",
            f"**Mélyebb aggodalom:** {r.core_concern}",
            f"",
            f"**Vásárlási trigger:** {r.buying_trigger}",
            f"",
            "---",
            "",
        ]

    # Failures (if any)
    if result.failures:
        lines += ["## Hibák", ""]
        for f in result.failures:
            lines.append(f"- **{f.persona_name}** [{f.error_code}]: {f.error_message}")
        lines.append("")

    return "\n".join(lines)


async def main_async(topic: str, audience: str, out: Path) -> None:
    print(f"Persona engine futtatása ({topic} / {audience}) ...")
    result = await execute_persona_engine(topic=topic, audience=audience)
    print(f"  {result.successful_count}/{result.total_personas} persona sikeres, {len(result.failures)} hiba")

    print("Szintézis futtatása ...")
    synthesis = None
    try:
        synthesis = await execute_synthesis(
            personas=result.responses, topic=topic, audience=audience
        )
        print("  Szintézis kész.")
    except Exception as exc:
        print(f"  Szintézis sikertelen (nem fatális): {exc}")

    md = to_markdown(topic=topic, audience=audience, result=result, synthesis=synthesis)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"Eredmény mentve: {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full analysis and save as markdown.")
    parser.add_argument("--topic", default="SaaS árazási stratégia", help="Kutatási téma")
    parser.add_argument("--audience", default="Magyar KKV pénzügyi vezetők", help="Célközönség")
    parser.add_argument(
        "--out",
        default="../docs/analysis-sample.md",
        help="Kimeneti fájl útvonala (alapértelmezett: ../docs/analysis-sample.md)",
    )
    args = parser.parse_args()
    asyncio.run(main_async(topic=args.topic, audience=args.audience, out=Path(args.out).resolve()))


if __name__ == "__main__":
    main()
