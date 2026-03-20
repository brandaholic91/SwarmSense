import { render, screen } from "@testing-library/react";
import { axe } from "jest-axe";

import Home from "@/app/page";
import { messages } from "@/lib/messages";

describe("Landing page", () => {
  it("renders the hero headline and preview stat", () => {
    render(<Home />);

    expect(screen.getByText(messages.landing.hero.headline)).toBeInTheDocument();
    expect(screen.getByText(messages.landing.preview.stat)).toBeInTheDocument();
  });

  it("shows three persona cards", () => {
    render(<Home />);

    const cards = screen.getAllByRole("article");
    expect(cards).toHaveLength(3);
  });

  it("reports no critical axe violations", async () => {
    const { container } = render(<Home />);
    const results = await axe(container);
    const critical = results.violations.filter(
      (violation) => violation.impact === "critical"
    );

    expect(critical).toHaveLength(0);
  });
});
