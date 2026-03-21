const getCookieMock = vi.fn();

vi.mock("next/headers", () => ({
  cookies: async () => ({
    get: (name: string) => getCookieMock(name),
  }),
}));

import { startRunAction } from "@/app/actions/start-run";

describe("startRunAction", () => {
  const originalApiUrl = process.env.API_URL;
  const originalInternalSecret = process.env.INTERNAL_SECRET;

  beforeEach(() => {
    process.env.API_URL = "http://localhost:8000";
    process.env.INTERNAL_SECRET = "test-secret";
    vi.restoreAllMocks();
    getCookieMock.mockReset();
  });

  afterAll(() => {
    process.env.API_URL = originalApiUrl;
    process.env.INTERNAL_SECRET = originalInternalSecret;
  });

  it("posts /run-sessions with combined payload and auth header", async () => {
    getCookieMock.mockImplementation((name: string) => {
      if (name === "swarmsense_verified_user") {
        return { value: "user-11" };
      }
      if (name === "swarmsense_run_context") {
        return { value: JSON.stringify({ topic: "Pricing", audience: "SMB CFOs" }) };
      }
      return undefined;
    });

    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          run_id: "run-11",
          status: "queued",
          created_at: "2026-03-21T11:00:00Z",
        }),
        { status: 200 }
      )
    );

    const result = await startRunAction({
      role_answer: "founder_ceo",
      use_case_answer: "message_validation",
    });

    expect(result).toEqual({ ok: true, run_id: "run-11" });
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/run-sessions",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({ "X-Internal-Secret": "test-secret" }),
      })
    );
  });

  it("maps backend 402 code to failure contract", async () => {
    getCookieMock.mockImplementation((name: string) => {
      if (name === "swarmsense_verified_user") {
        return { value: "user-11" };
      }
      if (name === "swarmsense_run_context") {
        return { value: JSON.stringify({ topic: "Pricing", audience: "SMB CFOs" }) };
      }
      return undefined;
    });

    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          detail: "A havi ingyenes kapacitás elérte a határát.",
          code: "COST_LIMIT_REACHED",
        }),
        { status: 402 }
      )
    );

    const result = await startRunAction({
      role_answer: "founder_ceo",
      use_case_answer: "message_validation",
    });

    expect(result).toEqual({
      ok: false,
      code: "COST_LIMIT_REACHED",
      detail: "A havi ingyenes kapacitás elérte a határát.",
    });
  });

  it("returns RUN_CONTEXT_MISSING when context cookies are unavailable", async () => {
    getCookieMock.mockReturnValue(undefined);

    const result = await startRunAction({
      role_answer: "founder_ceo",
      use_case_answer: "message_validation",
    });

    expect(result).toEqual({
      ok: false,
      code: "RUN_CONTEXT_MISSING",
      detail: "Run context is missing",
    });
  });

  it("throws when INTERNAL_SECRET is not configured", async () => {
    delete process.env.INTERNAL_SECRET;

    getCookieMock.mockReturnValue(undefined);

    await expect(
      startRunAction({ role_answer: "founder_ceo", use_case_answer: "message_validation" })
    ).rejects.toThrow("INTERNAL_SECRET is not configured");
  });
});
