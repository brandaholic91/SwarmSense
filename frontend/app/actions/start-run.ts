"use server";

import { headers } from "next/headers";

import { backendFetch, clientIp } from "@/lib/backend";

type StartRunInput = {
  topic: string;
  audience: string;
};

type StartRunResult = { ok: true; run_id: string } | { ok: false; code: string };

const MAX_FIELD_LENGTH = 500;

function isValidField(value: string): boolean {
  return value.length > 0 && value.length <= MAX_FIELD_LENGTH;
}

// Soha nem dob: a hívó (böngésző) mindig egy hibakódot kap, nyers hibaüzenetet nem.
export async function startRunAction(input: StartRunInput): Promise<StartRunResult> {
  try {
    const topic = String(input.topic ?? "").trim();
    const audience = String(input.audience ?? "").trim();
    if (!isValidField(topic) || !isValidField(audience)) {
      return { ok: false, code: "INVALID_INPUT" };
    }

    const forwardedFor = clientIp(await headers());
    const response = await backendFetch("/api/v1/runs", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        ...(forwardedFor ? { "X-Client-IP": forwardedFor } : {}),
      },
      body: JSON.stringify({ topic, audience }),
    });

    if (!response.ok) {
      if (response.status === 422) {
        return { ok: false, code: "INVALID_INPUT" };
      }
      const payload = (await response.json().catch(() => null)) as { code?: unknown } | null;
      const code = typeof payload?.code === "string" ? payload.code : "RUN_START_FAILED";
      return { ok: false, code };
    }

    const data = (await response.json()) as { run_id?: unknown };
    if (typeof data.run_id !== "string" || data.run_id.length === 0) {
      return { ok: false, code: "RUN_START_FAILED" };
    }

    return { ok: true, run_id: data.run_id };
  } catch {
    return { ok: false, code: "RUN_START_FAILED" };
  }
}
