import { render, screen } from "@testing-library/react";
import { axe } from "jest-axe";

import MethodologyPage from "@/app/modszertan/page";

describe("Methodology page", () => {
  it("describes the run, the limits and the numbers", () => {
    const { container } = render(<MethodologyPage />);
    const text = container.textContent ?? "";

    for (const phrase of ["18", "20 hívás", "legfeljebb 5", "legfeljebb 3 kísérlet", "12", "nem reprezentatív", "listaár"]) {
      expect(text).toContain(phrase);
    }
  });

  it("links to the sample run", () => {
    render(<MethodologyPage />);

    const link = screen.getByRole("link", { name: /mintafutás/i });
    expect(link).toHaveAttribute("href", "/minta");
  });

  it("reports no critical axe violations", async () => {
    const { container } = render(<MethodologyPage />);
    const results = await axe(container);

    expect(results.violations.filter((v) => v.impact === "critical")).toHaveLength(0);
  });
});
