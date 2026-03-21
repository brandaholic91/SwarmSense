import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import QualifierPage from "@/app/qualifier/page";
import { messages } from "@/lib/messages";

const mockPush = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
}));

describe("Qualifier page", () => {
  it("renders intro copy and keeps a single disabled primary CTA by default", () => {
    render(<QualifierPage />);

    expect(screen.getByText(messages.qualifier.intro)).toBeInTheDocument();

    const submit = screen.getByRole("button", {
      name: messages.qualifier.form.submitCta,
    });

    expect(submit).toBeDisabled();
    expect(submit).toHaveAttribute("aria-disabled", "true");
  });

  it("renders selector-only inputs with required minimum options", () => {
    render(<QualifierPage />);

    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();

    const radioGroup = screen.getByRole("radiogroup", {
      name: messages.qualifier.form.useCaseLabel,
    });
    expect(radioGroup).toBeInTheDocument();

    const useCaseOptions = screen.getAllByRole("radio");
    expect(useCaseOptions.length).toBeGreaterThanOrEqual(4);

    const roleSelect = screen.getByRole("combobox", {
      name: messages.qualifier.form.roleLabel,
    });
    fireEvent.click(roleSelect);

    const roleOptions = screen.getAllByRole("option");
    expect(roleOptions.length).toBeGreaterThanOrEqual(5);
  });

  it("shows inline validation errors on blur and enables submit only after both answers", async () => {
    render(<QualifierPage />);

    const roleSelect = screen.getByRole("combobox", {
      name: messages.qualifier.form.roleLabel,
    });
    const radioGroup = screen.getByRole("radiogroup", {
      name: messages.qualifier.form.useCaseLabel,
    });

    fireEvent.blur(roleSelect);
    fireEvent.blur(radioGroup);

    // Blur handler uses setTimeout(0) for cross-browser relatedTarget compatibility.
    await waitFor(() => {
      expect(
        screen.getByText(messages.qualifier.form.errors.roleAnswer)
      ).toBeInTheDocument();
      expect(
        screen.getByText(messages.qualifier.form.errors.useCaseAnswer)
      ).toBeInTheDocument();
    });

    const submit = screen.getByRole("button", {
      name: messages.qualifier.form.submitCta,
    });
    expect(submit).toBeDisabled();

    fireEvent.click(roleSelect);
    fireEvent.click(screen.getByRole("option", { name: messages.qualifier.form.roleOptions[0].label }));

    fireEvent.click(
      screen.getByRole("radio", {
        name: messages.qualifier.form.useCaseOptions[0].label,
      })
    );

    expect(submit).toBeEnabled();
    expect(submit).not.toHaveAttribute("aria-disabled");
  });

  it("navigates to /waiting after successful submit", async () => {
    render(<QualifierPage />);

    fireEvent.click(
      screen.getByRole("combobox", { name: messages.qualifier.form.roleLabel })
    );
    fireEvent.click(
      screen.getByRole("option", { name: messages.qualifier.form.roleOptions[0].label })
    );
    fireEvent.click(
      screen.getByRole("radio", { name: messages.qualifier.form.useCaseOptions[0].label })
    );

    fireEvent.submit(screen.getByRole("button", { name: messages.qualifier.form.submitCta }));

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/waiting");
    });
  });

  it("applies full-width minimum touch target classes for use-case options", () => {
    render(<QualifierPage />);

    const optionCard = screen
      .getByText(messages.qualifier.form.useCaseOptions[0].label)
      .closest("label");

    expect(optionCard).toHaveClass("w-full");
    expect(optionCard).toHaveClass("min-h-12");
  });
});
