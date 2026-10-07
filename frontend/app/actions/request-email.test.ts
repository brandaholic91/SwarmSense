import type { MockInstance } from "vitest";

import { requestEmailAction } from "@/app/actions/request-email";

const RUN_ID = "3f1c2a52-8a54-4c3e-9d57-0a6c6f9b1e11";
const EMAIL = "reader@example.com";

describe("requestEmailAction", () => {
  const originalApiUrl = process.env.API_URL;
  const originalInternalSecret = process.env.INTERNAL_SECRET;
  let fetchMock: MockInstance<typeof fetch>;

  beforeEach(() => {
    process.env.API_URL = "http://backend:8000";
    process.env.INTERNAL_SECRET = "s3cret";
    fetchMock = vi.spyOn(global, "fetch");
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  afterAll(() => {
    if (originalApiUrl === undefined) delete process.env.API_URL;
    else process.env.API_URL = originalApiUrl;
    if (originalInternalSecret === undefined) delete process.env.INTERNAL_SECRET;
    else process.env.INTERNAL_SECRET = originalInternalSecret;
  });

  it("posts the trimmed address with the internal secret and returns the remaining count", async () => {
    fetchMock.mockResolvedValue(
      new Response(JSON.stringify({ status: "sent", emails_remaining: 2 }), { status: 200 })
    );

    const result = await requestEmailAction({ runId: RUN_ID, email: `  ${EMAIL} ` });

    expect(result).toEqual({ ok: true, emailsRemaining: 2 });
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe(`http://backend:8000/api/v1/runs/${RUN_ID}/email`);
    expect(init.method).toBe("POST");
    expect(new Headers(init.headers).get("X-Internal-Secret")).toBe("s3cret");
    expect(JSON.parse(init.body as string)).toEqual({ email: EMAIL });
  });

  it("passes the backend error code through unchanged", async () => {
    fetchMock.mockResolvedValue(
      new Response(JSON.stringify({ code: "EMAIL_RUN_LIMIT_REACHED" }), { status: 429 })
    );

    await expect(requestEmailAction({ runId: RUN_ID, email: EMAIL })).resolves.toEqual({
      ok: false,
      code: "EMAIL_RUN_LIMIT_REACHED",
    });
  });

  it("returns INVALID_EMAIL without calling the backend for a non-UUID run id or empty address", async () => {
    await expect(requestEmailAction({ runId: "nem-uuid", email: EMAIL })).resolves.toEqual({
      ok: false,
      code: "INVALID_EMAIL",
    });
    await expect(requestEmailAction({ runId: RUN_ID, email: "   " })).resolves.toEqual({
      ok: false,
      code: "INVALID_EMAIL",
    });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("returns EMAIL_SEND_FAILED when fetch throws", async () => {
    fetchMock.mockRejectedValue(new TypeError("fetch failed"));

    await expect(requestEmailAction({ runId: RUN_ID, email: EMAIL })).resolves.toEqual({
      ok: false,
      code: "EMAIL_SEND_FAILED",
    });
  });

  it("returns EMAIL_SEND_FAILED for a non-JSON error or a success without a count", async () => {
    fetchMock.mockResolvedValueOnce(new Response("<html>", { status: 500 }));
    await expect(requestEmailAction({ runId: RUN_ID, email: EMAIL })).resolves.toEqual({
      ok: false,
      code: "EMAIL_SEND_FAILED",
    });

    fetchMock.mockResolvedValueOnce(new Response("{}", { status: 200 }));
    await expect(requestEmailAction({ runId: RUN_ID, email: EMAIL })).resolves.toEqual({
      ok: false,
      code: "EMAIL_SEND_FAILED",
    });
  });
});
