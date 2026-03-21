import { render, screen } from "@testing-library/react";

import ResearchSentPage from "@/app/research/sent/page";
import { messages } from "@/lib/messages";

describe("ResearchSentPage", () => {
  it("renders sent confirmation with normalized email", async () => {
    const page = await ResearchSentPage({
      searchParams: { email: "User@Example.com " },
    });

    render(page);

    expect(
      screen.getByRole("heading", { name: messages.research.form.email.successHeading })
    ).toBeInTheDocument();
    expect(screen.getByText("user@example.com")).toBeInTheDocument();
  });

  it("renders safely when email query param is invalid", async () => {
    const page = await ResearchSentPage({
      searchParams: { email: "not-an-email" },
    });

    render(page);

    expect(
      screen.getByRole("heading", { name: messages.research.form.email.successHeading })
    ).toBeInTheDocument();
    expect(screen.queryByText("not-an-email")).not.toBeInTheDocument();
  });
});
