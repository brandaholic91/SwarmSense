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

  it("renders three persona cards in the example result preview", () => {
    render(<Home />);

    const cards = messages.landing.preview.cards.map((card) =>
      screen.getByLabelText(`${card.name} - ${card.stanceLabel} - ${card.role}`, {
        selector: "article",
      })
    );

    expect(cards).toHaveLength(messages.landing.preview.cards.length);
  });

  it("makes none of the removed claims", () => {
    const { container } = render(<Home />);
    const text = (container.textContent ?? "").toLowerCase();
    const forbidden = [
      "90 másodperc",
      "15-20",
      "15–20",
      "Megfizethető ár",
      "Ügynökségi büdzsé",
      "A piackutatás még sosem volt ilyen egyszerű",
      "e-mailben",
      "Ingyenes próba",
      // az eredményoldal nem mutatja a personák válaszait: azok a PDF-ben vannak
      "összefoglalót és a personák válaszait",
    ];

    const present = forbidden.filter((phrase) => text.includes(phrase.toLowerCase()));

    expect(present).toEqual([]);
  });

  it("states what the piece is", () => {
    const { container } = render(<Home />);
    const text = (container.textContent ?? "").toLowerCase();

    // a futásidő mért tartománya 86–126 mp: a szöveg „másfél-két percet” ígér
    const required = ["18", "portfólió", "másfél-két perc", "regisztráció nélkül", "pdf"];
    const missing = required.filter((phrase) => !text.includes(phrase));

    expect(missing).toEqual([]);
  });

  it("links to the sample, methodology, privacy and terms pages", () => {
    const { container } = render(<Home />);
    const hrefs = Array.from(container.querySelectorAll("a")).map((a) => a.getAttribute("href"));

    for (const href of ["/minta", "/modszertan", "/privacy", "/terms"]) {
      expect(hrefs).toContain(href);
    }
    expect(hrefs).not.toContain("#sample");
  });

  it("marks the example result as an illustration", () => {
    const { container } = render(<Home />);

    expect(container.querySelector("#sample")?.textContent).toContain("Illusztráció");
  });
});
