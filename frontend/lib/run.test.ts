import type { MockInstance } from "vitest";

import { fetchRun } from "@/lib/run";

const RUN_ID = "3f1c2a52-8a54-4c3e-9d57-0a6c6f9b1e11";

describe("fetchRun", () => {
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

  it("returns null for a non-UUID id without calling the backend", async () => {
    expect(await fetchRun("nem-uuid")).toBeNull();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("returns null on 404", async () => {
    fetchMock.mockResolvedValue(new Response("{}", { status: 404 }));
    expect(await fetchRun(RUN_ID)).toBeNull();
  });

  it("throws on 503", async () => {
    fetchMock.mockResolvedValue(new Response("{}", { status: 503 }));
    await expect(fetchRun(RUN_ID)).rejects.toThrow();
  });

  it("returns the body on 200 and calls the run detail path", async () => {
    const body = { run_id: RUN_ID, status: "completed" };
    fetchMock.mockResolvedValue(new Response(JSON.stringify(body), { status: 200 }));

    expect(await fetchRun(RUN_ID)).toEqual(body);
    const [url] = fetchMock.mock.calls[0];
    expect(url).toBe(`http://backend.test/api/v1/runs/${RUN_ID}`);
  });
});
