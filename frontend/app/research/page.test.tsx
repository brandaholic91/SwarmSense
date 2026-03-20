import { fireEvent, render, screen } from "@testing-library/react";

import ResearchPage from "@/app/research/page";
import { messages } from "@/lib/messages";

describe("Research page", () => {
  it("disables submit when fields are empty", () => {
    render(<ResearchPage />);

    const submit = screen.getByRole("button", {
      name: messages.research.form.submitCta,
    });

    expect(submit).toBeDisabled();
    expect(submit).toHaveAttribute("aria-disabled", "true");
  });

  it("shows inline error when blurred with empty field", () => {
    render(<ResearchPage />);

    const researchField = screen.getByLabelText(messages.research.form.researchLabel);

    fireEvent.blur(researchField);

    expect(
      screen.getByText(messages.research.form.errors.researchTopic)
    ).toBeInTheDocument();
  });

  it("reveals the email capture section after submit", () => {
    render(<ResearchPage />);

    fireEvent.change(screen.getByLabelText(messages.research.form.researchLabel), {
      target: { value: "Árazási teszt" },
    });
    fireEvent.change(screen.getByLabelText(messages.research.form.audienceLabel), {
      target: { value: "Középvállalati CFO-k" },
    });

    fireEvent.click(
      screen.getByRole("button", { name: messages.research.form.submitCta })
    );

    expect(
      screen.getByText(messages.research.form.email.heading)
    ).toBeInTheDocument();
  });

  it("renders the email capture microcopy", () => {
    render(<ResearchPage />);

    fireEvent.change(screen.getByLabelText(messages.research.form.researchLabel), {
      target: { value: "Csomagár teszt" },
    });
    fireEvent.change(screen.getByLabelText(messages.research.form.audienceLabel), {
      target: { value: "SaaS termékvezetők" },
    });

    fireEvent.click(
      screen.getByRole("button", { name: messages.research.form.submitCta })
    );

    expect(
      screen.getByText(messages.research.form.email.subheadline)
    ).toBeInTheDocument();
    expect(
      screen.getByText(messages.research.form.email.privacyNote)
    ).toBeInTheDocument();
  });
});
