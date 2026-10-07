import { act, fireEvent, render, screen } from "@testing-library/react";
import type { MockInstance } from "vitest";

import { ReplayTrace } from "@/components/replay-trace";
import { messages } from "@/lib/messages";
import type { TraceEvent } from "@/lib/trace";

const RUN_ID = "3f1c2a52-8a54-4c3e-9d57-0a6c6f9b1e11";
const replaceMock = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: replaceMock, push: vi.fn() }),
}));

const price = { input_per_million_usd: 0.5, output_per_million_usd: 1.5 };

const EVENTS: TraceEvent[] = [
  { id: 1, type: "run_started", at: "2026-10-07T12:00:00.000Z" },
  { id: 2, type: "personas_generated", at: "2026-10-07T12:00:01.500Z", input_tokens: 120, output_tokens: 900 },
  { id: 3, type: "run_completed", at: "2026-10-07T12:00:03.000Z" },
];

function ok(events: TraceEvent[], status = "completed"): Response {
  return new Response(
    JSON.stringify({
      status,
      is_sample: true,
      topic: "Árazás",
      created_at: "2026-10-07T12:00:00Z",
      price,
      events,
    }),
    { status: 200 }
  );
}

async function advance(ms: number) {
  await act(async () => {
    await vi.advanceTimersByTimeAsync(ms);
  });
}

describe("ReplayTrace", () => {
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

  it("fetches the events exactly once, from the beginning", async () => {
    fetchMock.mockResolvedValue(ok(EVENTS));
    render(<ReplayTrace runId={RUN_ID} />);
    await advance(0);
    await advance(10_000);

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(String(fetchMock.mock.calls[0][0])).toBe(`/api/runs/${RUN_ID}/events?after=0`);
  });

  it("applies events at the original tempo", async () => {
    fetchMock.mockResolvedValue(ok(EVENTS));
    render(<ReplayTrace runId={RUN_ID} />);
    await advance(0); // a lekérés lezárul
    await advance(0); // az első esemény időzítője lefut

    // az első esemény (run_started) azonnal feldolgozódik, a második még nem
    expect(screen.getByText(messages.trace.phases.generating)).toHaveAttribute("aria-current", "step");
    await advance(1499);
    expect(screen.getByText(messages.trace.phases.generating)).toHaveAttribute("aria-current", "step");
    await advance(1);
    expect(screen.getByText(messages.trace.phases.personas)).toHaveAttribute("aria-current", "step");
  });

  it("shows the recorded label with the run date and the jump link throughout", async () => {
    fetchMock.mockResolvedValue(ok(EVENTS));
    render(<ReplayTrace runId={RUN_ID} />);
    await advance(0);

    expect(screen.getByText(/Rögzített futás, 2026\. október 7\./)).toBeInTheDocument();
    const link = screen.getByRole("link", { name: messages.replay.jumpToResult });
    expect(link).toHaveAttribute("href", `/eredmeny/${RUN_ID}`);

    await advance(1500);
    expect(screen.getByRole("link", { name: messages.replay.jumpToResult })).toHaveAttribute(
      "href",
      `/eredmeny/${RUN_ID}`
    );
  });

  it("keeps the final state and offers a restart that resets the state", async () => {
    fetchMock.mockResolvedValue(ok(EVENTS));
    render(<ReplayTrace runId={RUN_ID} />);
    await advance(0);
    expect(screen.queryByRole("button", { name: messages.replay.again })).not.toBeInTheDocument();

    await advance(3000);
    const again = screen.getByRole("button", { name: messages.replay.again });
    expect(screen.getByText(messages.trace.phases.pdf).closest("li")).not.toHaveAttribute("aria-current");

    fireEvent.click(again);
    expect(screen.queryByRole("button", { name: messages.replay.again })).not.toBeInTheDocument();
    // újrakezdés: a kezdeti állapot (nincs kiemelt fázis, nincs bepipált lépés)
    expect(document.querySelector('[aria-current="step"]')).toBeNull();
    expect(fetchMock).toHaveBeenCalledTimes(1);

    await advance(0);
    expect(screen.getByText(messages.trace.phases.generating)).toHaveAttribute("aria-current", "step");
  });

  it("redirects to the waiting page when the run is not finished", async () => {
    fetchMock.mockResolvedValue(ok(EVENTS.slice(0, 1), "running"));
    render(<ReplayTrace runId={RUN_ID} />);
    await advance(0);

    expect(replaceMock).toHaveBeenCalledWith(`/waiting/${RUN_ID}`);
    expect(screen.queryByRole("button", { name: messages.replay.again })).not.toBeInTheDocument();
  });

  it("shows an error message and a form link when the request fails", async () => {
    fetchMock.mockResolvedValue(new Response("{}", { status: 502 }));
    render(<ReplayTrace runId={RUN_ID} />);
    await advance(0);

    expect(screen.getByRole("alert")).toHaveTextContent(messages.replay.error);
    expect(screen.getByRole("link", { name: messages.trace.formLink })).toHaveAttribute("href", "/research");
  });

  it("shows the error when the network request throws", async () => {
    fetchMock.mockRejectedValue(new TypeError("network"));
    render(<ReplayTrace runId={RUN_ID} />);
    await advance(0);

    expect(screen.getByRole("alert")).toHaveTextContent(messages.replay.error);
  });
});
