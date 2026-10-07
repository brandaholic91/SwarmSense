import type { MockInstance } from "vitest";

import { headers } from "next/headers";

import { startRunAction } from "@/app/actions/start-run";

vi.mock("next/headers", () => ({ headers: vi.fn() }));
const headersMock = vi.mocked(headers);

describe("startRunAction", () => {
  const originalApiUrl = process.env.API_URL;
  const originalInternalSecret = process.env.INTERNAL_SECRET;
  let fetchMock: MockInstance<typeof fetch>;

  beforeEach(() => {
    process.env.API_URL = "http://backend:8000";
    process.env.INTERNAL_SECRET = "s3cret";
    fetchMock = vi.spyOn(global, "fetch");
    headersMock.mockResolvedValue(new Headers() as never);
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

  it("posts trimmed topic and audience with the internal secret", async () => {
    fetchMock.mockResolvedValue(
      new Response(
        JSON.stringify({ run_id: "r-1", status: "queued", created_at: "2026-10-07T12:00:00Z" }),
        { status: 200 }
      )
    );

    const result = await startRunAction({ topic: "  Árazás ", audience: " KKV vezetők " });

    expect(result).toEqual({ ok: true, run_id: "r-1" });
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("http://backend:8000/api/v1/runs");
    expect(new Headers(init.headers).get("X-Internal-Secret")).toBe("s3cret");
    expect(JSON.parse(init.body as string)).toEqual({
      topic: "Árazás",
      audience: "KKV vezetők",
    });
  });

  it("returns the backend error code on failure", async () => {
    fetchMock.mockResolvedValue(
      new Response(JSON.stringify({ detail: "boom", code: "RUN_START_FAILED" }), { status: 500 })
    );

    await expect(startRunAction({ topic: "a", audience: "b" })).resolves.toEqual({
      ok: false,
      code: "RUN_START_FAILED",
    });
  });

  it("maps 422 to INVALID_INPUT", async () => {
    fetchMock.mockResolvedValue(
      new Response(JSON.stringify({ detail: [{ loc: ["body", "topic"], msg: "x" }] }), {
        status: 422,
      })
    );

    await expect(startRunAction({ topic: "a", audience: "b" })).resolves.toEqual({
      ok: false,
      code: "INVALID_INPUT",
    });
  });

  it("returns RUN_START_FAILED when the backend is unreachable", async () => {
    fetchMock.mockRejectedValue(new TypeError("fetch failed"));

    await expect(startRunAction({ topic: "a", audience: "b" })).resolves.toEqual({
      ok: false,
      code: "RUN_START_FAILED",
    });
  });

  it("returns RUN_START_FAILED on a non-JSON or run_id-less response", async () => {
    fetchMock.mockResolvedValueOnce(new Response("<html>", { status: 200 }));
    await expect(startRunAction({ topic: "a", audience: "b" })).resolves.toEqual({
      ok: false,
      code: "RUN_START_FAILED",
    });

    fetchMock.mockResolvedValueOnce(new Response("{}", { status: 200 }));
    await expect(startRunAction({ topic: "a", audience: "b" })).resolves.toEqual({
      ok: false,
      code: "RUN_START_FAILED",
    });
  });

  it("returns INVALID_INPUT without calling the backend for empty or over-500-char input", async () => {
    await expect(startRunAction({ topic: "   ", audience: "b" })).resolves.toEqual({
      ok: false,
      code: "INVALID_INPUT",
    });
    await expect(
      startRunAction({ topic: "x".repeat(501), audience: "b" })
    ).resolves.toEqual({ ok: false, code: "INVALID_INPUT" });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("returns RUN_START_FAILED when API_URL or INTERNAL_SECRET is missing", async () => {
    delete process.env.API_URL;
    await expect(startRunAction({ topic: "a", audience: "b" })).resolves.toEqual({
      ok: false,
      code: "RUN_START_FAILED",
    });

    process.env.API_URL = "http://backend:8000";
    delete process.env.INTERNAL_SECRET;
    await expect(startRunAction({ topic: "a", audience: "b" })).resolves.toEqual({
      ok: false,
      code: "RUN_START_FAILED",
    });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("forwards the first x-forwarded-for address as X-Client-IP", async () => {
    headersMock.mockResolvedValue(
      new Headers({ "x-forwarded-for": "203.0.113.7, 10.0.0.1" }) as never
    );
    fetchMock.mockResolvedValue(new Response(JSON.stringify({ run_id: "r-1" }), { status: 200 }));

    await startRunAction({ topic: "a", audience: "b" });

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(new Headers(init.headers).get("X-Client-IP")).toBe("203.0.113.7");
  });

  it("sends no X-Client-IP without a forwarded header", async () => {
    fetchMock.mockResolvedValue(new Response(JSON.stringify({ run_id: "r-1" }), { status: 200 }));

    await startRunAction({ topic: "a", audience: "b" });

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(new Headers(init.headers).has("X-Client-IP")).toBe(false);
  });

  it("passes a 429 limit code through", async () => {
    fetchMock.mockResolvedValue(
      new Response(JSON.stringify({ code: "DAILY_LIMIT_REACHED" }), { status: 429 })
    );

    await expect(startRunAction({ topic: "a", audience: "b" })).resolves.toEqual({
      ok: false,
      code: "DAILY_LIMIT_REACHED",
    });
  });

  it("returns RUN_START_FAILED for a 500 with a non-JSON body", async () => {
    fetchMock.mockResolvedValue(new Response("<html>oops</html>", { status: 500 }));

    await expect(startRunAction({ topic: "a", audience: "b" })).resolves.toEqual({
      ok: false,
      code: "RUN_START_FAILED",
    });
  });

  it("returns RUN_START_FAILED on a timeout (AbortError)", async () => {
    fetchMock.mockRejectedValue(new DOMException("timed out", "AbortError"));

    await expect(startRunAction({ topic: "a", audience: "b" })).resolves.toEqual({
      ok: false,
      code: "RUN_START_FAILED",
    });
  });
});
