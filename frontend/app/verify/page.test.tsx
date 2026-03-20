import { render, screen, waitFor } from "@testing-library/react";

import { VerifyClient } from "@/app/verify/verify-client";
import { messages } from "@/lib/messages";

// vi.hoisted ensures these are available inside vi.mock factory closures (hoisted before imports).
// mockRouter must be a stable object — useRouter returning a new object each render would cause
// [token, router] useEffect to fire on every render, creating an infinite setState → re-render loop.
const { mockPush, mockRouter } = vi.hoisted(() => {
  const mockPush = vi.fn();
  return { mockPush, mockRouter: { push: mockPush } };
});

let verifyTokenImpl = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => mockRouter,
}));

vi.mock("@/app/actions/verify-token", () => ({
  verifyTokenAction: (...args: unknown[]) => verifyTokenImpl(...args),
}));

describe("VerifyClient", () => {
  beforeEach(() => {
    mockPush.mockReset();
    verifyTokenImpl = vi.fn();
  });

  it("redirects to qualifier when token verification succeeds", async () => {
    verifyTokenImpl.mockResolvedValue({ ok: true, user_id: "user-7" });

    render(<VerifyClient token="token-7" />);

    await waitFor(() => {
      expect(verifyTokenImpl).toHaveBeenCalledWith({ token: "token-7" });
      expect(mockPush).toHaveBeenCalledWith("/qualifier?user_id=user-7");
    });
  });

  it("renders full-screen Hungarian error state for expired tokens", async () => {
    verifyTokenImpl.mockResolvedValue({
      ok: false,
      code: "TOKEN_EXPIRED",
      detail: "Magic link token expired",
    });

    render(<VerifyClient token="token-9" />);

    await waitFor(() => {
      expect(screen.getByText(messages.verify.title)).toBeInTheDocument();
      expect(screen.getByText(messages.verify.descriptionPrefix)).toBeInTheDocument();
      expect(screen.getByText("A bejelentkezési link lejárt. Kérj újat.")).toBeInTheDocument();
      expect(
        screen.getByRole("link", { name: messages.verify.requestNewLinkCta })
      ).toHaveAttribute("href", "/research");
    });
  });

  it("renders same error screen for invalid tokens", async () => {
    verifyTokenImpl.mockResolvedValue({
      ok: false,
      code: "TOKEN_INVALID",
      detail: "Magic link token invalid",
    });

    render(<VerifyClient token="token-11" />);

    await waitFor(() => {
      expect(
        screen.getByText("A bejelentkezési link érvénytelen. Kérj újat.")
      ).toBeInTheDocument();
      expect(
        screen.getByRole("link", { name: messages.verify.requestNewLinkCta })
      ).toBeInTheDocument();
    });
  });

  it("renders missing-token error when no token is provided", async () => {
    render(<VerifyClient token="" />);

    await waitFor(() => {
      expect(
        screen.getByText("Nem érkezett bejelentkezési link. Kérj újat.")
      ).toBeInTheDocument();
    });
    expect(verifyTokenImpl).not.toHaveBeenCalled();
  });

  it("renders error state when network fails", async () => {
    verifyTokenImpl.mockRejectedValue(new Error("Network error"));

    render(<VerifyClient token="token-x" />);

    await waitFor(() => {
      expect(
        screen.getByText("A bejelentkezési link érvénytelen. Kérj újat.")
      ).toBeInTheDocument();
    });
  });
});
