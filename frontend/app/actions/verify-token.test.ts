import { verifyTokenAction } from "@/app/actions/verify-token";

describe("verifyTokenAction", () => {
  const originalApiUrl = process.env.API_URL;

  beforeEach(() => {
    process.env.API_URL = "http://localhost:8000";
    vi.restoreAllMocks();
  });

  afterAll(() => {
    process.env.API_URL = originalApiUrl;
  });

  it("returns user id for valid token", async () => {
    const fetchMock = vi
      .spyOn(global, "fetch")
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ user_id: "user-42" }), { status: 200 })
      );

    const result = await verifyTokenAction({ token: "token-123" });

    expect(result).toEqual({ ok: true, user_id: "user-42" });
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/auth/verify",
      expect.objectContaining({
        method: "POST",
      })
    );
  });

  it("preserves error payload contract for expired tokens", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(
        JSON.stringify({ detail: "Magic link token expired", code: "TOKEN_EXPIRED" }),
        { status: 401 }
      )
    );

    const result = await verifyTokenAction({ token: "token-123" });

    expect(result).toEqual({
      ok: false,
      detail: "Magic link token expired",
      code: "TOKEN_EXPIRED",
    });
  });

  it("maps unknown backend error code to TOKEN_INVALID", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(
        JSON.stringify({ detail: "Magic link token invalid", code: "SOMETHING_ELSE" }),
        { status: 401 }
      )
    );

    const result = await verifyTokenAction({ token: "token-123" });

    expect(result).toEqual({
      ok: false,
      detail: "Magic link token invalid",
      code: "TOKEN_INVALID",
    });
  });
});
