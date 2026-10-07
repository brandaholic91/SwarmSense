import { act, render, screen, within } from "@testing-library/react";
import type { MockInstance } from "vitest";

import { LiveTrace } from "@/components/live-trace";
import { getErrorMessageByCode } from "@/lib/errors";
import { messages } from "@/lib/messages";
import { ev, fullRunEvents } from "@/test/trace-fixtures";

const RUN_ID = "3f1c2a52-8a54-4c3e-9d57-0a6c6f9b1e11";
const replaceMock = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: replaceMock, push: vi.fn() }),
}));

const price = { input_per_million_usd: 0.5, output_per_million_usd: 1.5 };

function ok(events: unknown[], status = "running"): Response {
  return new Response(
    JSON.stringify({ status, is_sample: false, topic: "Árazás", price, events }),
    { status: 200 }
  );
}

function urls(fetchMock: MockInstance<typeof fetch>): string[] {
  return fetchMock.mock.calls.map((call) => String(call[0]));
}

// Egy tick: a függőben lévő promise-ok lefutnak, majd az idő előreugrik.
async function tick(ms = 1000) {
  await act(async () => {
    await vi.advanceTimersByTimeAsync(ms);
  });
}

describe("LiveTrace", () => {
  let fetchMock: MockInstance<typeof fetch>;

  beforeEach(() => {
    vi.useFakeTimers();
    replaceMock.mockReset();
    fetchMock = vi.spyOn(global, "fetch");
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("requests after=0 first, then after the largest received id", async () => {
    fetchMock
      .mockResolvedValueOnce(ok([ev(1, "run_started"), ev(2, "personas_generated")]))
      .mockResolvedValue(ok([]));

    render(<LiveTrace runId={RUN_ID} />);
    await tick(0);
    await tick(1000);

    expect(urls(fetchMock)[0]).toBe(`/api/runs/${RUN_ID}/events?after=0`);
    expect(urls(fetchMock)[1]).toBe(`/api/runs/${RUN_ID}/events?after=2`);
  });

  it("does not start a new request while the previous one is pending", async () => {
    fetchMock.mockReturnValue(new Promise(() => {}));

    render(<LiveTrace runId={RUN_ID} />);
    await tick(5000);

    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("redirects to the result page and stops when the first response is a complete run", async () => {
    fetchMock.mockResolvedValue(ok(fullRunEvents()));

    render(<LiveTrace runId={RUN_ID} />);
    await tick(0);
    await tick(5000);

    expect(replaceMock).toHaveBeenCalledTimes(1);
    expect(replaceMock).toHaveBeenCalledWith(`/eredmeny/${RUN_ID}`);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("fetches immediately when the tab becomes visible, without waiting the interval", async () => {
    fetchMock.mockResolvedValue(ok([]));
    render(<LiveTrace runId={RUN_ID} />);
    await tick(0);
    expect(fetchMock).toHaveBeenCalledTimes(1);

    Object.defineProperty(document, "visibilityState", { configurable: true, value: "visible" });
    await act(async () => {
      document.dispatchEvent(new Event("visibilitychange"));
      await vi.advanceTimersByTimeAsync(0);
    });

    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("shows the connection error and the sample link after three failures, then stops", async () => {
    fetchMock.mockResolvedValue(new Response("{}", { status: 500 }));

    render(<LiveTrace runId={RUN_ID} />);
    await tick(0);
    await tick(1000);
    await tick(1000);
    await tick(5000);

    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(screen.getByRole("alert")).toHaveTextContent(messages.trace.connectionLost);
    expect(screen.getByRole("link", { name: messages.trace.sampleLink })).toHaveAttribute(
      "href",
      "/minta"
    );
  });

  it("resets the failure counter after a successful response", async () => {
    fetchMock
      .mockRejectedValueOnce(new TypeError("network"))
      .mockRejectedValueOnce(new TypeError("network"))
      .mockResolvedValueOnce(ok([]))
      .mockRejectedValueOnce(new TypeError("network"))
      .mockRejectedValueOnce(new TypeError("network"))
      .mockResolvedValue(ok([]));

    render(<LiveTrace runId={RUN_ID} />);
    await tick(0);
    for (let i = 0; i < 6; i++) await tick(1000);

    expect(fetchMock.mock.calls.length).toBeGreaterThan(5);
    expect(screen.queryByText(messages.trace.connectionLost)).not.toBeInTheDocument();
  });

  it("stops after a 404 and shows the not-found message", async () => {
    fetchMock.mockResolvedValue(new Response('{"code":"RUN_NOT_FOUND"}', { status: 404 }));

    render(<LiveTrace runId={RUN_ID} />);
    await tick(0);
    await tick(5000);

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(screen.getByText(/nem találjuk/i)).toBeInTheDocument();
  });

  it("shows the failure text for run_failed and does not redirect", async () => {
    fetchMock.mockResolvedValue(
      ok([ev(1, "run_started"), ev(2, "run_failed", { error_code: "TOO_FEW_PERSONAS" })])
    );

    render(<LiveTrace runId={RUN_ID} />);
    await tick(0);
    await tick(5000);

    expect(screen.getByRole("alert")).toHaveTextContent(getErrorMessageByCode("TOO_FEW_PERSONAS"));
    expect(screen.getByRole("link", { name: messages.trace.sampleLink })).toHaveAttribute(
      "href",
      "/minta"
    );
    expect(replaceMock).not.toHaveBeenCalled();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it.each(["completed", "partial"])(
    "redirects on status %s even when no run_completed event arrived",
    async (status) => {
      fetchMock.mockResolvedValue(ok([ev(1, "run_started")], status));

      render(<LiveTrace runId={RUN_ID} />);
      await tick(0);
      await tick(5000);

      expect(replaceMock).toHaveBeenCalledTimes(1);
      expect(replaceMock).toHaveBeenCalledWith(`/eredmeny/${RUN_ID}`);
      expect(fetchMock).toHaveBeenCalledTimes(1);
    }
  );

  it("shows the generic failure and stops polling on status failed without a run_failed event", async () => {
    fetchMock.mockResolvedValue(
      ok([ev(1, "run_started"), ev(2, "persona_started", { persona_index: 0, persona_name: "P0" })], "failed")
    );

    render(<LiveTrace runId={RUN_ID} />);
    await tick(0);
    await tick(5000);

    expect(screen.getByRole("alert")).toHaveTextContent(getErrorMessageByCode("INTERNAL_ERROR"));
    expect(
      within(screen.getByRole("list", { name: messages.trace.personasAriaLabel })).queryByText(
        messages.trace.row.running
      )
    ).not.toBeInTheDocument();
    expect(replaceMock).not.toHaveBeenCalled();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});
