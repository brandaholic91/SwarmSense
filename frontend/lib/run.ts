import { backendFetch, isRunId } from "@/lib/backend";
import type { Price } from "@/lib/cost";

export type RunStatus = "queued" | "running" | "composing" | "completed" | "partial" | "failed";

export type RunSynthesis = {
  summary: string;
  main_barriers: string[];
  winning_conditions: string;
  best_target_segment: string;
  strategic_recommendation: string;
};

// A backend `_build_result_payload` kimenetének az oldalnak szükséges része.
export type RunResult = {
  completed_persona_count: number;
  total_persona_count: number;
  stance_counts: { support: number; reject: number; conditional: number };
  synthesis: RunSynthesis | null;
  failed_personas: { name: string; error_code: string }[];
  personas?: unknown[];
};

export type RunDetail = {
  run_id: string;
  status: RunStatus;
  is_sample: boolean;
  topic: string;
  audience: string;
  created_at: string;
  completed_at: string | null;
  duration_ms: number | null;
  input_tokens: number;
  output_tokens: number;
  retry_count: number;
  price: Price;
  result: RunResult | null;
  emails_remaining: number;
};

// Csak szerveroldalon használható. `null`: nincs ilyen futás (404 vagy nem UUID);
// más hibánál dob, így az oldal hibaoldalra fut, nem "nincs ilyen futás"-ra.
export async function fetchRun(id: string): Promise<RunDetail | null> {
  if (!isRunId(id)) return null;
  const response = await backendFetch(`/api/v1/runs/${id}`);
  if (response.status === 404) return null;
  if (!response.ok) {
    throw new Error(`run detail request failed with status ${response.status}`);
  }
  return (await response.json()) as RunDetail;
}

// Csak szerveroldalon használható. `null`: nincs mintafutás (404); más hibánál dob.
export async function fetchSampleRunId(): Promise<string | null> {
  const response = await backendFetch("/api/v1/runs/sample");
  if (response.status === 404) return null;
  if (!response.ok) {
    throw new Error(`sample request failed with status ${response.status}`);
  }
  const body = (await response.json()) as { run_id: string };
  return body.run_id;
}
