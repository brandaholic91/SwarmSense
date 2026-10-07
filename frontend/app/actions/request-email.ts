"use server";

import { backendFetch, isRunId } from "@/lib/backend";

type RequestEmailInput = {
  runId: string;
  email: string;
};

type RequestEmailResult =
  | { ok: true; emailsRemaining: number }
  | { ok: false; code: string };

// Soha nem dob: a hívó (böngésző) mindig egy hibakódot kap, nyers hibaüzenetet nem.
// A címet csak a backend érvényesíti; itt az üres és a nem UUID értéket szűrjük ki.
export async function requestEmailAction(input: RequestEmailInput): Promise<RequestEmailResult> {
  try {
    const runId = String(input.runId ?? "");
    const email = String(input.email ?? "").trim();
    if (!isRunId(runId) || email.length === 0) {
      return { ok: false, code: "INVALID_EMAIL" };
    }

    const response = await backendFetch(`/api/v1/runs/${runId}/email`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ email }),
      // a backend PDF-et is generálhat és levelet küld: hosszabb időkorlát, mint az alap
      timeoutMs: 60_000,
    });

    if (!response.ok) {
      const payload = (await response.json().catch(() => null)) as { code?: unknown } | null;
      const code = typeof payload?.code === "string" ? payload.code : "EMAIL_SEND_FAILED";
      return { ok: false, code };
    }

    const data = (await response.json()) as { emails_remaining?: unknown };
    if (typeof data.emails_remaining !== "number") {
      return { ok: false, code: "EMAIL_SEND_FAILED" };
    }
    return { ok: true, emailsRemaining: data.emails_remaining };
  } catch {
    return { ok: false, code: "EMAIL_SEND_FAILED" };
  }
}
