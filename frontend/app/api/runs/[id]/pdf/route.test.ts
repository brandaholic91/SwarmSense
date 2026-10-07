import type { MockInstance } from "vitest";

import { GET } from "@/app/api/runs/[id]/pdf/route";

const RUN_ID = "3f1c2a52-8a54-4c3e-9d57-0a6c6f9b1e11";

function call(id: string) {
  return GET(new Request(`http://localhost:3000/api/runs/${id}/pdf`), {
    params: Promise.resolve({ id }),
  });
}

describe("GET /api/runs/[id]/pdf", () => {
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

  it("passes the binary body and both headers through unchanged", async () => {
    const bytes = new Uint8Array([0x25, 0x50, 0x44, 0x46, 0x2d, 0x00, 0xff, 0x80]);
    const disposition = `attachment; filename="swarmsense-${RUN_ID.slice(0, 8)}.pdf"`;
    fetchMock.mockResolvedValue(
      new Response(bytes, {
        status: 200,
        headers: { "Content-Type": "application/pdf", "Content-Disposition": disposition },
      })
    );

    const response = await call(RUN_ID);

    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe(`http://backend.test/api/v1/runs/${RUN_ID}/pdf`);
    expect(new Headers(init.headers).get("X-Internal-Secret")).toBe("s3cret");
    expect(response.status).toBe(200);
    expect(response.headers.get("Content-Type")).toBe("application/pdf");
    expect(response.headers.get("Content-Disposition")).toBe(disposition);
    expect(new Uint8Array(await response.arrayBuffer())).toEqual(bytes);
  });

  it("waits up to 90 seconds for the backend", async () => {
    const timeoutSpy = vi.spyOn(AbortSignal, "timeout");
    fetchMock.mockResolvedValue(new Response(new Uint8Array([1]), { status: 200 }));

    await call(RUN_ID);

    expect(timeoutSpy).toHaveBeenCalledWith(90_000);
  });

  it("answers 404 RUN_NOT_FOUND for a non-UUID id without calling the backend", async () => {
    const response = await call("not-a-uuid");

    expect(response.status).toBe(404);
    expect(await response.json()).toEqual({ code: "RUN_NOT_FOUND" });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("passes a backend 503 through with its code", async () => {
    fetchMock.mockResolvedValue(
      new Response(JSON.stringify({ detail: "x", code: "PDF_UNAVAILABLE" }), {
        status: 503,
        headers: { "Content-Type": "application/json" },
      })
    );

    const response = await call(RUN_ID);

    expect(response.status).toBe(503);
    expect(await response.json()).toEqual({ code: "PDF_UNAVAILABLE" });
    expect(response.headers.get("Content-Type")).toBe("application/json");
  });

  it("never forwards an arbitrary upstream error body", async () => {
    fetchMock.mockResolvedValue(
      new Response("<html>Internal Server Error NYERS</html>", {
        status: 500,
        headers: { "Content-Type": "text/html" },
      })
    );

    const response = await call(RUN_ID);

    expect(response.status).toBe(500);
    expect(await response.json()).toEqual({ code: "BACKEND_UNAVAILABLE" });
    expect(response.headers.get("Cache-Control")).toBe("no-store");
  });

  it("answers 502 BACKEND_UNAVAILABLE when the fetch throws", async () => {
    fetchMock.mockRejectedValue(new TypeError("fetch failed"));

    const response = await call(RUN_ID);

    expect(response.status).toBe(502);
    expect(await response.json()).toEqual({ code: "BACKEND_UNAVAILABLE" });
  });
});
