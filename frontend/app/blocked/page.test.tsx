import { render, screen } from "@testing-library/react";

import BlockedPage from "@/app/blocked/page";
import { messages } from "@/lib/messages";

describe("BlockedPage", () => {
  it("renders blocking screen with required heading and main landmark", async () => {
    const page = await BlockedPage({
      searchParams: { email: "user@example.com" },
    });

    render(page);

    expect(screen.getByRole("main")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: messages.blockingScreen.heading })
    ).toBeInTheDocument();
  });

  it("renders safe fallback state when email is missing or invalid", async () => {
    const page = await BlockedPage({
      searchParams: { email: "not-an-email" },
    });

    render(page);

    expect(screen.getByText(messages.blockingScreen.invalidEmail)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: messages.blockingScreen.cta })
    ).toBeDisabled();
  });
});
