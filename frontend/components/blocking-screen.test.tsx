import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import { BlockingScreen } from "@/components/blocking-screen";
import { messages } from "@/lib/messages";

let joinWaitlistImpl = vi.fn();

vi.mock("@/app/actions/join-waitlist", () => ({
  joinWaitlistAction: (...args: unknown[]) => joinWaitlistImpl(...args),
}));

describe("BlockingScreen", () => {
  beforeEach(() => {
    joinWaitlistImpl = vi.fn();
  });

  it("shows exactly one primary CTA in default state", () => {
    render(<BlockingScreen email="user@example.com" canSubmitWaitlist />);

    const cta = screen.getByRole("button", { name: messages.blockingScreen.cta });
    expect(cta).toBeInTheDocument();
    expect(screen.getAllByRole("button")).toHaveLength(1);
  });

  it("transitions to waitlist-submitted state after successful submit", async () => {
    joinWaitlistImpl.mockResolvedValue({ ok: true, status: "joined" });

    render(<BlockingScreen email="user@example.com" canSubmitWaitlist />);

    fireEvent.click(screen.getByRole("button", { name: messages.blockingScreen.cta }));

    await waitFor(() => {
      expect(screen.getByText(messages.blockingScreen.submitted)).toBeInTheDocument();
    });

    expect(
      screen.queryByRole("button", { name: messages.blockingScreen.cta })
    ).not.toBeInTheDocument();
  });

  it("disables submit when email handoff is missing", () => {
    render(<BlockingScreen email={null} canSubmitWaitlist={false} />);

    const cta = screen.getByRole("button", { name: messages.blockingScreen.cta });
    expect(cta).toBeDisabled();
    expect(screen.getByText(messages.blockingScreen.invalidEmail)).toBeInTheDocument();
  });
});
