import type { TraceEvent } from "@/lib/trace";

export function ev(id: number, type: string, extra: Partial<TraceEvent> = {}): TraceEvent {
  return { id, type, at: `2026-10-07T12:00:${String(id).padStart(2, "0")}Z`, ...extra };
}

// Egy teljes futás: 18 persona, egy retry-jal (2. persona) és egy kiesővel (5. persona).
export function fullRunEvents(): TraceEvent[] {
  const events: TraceEvent[] = [
    ev(1, "run_started"),
    ev(2, "personas_generated", { input_tokens: 120, output_tokens: 900 }),
  ];
  let id = 3;
  for (let i = 0; i < 18; i++) {
    events.push(ev(id++, "persona_started", { persona_index: i, persona_name: `Persona ${i}` }));
    if (i === 2) {
      events.push(ev(id++, "persona_retry", { persona_index: i, attempt: 2, error_code: "LLM_TIMEOUT" }));
    }
    if (i === 5) {
      events.push(
        ev(id++, "persona_failed", {
          persona_index: i,
          attempt: 3,
          error_code: "INVALID_RESPONSE",
          duration_ms: 4000,
          input_tokens: 10,
          output_tokens: 20,
        })
      );
    } else {
      events.push(
        ev(id++, "persona_completed", {
          persona_index: i,
          attempt: i === 2 ? 2 : 1,
          duration_ms: 2000,
          input_tokens: 100,
          output_tokens: 200,
        })
      );
    }
  }
  events.push(ev(id++, "synthesis_started"));
  events.push(ev(id++, "synthesis_completed", { input_tokens: 500, output_tokens: 300 }));
  events.push(ev(id++, "run_completed"));
  return events;
}

