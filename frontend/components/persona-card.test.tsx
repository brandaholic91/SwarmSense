import { render, screen } from "@testing-library/react";

import { PersonaCard } from "@/components/persona-card";
import {
  stanceConditional,
  stanceReject,
  stanceSupport,
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

  it("applies support stance color", () => {
    render(
      <PersonaCard
        name="Varga Daniel"
        role="PM"
        stance="support"
        stanceLabel="Tamogatja"
        summary="Pozitiv visszajelzes."
        ariaLabel="Varga Daniel - Tamogatja - PM"
      />
    );

    const card = screen.getByLabelText("Varga Daniel - Tamogatja - PM");
    expect(card).toHaveStyle(`border-left-color: ${stanceSupport}`);
  });

  it("applies conditional stance color", () => {
    render(
      <PersonaCard
        name="Toth Eszter"
        role="Marketing"
        stance="conditional"
        stanceLabel="Feltételes"
        summary="Felteteles visszajelzes."
        ariaLabel="Toth Eszter - Feltételes - Marketing"
      />
    );

    const card = screen.getByLabelText("Toth Eszter - Feltételes - Marketing");
    expect(card).toHaveStyle(`border-left-color: ${stanceConditional}`);
  });

  it("default variant does not apply line-clamp overflow to summary", () => {
    render(
      <PersonaCard
        name="Test User"
        role="Engineer"
        stance="reject"
        stanceLabel="Elutasitja"
        summary="Hosszu szoveg."
        ariaLabel="Test User - Elutasitja - Engineer"
        variant="default"
      />
    );

    const summary = screen.getByText("Hosszu szoveg.");
    expect(summary).not.toHaveStyle("overflow: hidden");
  });

  it("compact variant applies line-clamp overflow to summary", () => {
    render(
      <PersonaCard
        name="Test User"
        role="Engineer"
        stance="reject"
        stanceLabel="Elutasitja"
        summary="Hosszu szoveg."
        ariaLabel="Test User - Elutasitja - Engineer"
        variant="compact"
      />
    );

    const summary = screen.getByText("Hosszu szoveg.");
    expect(summary).toHaveStyle("overflow: hidden");
  });
});
