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

type RunSessionResponse = {
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

  const internalSecret = process.env.INTERNAL_SECRET;
  if (!internalSecret) {
    throw new Error("INTERNAL_SECRET is not configured");
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

  const response = await fetch(`${apiUrl}/api/v1/run-sessions`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "X-Internal-Secret": internalSecret,
    },
    body: JSON.stringify({
      user_id: userId,
      topic: runContext.topic,
      audience: runContext.audience,
      role_answer: role_answer.trim(),
      use_case_answer: use_case_answer.trim(),
    }),
    cache: "no-store",
  });

  if (!response.ok) {
    const errorPayload = (await response.json().catch(() => null)) as ErrorResponse | null;
    return {
      ok: false,
      code: errorPayload?.code ?? "RUN_START_FAILED",
      detail: errorPayload?.detail ?? "Failed to start run",
    };
  }

  const data = (await response.json()) as RunSessionResponse;
  if (!data.run_id || typeof data.run_id !== "string") {
    return {
      ok: false,
      code: "RUN_START_FAILED",
      detail: "Failed to start run",
    };
  }

  return {
    ok: true,
    run_id: data.run_id,
  };
}
