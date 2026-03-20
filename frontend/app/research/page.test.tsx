import { fireEvent, render, screen } from "@testing-library/react";

import ResearchPage from "@/app/research/page";
import { messages } from "@/lib/messages";

describe("Research page", () => {
  it("keeps submit disabled when only one field is filled", () => {
    render(<ResearchPage />);

    fireEvent.change(screen.getByLabelText(messages.research.form.researchLabel), {
      target: { value: "B2B onboarding" },
    });

    const submit = screen.getByRole("button", {
      name: messages.research.form.submitCta,
    });
    expect(submit).toBeDisabled();
    expect(submit).toHaveAttribute("aria-disabled", "true");
  });

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

  it("keeps email submit disabled until email and consent are provided", () => {
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

    const emailSubmit = screen.getByRole("button", {
      name: messages.research.form.email.cta,
    });
    const consent = screen.getByRole("checkbox");
    const email = screen.getByLabelText(messages.research.form.email.label);

    expect(consent).not.toBeChecked();
    expect(emailSubmit).toBeDisabled();
    expect(emailSubmit).toHaveAttribute("aria-disabled", "true");

    fireEvent.change(email, { target: { value: "teszt@example.com" } });
    expect(emailSubmit).toBeDisabled();

    fireEvent.click(consent);
    expect(emailSubmit).toBeEnabled();
  });

  it("renders privacy and terms links opening in a new tab", () => {
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

    const privacyLink = screen.getByRole("link", {
      name: messages.research.form.email.privacyPolicyLink,
    });
    const termsLink = screen.getByRole("link", {
      name: messages.research.form.email.termsOfServiceLink,
    });

    expect(privacyLink).toHaveAttribute("target", "_blank");
    expect(privacyLink).toHaveAttribute("rel", "noopener");
    expect(termsLink).toHaveAttribute("target", "_blank");
    expect(termsLink).toHaveAttribute("rel", "noopener");
  });
});
