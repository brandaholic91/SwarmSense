export const TOTAL_PERSONAS = 18;
export const MAX_ATTEMPTS = 3;

export type TraceEvent = {
  id: number;
  type: string;
  at: string;
  persona_index?: number;
  persona_name?: string;
  attempt?: number;
  error_code?: string;
  duration_ms?: number;
  input_tokens?: number;
  output_tokens?: number;
};

export type PersonaRow = {
  index: number;
  name: string;
  status: "running" | "completed" | "failed" | "interrupted";
  attempt: number;
  startedAt: string;
  durationMs: number | null;
  errorCode: string | null;
  // A persona saját hívásának tokenjei: 0, amíg a sor fut; a lezáró esemény
  // (persona_completed / persona_failed) hozza az értéket.
  inputTokens: number;
  outputTokens: number;
};

export type TracePhase =
  | "waiting"
  | "generating"
  | "personas"
  | "synthesis"
  | "pdf"
  | "done"
  | "failed";

export type TraceState = {
  lastEventId: number;
  phase: TracePhase;
  startedAt: string | null;
  endedAt: string | null;
  personas: PersonaRow[]; // persona_index szerint rendezve
  inputTokens: number;
  outputTokens: number;
  retryCount: number;
  synthesisFailed: boolean;
  failureCode: string | null;
};

export function initialTraceState(): TraceState {
  return {
    lastEventId: 0,
    phase: "waiting",
    startedAt: null,
    endedAt: null,
    personas: [],
    inputTokens: 0,
    outputTokens: 0,
    retryCount: 0,
    synthesisFailed: false,
    failureCode: null,
  };
}

// Tiszta: nem módosítja a bemenetet. Az id <= lastEventId esemény figyelmen kívül marad,
// így ugyanaz az eseménysor többször lejátszva sem duplázza az összegeket.
export function applyEvent(state: TraceState, event: TraceEvent): TraceState {
  if (event.id <= state.lastEventId) return state;

  const next: TraceState = { ...state, lastEventId: event.id };
  const withTokens = (s: TraceState): TraceState => ({
    ...s,
    inputTokens: s.inputTokens + (event.input_tokens ?? 0),
    outputTokens: s.outputTokens + (event.output_tokens ?? 0),
  });
  const updateRow = (change: (row: PersonaRow) => PersonaRow): PersonaRow[] =>
    next.personas.map((row) => (row.index === event.persona_index ? change(row) : row));

  switch (event.type) {
    case "run_started":
      return { ...next, phase: "generating", startedAt: event.at };
    case "personas_generated":
      return withTokens({ ...next, phase: "personas" });
    case "persona_started": {
      const row: PersonaRow = {
        index: event.persona_index ?? next.personas.length,
        name: event.persona_name ?? "",
        status: "running",
        attempt: 1,
        startedAt: event.at,
        durationMs: null,
        errorCode: null,
        inputTokens: 0,
        outputTokens: 0,
      };
      const personas = [...next.personas.filter((r) => r.index !== row.index), row].sort(
        (a, b) => a.index - b.index
      );
      return { ...next, personas };
    }
    case "persona_retry":
      return {
        ...next,
        retryCount: next.retryCount + 1,
        personas: updateRow((row) => ({
          ...row,
          attempt: event.attempt ?? row.attempt,
          errorCode: event.error_code ?? null,
        })),
      };
    case "persona_completed":
      return withTokens({
        ...next,
        personas: updateRow((row) => ({
          ...row,
          status: "completed",
          durationMs: event.duration_ms ?? null,
          attempt: event.attempt ?? row.attempt,
          errorCode: null,
          inputTokens: event.input_tokens ?? 0,
          outputTokens: event.output_tokens ?? 0,
        })),
      });
    case "persona_failed":
      return withTokens({
        ...next,
        personas: updateRow((row) => ({
          ...row,
          status: "failed",
          durationMs: event.duration_ms ?? null,
          attempt: event.attempt ?? row.attempt,
          errorCode: event.error_code ?? null,
          inputTokens: event.input_tokens ?? 0,
          outputTokens: event.output_tokens ?? 0,
        })),
      });
    case "synthesis_started":
      return { ...next, phase: "synthesis" };
    case "synthesis_completed":
      return withTokens({ ...next, phase: "pdf" });
    case "synthesis_failed":
      // A sikertelen hívás tokenjei is elfogytak, ezért ugyanúgy számítanak.
      return withTokens({ ...next, phase: "pdf", synthesisFailed: true });
    case "run_completed":
      return { ...next, phase: "done", endedAt: event.at };
    case "run_failed":
      return {
        ...next,
        phase: "failed",
        endedAt: event.at,
        failureCode: event.error_code ?? null,
        // A lezárt futásban nem maradhat „fut” sor, és az órája sem járhat tovább.
        personas: next.personas.map((row) =>
          row.status === "running"
            ? {
                ...row,
                status: "interrupted",
                durationMs: Math.max(0, Date.parse(event.at) - Date.parse(row.startedAt)),
              }
            : row
        ),
      };
    default:
      return next;
  }
}

export function countByStatus(state: TraceState): {
  queued: number;
  running: number;
  completed: number;
  failed: number;
  interrupted: number;
} {
  const count = (status: PersonaRow["status"]) =>
    state.personas.filter((row) => row.status === status).length;
  return {
    queued: state.phase === "personas" ? TOTAL_PERSONAS - state.personas.length : 0,
    running: count("running"),
    completed: count("completed"),
    failed: count("failed"),
    interrupted: count("interrupted"),
  };
}
