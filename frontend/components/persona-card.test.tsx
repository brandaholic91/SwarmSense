import { render, screen } from "@testing-library/react";

import { PersonaCard } from "@/components/persona-card";
import {
  stanceReject,
  surface,
  textPrimary,
  textSecondary,
} from "@/lib/tokens";

describe("PersonaCard", () => {
  it("renders stance label, name, and summary", () => {
    render(
      <PersonaCard
        name="Kovacs Reka"
        role="CFO"
        stance="reject"
        stanceLabel="Elutasitja"
        summary="Tul nagy a kockazat."
        ariaLabel="Kovacs Reka - Elutasitja - CFO"
        variant="compact"
      />
    );

    expect(screen.getByLabelText("Kovacs Reka - Elutasitja - CFO")).toBeInTheDocument();
    expect(screen.getByText("Elutasitja")).toBeInTheDocument();
    expect(screen.getByText("Kovacs Reka")).toBeInTheDocument();
    expect(screen.getByText("Tul nagy a kockazat.")).toBeInTheDocument();
  });

  it("applies stance and surface styling", () => {
    render(
      <PersonaCard
        name="Varga Daniel"
        role="Termekvezeto"
        stance="reject"
        stanceLabel="Elutasitja"
        summary="Tesztszoveg."
        ariaLabel="Varga Daniel - Elutasitja - Termekvezeto"
      />
    );

    const card = screen.getByLabelText(
      "Varga Daniel - Elutasitja - Termekvezeto"
    );

    expect(card).toHaveStyle(`border-left-color: ${stanceReject}`);
    expect(card).toHaveStyle(`background-color: ${surface}`);
    expect(card).toHaveStyle(`color: ${textPrimary}`);

    const meta = screen.getByText("Termekvezeto");
    expect(meta).toHaveStyle(`color: ${textSecondary}`);
  });
});
