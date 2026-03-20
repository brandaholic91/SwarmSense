import { render, screen } from "@testing-library/react";

import VerifyPage from "@/app/verify/page";
import { messages } from "@/lib/messages";

const redirectMock = vi.fn();
const verifyTokenActionMock = vi.fn();

vi.mock("next/navigation", () => ({
  redirect: (path: string) => redirectMock(path),
}));

vi.mock("@/app/actions/verify-token", () => ({
  verifyTokenAction: (input: { token: string }) => verifyTokenActionMock(input),
}));

describe("Verify page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("redirects to qualifier when token verification succeeds", async () => {
    verifyTokenActionMock.mockResolvedValueOnce({ ok: true, user_id: "user-7" });

    await VerifyPage({ searchParams: { token: "token-7" } });

    expect(verifyTokenActionMock).toHaveBeenCalledWith({ token: "token-7" });
    expect(redirectMock).toHaveBeenCalledWith("/qualifier?user_id=user-7");
  });

  it("renders full-screen Hungarian error state for expired tokens", async () => {
    verifyTokenActionMock.mockResolvedValueOnce({
      ok: false,
      code: "TOKEN_EXPIRED",
      detail: "Magic link token expired",
    });

    const page = await VerifyPage({ searchParams: { token: "token-9" } });
    render(page);

    expect(screen.getByText(messages.verify.title)).toBeInTheDocument();
    expect(screen.getByText(messages.verify.descriptionPrefix)).toBeInTheDocument();
    expect(screen.getByText("A bejelentkezési link lejárt. Kérj újat.")).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: messages.verify.requestNewLinkCta })
    ).toHaveAttribute("href", "/research");
  });

  it("renders same error screen for invalid tokens", async () => {
    verifyTokenActionMock.mockResolvedValueOnce({
      ok: false,
      code: "TOKEN_INVALID",
      detail: "Magic link token invalid",
    });

    const page = await VerifyPage({ searchParams: { token: "token-11" } });
    render(page);

    expect(screen.getByText("A bejelentkezési link érvénytelen. Kérj újat.")).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: messages.verify.requestNewLinkCta })
    ).toBeInTheDocument();
  });
});
