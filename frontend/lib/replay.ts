import type { TraceEvent } from "@/lib/trace";

export type ScheduledEvent = { event: TraceEvent; delayMs: number };

// Az események az `id` sorrendjében, az első eseménytől mért késleltetéssel. Az időben
// visszafelé lépő esemény nem előzheti meg az előzőt, ezért a késleltetés sosem csökken.
export function buildSchedule(events: TraceEvent[]): ScheduledEvent[] {
  const sorted = [...events].sort((a, b) => a.id - b.id);
  if (sorted.length === 0) return [];
  const first = Date.parse(sorted[0].at);
  let previous = 0;
  return sorted.map((event) => {
    const delayMs = Math.max(previous, Date.parse(event.at) - first);
    previous = delayMs;
    return { event, delayMs };
  });
}
