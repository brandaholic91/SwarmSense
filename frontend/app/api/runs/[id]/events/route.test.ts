import type { MockInstance } from "vitest";

import { GET } from "@/app/api/runs/[id]/events/route";

const RUN_ID = "3f1c2a52-8a54-4c3e-9d57-0a6c6f9b1e11";

function call(id: string, query = "") {
  return GET(new Request(`http://localhost:3000/api/runs/${id}/events${query}`), {
    params: Promise.resolve({ id }),
  });
}

describe("GET /api/runs/[id]/events", () => {
  const originalApiUrl = process.env.API_URL;
  const originalSecret = process.env.INTERNAL_SECRET;
  let fetchMock: MockInstance<typeof fetch>;

  beforeEach(() => {
    process.env.API_URL = "http://backend.test";
    process.env.INTERNAL_SECRET = "s3cret";
    fetchMock = vi.spyOn(global, "fetch");
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  afterAll(() => {
    if (originalApiUrl === undefined) delete process.env.API_URL;
    else process.env.API_URL = originalApiUrl;
    if (originalSecret === undefined) delete process.env.INTERNAL_SECRET;
    else process.env.INTERNAL_SECRET = originalSecret;
  });

  it("proxies the backend body and status (200) with the internal secret", async () => {
    const body = { status: "running", events: [{ id: 42, type: "run_started", at: "x" }] };
    fetchMock.mockResolvedValue(new Response(JSON.stringify(body), { status: 200 }));

    const response = await call(RUN_ID, "?after=41");

    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe(`http://backend.test/api/v1/runs/${RUN_ID}/events?after=41`);
    expect(new Headers(init.headers).get("X-Internal-Secret")).toBe("s3cret");
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual(body);
    expect(response.headers.get("Cache-Control")).toBe("no-store");
  });

  it("proxies a backend 404 unchanged", async () => {
    fetchMock.mockResolvedValue(
      new Response(JSON.stringify({ code: "RUN_NOT_FOUND" }), { status: 404 })
    );

    const response = await call(RUN_ID, "?after=0");

    expect(response.status).toBe(404);
    expect(await response.json()).toEqual({ code: "RUN_NOT_FOUND" });
    expect(response.headers.get("Cache-Control")).toBe("no-store");
  });

  it("answers 404 RUN_NOT_FOUND for a non-UUID id without calling the backend", async () => {
    const response = await call("not-a-uuid");

    expect(response.status).toBe(404);
    expect(await response.json()).toEqual({ code: "RUN_NOT_FOUND" });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("defaults a missing after to 0", async () => {
    fetchMock.mockResolvedValue(new Response("{}", { status: 200 }));

    await call(RUN_ID);

    expect((fetchMock.mock.calls[0] as [string])[0]).toBe(
      `http://backend.test/api/v1/runs/${RUN_ID}/events?after=0`
    );
  });

  it.each(["?after=abc", "?after=-3", "?after=", "?after=1.5"])(
    "rejects %s with 400 INVALID_INPUT without calling the backend",
    async (query) => {
      const response = await call(RUN_ID, query);

      expect(response.status).toBe(400);
      expect(await response.json()).toEqual({ code: "INVALID_INPUT" });
      expect(fetchMock).not.toHaveBeenCalled();
    }
  );

  it("answers 502 BACKEND_UNAVAILABLE when the fetch throws", async () => {
    fetchMock.mockRejectedValue(new TypeError("fetch failed"));

    const response = await call(RUN_ID, "?after=0");

    expect(response.status).toBe(502);
    expect(await response.json()).toEqual({ code: "BACKEND_UNAVAILABLE" });
    expect(response.headers.get("Cache-Control")).toBe("no-store");
  });
});
