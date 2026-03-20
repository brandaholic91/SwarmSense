import { render, screen } from "@testing-library/react";
import { axe } from "jest-axe";

import Home from "@/app/page";
import { messages } from "@/lib/messages";

describe("Landing page", () => {
  it("renders the hero headline and preview content", () => {
    render(<Home />);

    const heroText = `${messages.landing.hero.headline} ${messages.landing.hero.highlight} ${messages.landing.hero.headlineSuffix}`;
    expect(
      screen.getByRole("heading", { name: heroText })
    ).toBeInTheDocument();
    expect(screen.getByText(messages.landing.preview.heading)).toBeInTheDocument();
  });

  it("reports no critical axe violations", async () => {
    const { container } = render(<Home />);
    const results = await axe(container);
    const critical = results.violations.filter(
      (violation) => violation.impact === "critical"
    );

    expect(critical).toHaveLength(0);
  });

  it("renders the nav CTA button", () => {
    render(<Home />);

    const ctas = screen.getAllByRole("link", { name: messages.landing.nav.cta });
    expect(ctas.length).toBeGreaterThan(0);
  });
});
