import { fireEvent, render, screen } from "@testing-library/react";

import ResearchPage from "@/app/research/page";
import { messages } from "@/lib/messages";

const mockPush = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
}));

describe("Research page", () => {
  beforeEach(() => {
    mockPush.mockReset();
  });

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

  it("navigates to /research/email with encoded query params on submit", () => {
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

    expect(mockPush).toHaveBeenCalledWith(
      `/research/email?topic=${encodeURIComponent("Árazási teszt")}&audience=${encodeURIComponent("Középvállalati CFO-k")}`
    );
  });

  it("navigates to /research/email on submit with trimmed values", () => {
    render(<ResearchPage />);

    fireEvent.change(screen.getByLabelText(messages.research.form.researchLabel), {
      target: { value: "  Csomagár teszt  " },
    });
    fireEvent.change(screen.getByLabelText(messages.research.form.audienceLabel), {
      target: { value: "  SaaS termékvezetők  " },
    });
    fireEvent.click(
      screen.getByRole("button", { name: messages.research.form.submitCta })
    );

    expect(mockPush).toHaveBeenCalledWith(
      `/research/email?topic=${encodeURIComponent("Csomagár teszt")}&audience=${encodeURIComponent("SaaS termékvezetők")}`
    );
  });

  it("does not navigate when only one field is filled on submit", () => {
    render(<ResearchPage />);

    fireEvent.change(screen.getByLabelText(messages.research.form.researchLabel), {
      target: { value: "Csomagár teszt" },
    });

    fireEvent.click(
      screen.getByRole("button", { name: messages.research.form.submitCta })
    );

    expect(mockPush).not.toHaveBeenCalled();
  });

  it("does not navigate when both fields are empty on submit", () => {
    render(<ResearchPage />);

    fireEvent.click(
      screen.getByRole("button", { name: messages.research.form.submitCta })
    );

    expect(mockPush).not.toHaveBeenCalled();
  });

});
