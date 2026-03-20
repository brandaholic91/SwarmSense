import { joinWaitlistAction } from "@/app/actions/join-waitlist";

describe("joinWaitlistAction", () => {
  const originalApiUrl = process.env.API_URL;

  beforeEach(() => {
    process.env.API_URL = "http://localhost:8000";
    vi.restoreAllMocks();
  });

  afterAll(() => {
    process.env.API_URL = originalApiUrl;
  });

  it("returns success when user is newly joined", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ status: "joined" }), { status: 200 })
    );

    const result = await joinWaitlistAction({ email: "user@example.com" });

    expect(result).toEqual({ ok: true, status: "joined" });
  });

  it("treats duplicate signup as successful", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ status: "already_joined" }), { status: 200 })
    );

    const result = await joinWaitlistAction({ email: "user@example.com" });

    expect(result).toEqual({ ok: true, status: "already_joined" });
  });

  it("maps backend error code to Hungarian user message", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          detail: "Failed to join waitlist",
          code: "WAITLIST_SIGNUP_FAILED",
        }),
        { status: 500 }
      )
    );

    const result = await joinWaitlistAction({ email: "user@example.com" });

    expect(result).toEqual({
      ok: false,
      message: "Most nem sikerult feliratkozni az ertesitore. Kerjuk, probald ujra.",
    });
  });
});
