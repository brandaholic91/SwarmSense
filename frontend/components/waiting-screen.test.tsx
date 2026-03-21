import { render, screen, waitFor } from "@testing-library/react";

import { WaitingScreen } from "@/components/waiting-screen";
import { messages } from "@/lib/messages";

function buildResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

describe("WaitingScreen", () => {
  beforeEach(() => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      buildResponse({
        run_id: "run-1",
        status: "running",
        persona_count: 3,
        total_personas: 18,
        updated_at: "2026-03-21T10:00:00+00:00",
      })
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("polls every 5 seconds and renders running counter with aria semantics", async () => {
    render(
      <WaitingScreen
        runId="run-1"
        email="teszt@example.com"
        apiBaseUrl="https://api.example.com"
      />
    );

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        "https://api.example.com/api/v1/runs/run-1/status",
        { cache: "no-store" }
      );
    });

    await waitFor(() => {
      expect(screen.getByText("Futtatás: 3/18 persona")).toBeInTheDocument();
    });

    const progressbar = screen.getByRole("progressbar");
    expect(progressbar).toHaveAttribute("aria-valuemin", "0");
    expect(progressbar).toHaveAttribute("aria-valuemax", "18");
    expect(progressbar).toHaveAttribute("aria-valuenow", "3");

  });

  it("shows transient generating state before first meaningful running progress", async () => {
    vi.mocked(global.fetch).mockResolvedValueOnce(
      buildResponse({
        run_id: "run-1",
        status: "running",
        persona_count: 0,
        total_personas: 18,
        updated_at: "2026-03-21T10:00:00+00:00",
      })
    );

    render(
      <WaitingScreen
        runId="run-1"
        email="teszt@example.com"
        apiBaseUrl="https://api.example.com"
      />
    );

    await waitFor(() => {
      expect(screen.getByText(messages.waiting.states.generating)).toBeInTheDocument();
    });
  });

  it("renders completed final status", async () => {
    vi.mocked(global.fetch)
      .mockResolvedValueOnce(
        buildResponse({
          run_id: "run-1",
          status: "completed",
          persona_count: 18,
          total_personas: 18,
          updated_at: "2026-03-21T10:00:00+00:00",
        })
      );

    render(
      <WaitingScreen
        runId="run-1"
        email="teszt@example.com"
        apiBaseUrl="https://api.example.com"
      />
    );

    await waitFor(() => {
      expect(screen.getByText(messages.waiting.states.completed)).toBeInTheDocument();
    });
  });

  it("renders failed-state retry guidance", async () => {
    vi.mocked(global.fetch).mockResolvedValueOnce(
      buildResponse({
        run_id: "run-1",
        status: "failed",
        persona_count: 7,
        total_personas: 18,
        updated_at: "2026-03-21T10:00:00+00:00",
      })
    );

    render(
      <WaitingScreen
        runId="run-1"
        email="teszt@example.com"
        apiBaseUrl="https://api.example.com"
      />
    );

    await waitFor(() => {
      expect(screen.getByText(messages.waiting.states.failed)).toBeInTheDocument();
    });

    expect(screen.getByText(messages.waiting.retrySuggestion)).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: messages.research.form.submitCta })
    ).toHaveAttribute("href", "/research");
  });
});
