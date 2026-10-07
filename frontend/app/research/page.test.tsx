import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import { startRunAction } from "@/app/actions/start-run";
import ResearchPage from "@/app/research/page";
import { errorMessages } from "@/lib/errors";
import { messages } from "@/lib/messages";

vi.mock("@/app/actions/start-run", () => ({ startRunAction: vi.fn() }));
const startRunMock = vi.mocked(startRunAction);

function fillForm(topic: string, audience: string) {
  fireEvent.change(screen.getByLabelText(messages.research.form.researchLabel), {
    target: { value: topic },
  });
  fireEvent.change(screen.getByLabelText(messages.research.form.audienceLabel), {
    target: { value: audience },
  });
}

function submitButton() {
  return screen.getByRole("button", { name: messages.research.form.submitCta });
}

const mockPush = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
}));

describe("Research page", () => {
  beforeEach(() => {
    mockPush.mockReset();
    startRunMock.mockReset();
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

  it("starts a run and navigates to the waiting screen", async () => {
    render(<ResearchPage />);
    startRunMock.mockResolvedValue({ ok: true, run_id: "r-1" });
    fillForm("  Árazási teszt ", " KKV vezetők  ");

    fireEvent.click(submitButton());

    await waitFor(() => expect(mockPush).toHaveBeenCalledWith("/waiting/r-1"));
    expect(startRunMock).toHaveBeenCalledWith({
      topic: "Árazási teszt",
      audience: "KKV vezetők",
    });
  });

  it("shows the mapped error message and re-enables submit when start fails", async () => {
    render(<ResearchPage />);
    startRunMock.mockResolvedValue({ ok: false, code: "RUN_START_FAILED" });
    fillForm("Árazási teszt", "KKV vezetők");

    fireEvent.click(submitButton());

    expect(await screen.findByRole("alert")).toHaveTextContent(
      errorMessages.RUN_START_FAILED
    );
    await waitFor(() => expect(submitButton()).toBeEnabled());
    expect(mockPush).not.toHaveBeenCalled();
  });

  it("disables submit while the run is starting", async () => {
    render(<ResearchPage />);
    startRunMock.mockReturnValue(new Promise(() => {}));
    fillForm("Árazási teszt", "KKV vezetők");

    fireEvent.click(submitButton());

    await waitFor(() => expect(submitButton()).toBeDisabled());
    fireEvent.click(submitButton());
    expect(startRunMock).toHaveBeenCalledTimes(1);
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
