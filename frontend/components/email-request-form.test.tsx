import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { axe } from "jest-axe";

import { requestEmailAction } from "@/app/actions/request-email";
import { EmailRequestForm } from "@/components/email-request-form";
import { errorMessages } from "@/lib/errors";
import { messages } from "@/lib/messages";

vi.mock("@/app/actions/request-email", () => ({ requestEmailAction: vi.fn() }));
const actionMock = vi.mocked(requestEmailAction);

const RUN_ID = "3f1c2a52-8a54-4c3e-9d57-0a6c6f9b1e11";
const t = messages.result.email;

describe("EmailRequestForm", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("sends the typed address and shows a confirmation, then clears the field", async () => {
    actionMock.mockResolvedValue({ ok: true, emailsRemaining: 1 });
    render(<EmailRequestForm runId={RUN_ID} emailsRemaining={2} />);

    const input = screen.getByLabelText(t.label);
    fireEvent.change(input, { target: { value: "reader@example.com" } });
    fireEvent.click(screen.getByRole("button", { name: t.submit }));

    expect(actionMock).toHaveBeenCalledWith({ runId: RUN_ID, email: "reader@example.com" });
    expect(await screen.findByText(t.sent)).toBeInTheDocument();
    expect(input).toHaveValue("");
  });

  it("disables the button and explains when no mail can be requested", () => {
    render(<EmailRequestForm runId={RUN_ID} emailsRemaining={0} />);

    expect(screen.getByRole("button", { name: t.submit })).toBeDisabled();
    expect(screen.getByText(errorMessages.EMAIL_RUN_LIMIT_REACHED)).toBeInTheDocument();
  });

  it("shows the error text for a failure code with role=alert", async () => {
    actionMock.mockResolvedValue({ ok: false, code: "INVALID_EMAIL" });
    render(<EmailRequestForm runId={RUN_ID} emailsRemaining={3} />);

    fireEvent.change(screen.getByLabelText(t.label), { target: { value: "nem-cim" } });
    fireEvent.click(screen.getByRole("button", { name: t.submit }));

    expect(await screen.findByRole("alert")).toHaveTextContent(errorMessages.INVALID_EMAIL);
    expect(screen.queryByText(t.sent)).not.toBeInTheDocument();
  });

  it("disables the button while the request is in flight", async () => {
    let resolve!: (value: { ok: true; emailsRemaining: number }) => void;
    actionMock.mockReturnValue(new Promise((r) => (resolve = r)));
    render(<EmailRequestForm runId={RUN_ID} emailsRemaining={3} />);

    fireEvent.change(screen.getByLabelText(t.label), { target: { value: "reader@example.com" } });
    fireEvent.click(screen.getByRole("button", { name: t.submit }));

    await waitFor(() => expect(screen.getByRole("button")).toBeDisabled());
    resolve({ ok: true, emailsRemaining: 2 });
    await waitFor(() => expect(screen.getByRole("button")).toBeEnabled());
  });

  it("locks the form once the remaining count reaches zero after a send", async () => {
    actionMock.mockResolvedValue({ ok: true, emailsRemaining: 0 });
    render(<EmailRequestForm runId={RUN_ID} emailsRemaining={1} />);

    fireEvent.change(screen.getByLabelText(t.label), { target: { value: "reader@example.com" } });
    fireEvent.click(screen.getByRole("button", { name: t.submit }));

    expect(await screen.findByText(t.sent)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: t.submit })).toBeDisabled();
  });

  it("shows the 14-day deletion note with a link to the privacy page", () => {
    render(<EmailRequestForm runId={RUN_ID} emailsRemaining={3} />);

    expect(screen.getByText(t.retentionNote)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: t.privacyLink })).toHaveAttribute("href", "/privacy");
  });

  it("has no accessibility violations", async () => {
    const { container } = render(<EmailRequestForm runId={RUN_ID} emailsRemaining={3} />);
    const results = await axe(container);
    expect(results.violations.filter((v) => v.impact === "critical")).toEqual([]);
  });
});
