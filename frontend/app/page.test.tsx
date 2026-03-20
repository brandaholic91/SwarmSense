import { fireEvent, render, screen } from "@testing-library/react";
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
    expect(cards).toHaveLength(messages.landing.preview.cards.length);
  });

  it("reports no critical axe violations", async () => {
    const { container } = render(<Home />);
    const results = await axe(container);
    const critical = results.violations.filter(
      (violation) => violation.impact === "critical"
    );

    expect(critical).toHaveLength(0);
  });

  it("renders the submission form fields and warning", () => {
    render(<Home />);

    expect(
      screen.getByLabelText(messages.landing.form.researchLabel)
    ).toBeInTheDocument();
    expect(
      screen.getByLabelText(messages.landing.form.audienceLabel)
    ).toBeInTheDocument();
    expect(
      screen.getByText(messages.landing.form.piiWarning)
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: messages.landing.form.cta })
    ).toBeInTheDocument();
  });

  it("disables submit until both fields are filled", () => {
    render(<Home />);

    const submit = screen.getByRole("button", {
      name: messages.landing.form.cta,
    });

    expect(submit).toBeDisabled();
    expect(submit).toHaveAttribute("aria-disabled", "true");

    fireEvent.change(screen.getByLabelText(messages.landing.form.researchLabel), {
      target: { value: "B2B onboarding" },
    });
    fireEvent.change(screen.getByLabelText(messages.landing.form.audienceLabel), {
      target: { value: "SaaS termékvezetők" },
    });

    expect(submit).not.toBeDisabled();
    expect(submit).toHaveAttribute("aria-disabled", "false");
  });

  it("shows inline validation errors on blur only", () => {
    render(<Home />);

    const researchField = screen.getByLabelText(messages.landing.form.researchLabel);

    expect(
      screen.queryByText(messages.landing.form.errors.researchTopic)
    ).not.toBeInTheDocument();

    fireEvent.blur(researchField);

    expect(
      screen.getByText(messages.landing.form.errors.researchTopic)
    ).toBeInTheDocument();

    fireEvent.change(researchField, { target: { value: "Persona kutatás" } });

    expect(
      screen.getByText(messages.landing.form.errors.researchTopic)
    ).toBeInTheDocument();
  });

  it("reveals the email capture stub on submit and preserves values", () => {
    render(<Home />);

    const researchField = screen.getByLabelText(messages.landing.form.researchLabel);
    const audienceField = screen.getByLabelText(messages.landing.form.audienceLabel);

    fireEvent.change(researchField, { target: { value: "Árazási teszt" } });
    fireEvent.change(audienceField, { target: { value: "Középvállalati CFO-k" } });

    fireEvent.click(
      screen.getByRole("button", { name: messages.landing.form.cta })
    );

    expect(screen.getByLabelText(messages.landing.form.emailLabel)).toBeInTheDocument();
    expect(screen.getByText(messages.emailCaptureNotice)).toBeInTheDocument();
    expect(researchField).toHaveValue("Árazási teszt");
    expect(audienceField).toHaveValue("Középvállalati CFO-k");
  });
});
