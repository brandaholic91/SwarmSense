"use server";

import { cookies } from "next/headers";

type StartRunInput = {
  role_answer: string;
  use_case_answer: string;
};

type StartRunSuccess = {
  ok: true;
  run_id: string;
};

type StartRunFailure = {
  ok: false;
  code: string;
  detail: string;
};

type RunContext = {
  topic: string;
  audience: string;
};

type RunResponse = {
  run_id: string;
  status: string;
  created_at: string;
};

type ErrorResponse = {
  detail: string;
  code: string;
};

function parseRunContext(raw: string | undefined): RunContext | null {
  if (!raw) {
    return null;
  }

  try {
    const parsed = JSON.parse(raw) as Partial<RunContext>;
    if (
      typeof parsed.topic === "string" &&
      parsed.topic.trim().length > 0 &&
      typeof parsed.audience === "string" &&
      parsed.audience.trim().length > 0
    ) {
      return {
        topic: parsed.topic.trim(),
        audience: parsed.audience.trim(),
      };
    }
    return null;
  } catch {
    return null;
  }
}

export async function startRunAction({
  role_answer,
  use_case_answer,
}: StartRunInput): Promise<StartRunSuccess | StartRunFailure> {
  const apiUrl = process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL;
  if (!apiUrl) {
    throw new Error("API_URL is not configured");
  }

  const cookieStore = await cookies();
  const userId = cookieStore.get("swarmsense_verified_user")?.value;
  const runContext = parseRunContext(cookieStore.get("swarmsense_run_context")?.value);

  if (!userId || !runContext) {
    return {
      ok: false,
      code: "RUN_CONTEXT_MISSING",
      detail: "Run context is missing",
    };
  }

  const runResponse = await fetch(`${apiUrl}/api/v1/runs`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify({
      user_id: userId,
      topic: runContext.topic,
      audience: runContext.audience,
    }),
    cache: "no-store",
  });

  if (!runResponse.ok) {
    const errorPayload = (await runResponse.json().catch(() => null)) as ErrorResponse | null;
    return {
      ok: false,
      code: errorPayload?.code ?? "RUN_START_FAILED",
      detail: errorPayload?.detail ?? "Failed to start run",
    };
  }

  const runData = (await runResponse.json()) as RunResponse;
  const qualifierResponse = await fetch(`${apiUrl}/api/v1/qualifier`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify({
      run_id: runData.run_id,
      user_id: userId,
      role_answer: role_answer.trim(),
      use_case_answer: use_case_answer.trim(),
    }),
    cache: "no-store",
  });

  if (!qualifierResponse.ok) {
    const errorPayload = (await qualifierResponse.json().catch(() => null)) as ErrorResponse | null;
    return {
      ok: false,
      code: errorPayload?.code ?? "QUALIFIER_SAVE_FAILED",
      detail: errorPayload?.detail ?? "Failed to save qualifier",
    };
  }

  return {
    ok: true,
    run_id: runData.run_id,
  };
}
