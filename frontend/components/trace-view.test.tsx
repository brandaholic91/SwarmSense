import { render, screen, within } from "@testing-library/react";
import { axe } from "jest-axe";

import { formatRowTokens, TraceView } from "@/components/trace-view";
import { estimateCostUsd, formatCostUsd } from "@/lib/cost";
import { messages } from "@/lib/messages";
import { applyEvent, initialTraceState } from "@/lib/trace";
import { ev, fullRunEvents } from "@/test/trace-fixtures";

const price = { input_per_million_usd: 0.5, output_per_million_usd: 1.5 };
const NOW = Date.parse("2026-10-07T12:01:00Z");
const t = messages.trace;

function personaList() {
  return within(screen.getByRole("list", { name: t.personasAriaLabel }));
}

describe("TraceView", () => {
  const done = fullRunEvents().reduce(applyEvent, initialTraceState());

  it("shows 17 completed rows and one failed row with its error code", () => {
    render(<TraceView topic="Árazás" state={done} now={NOW} price={price} />);

    const list = personaList();
    expect(list.getAllByText(t.row.completed)).toHaveLength(17);
    expect(list.getAllByText(t.row.failed)).toHaveLength(1);
    expect(list.getByText("INVALID_RESPONSE")).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Árazás");
  });

  it("shows attempt 2/3 for the retried persona", () => {
    render(<TraceView topic="x" state={done} now={NOW} price={price} />);

    expect(personaList().getAllByText(`${t.row.attemptLabel} 2/3`)).toHaveLength(1);
  });

  it("shows each finished persona's own tokens in its row", () => {
    render(<TraceView topic="x" state={done} now={NOW} price={price} />);

    const list = personaList();
    // 17 kész persona 100/200 tokennel, a kiesett 10/20-szal
    expect(list.getAllByText(formatRowTokens(100, 200))).toHaveLength(17);
    const failedRow = list.getByText("INVALID_RESPONSE").closest("li");
    expect(failedRow).toHaveTextContent(formatRowTokens(10, 20));
  });

  it("groups thousands in the row tokens", () => {
    expect(formatRowTokens(812, 1940)).toBe(
      `${t.row.tokensIn} 812 · ${t.row.tokensOut} 1 940 ${t.row.tokensUnit}`
    );
    expect(formatRowTokens(0, 1234567)).toContain("1 234 567");
  });

  it("shows a dash instead of tokens while a persona is still running", () => {
    const state = [
      ev(1, "run_started"),
      ev(2, "personas_generated"),
      ev(3, "persona_started", { persona_index: 0, persona_name: "P0" }),
      ev(4, "persona_started", { persona_index: 1, persona_name: "P1" }),
      ev(5, "persona_completed", { persona_index: 1, input_tokens: 7, output_tokens: 9 }),
    ].reduce(applyEvent, initialTraceState());

    render(<TraceView topic="x" state={state} now={NOW} price={price} />);

    const list = personaList();
    const running = list.getByText("P0").closest("li");
    expect(running).toHaveTextContent(t.row.tokensPending);
    expect(running).not.toHaveTextContent(t.row.tokensUnit);
    expect(list.getByText("P1").closest("li")).toHaveTextContent(formatRowTokens(7, 9));
  });

  it("shows a failed run's unfinished personas as interrupted, not running", () => {
    const state = [
      ev(1, "run_started"),
      ev(2, "personas_generated"),
      ev(3, "persona_started", { persona_index: 0, persona_name: "P0" }),
      ev(4, "persona_started", { persona_index: 1, persona_name: "P1" }),
      ev(5, "persona_completed", { persona_index: 1, input_tokens: 7, output_tokens: 9 }),
      ev(10, "run_failed", { error_code: "RUN_TIMED_OUT" }),
    ].reduce(applyEvent, initialTraceState());

    render(<TraceView topic="x" state={state} now={NOW + 60_000} price={price} />);

    const list = personaList();
    expect(list.queryByText(t.row.running)).not.toBeInTheDocument();
    const row = list.getByText("P0").closest("li");
    expect(row).toHaveTextContent(t.row.interrupted);
    // az óra a lezáráskor megáll: 7 mp (12:00:03 -> 12:00:10), nem a mostani idő
    expect(row).toHaveTextContent("0:07");
    expect(row).toHaveTextContent(t.row.tokensPending);
    const summary = within(screen.getByLabelText(t.summaryAriaLabel));
    expect(summary.getByText(t.summary.interrupted).nextElementSibling).toHaveTextContent("1");
    expect(summary.getByText(t.summary.running).nextElementSibling).toHaveTextContent("0");
  });

  it("shows the estimated cost and the estimate marker in the summary", () => {
    render(<TraceView topic="x" state={done} now={NOW} price={price} />);

    const summary = within(screen.getByLabelText(t.summaryAriaLabel));
    const expected = formatCostUsd(estimateCostUsd(done.inputTokens, done.outputTokens, price));
    expect(summary.getByText(expected)).toBeInTheDocument();
    expect(summary.getByText(new RegExp(t.summary.estimate))).toBeInTheDocument();
  });

  it("shows 13 queued rows in the personas phase after 5 personas started", () => {
    const state = [
      ev(1, "run_started"),
      ev(2, "personas_generated"),
      ...[0, 1, 2, 3, 4].map((i) =>
        ev(3 + i, "persona_started", { persona_index: i, persona_name: `P${i}` })
      ),
    ].reduce(applyEvent, initialTraceState());

    render(<TraceView topic="x" state={state} now={NOW} price={price} />);

    expect(personaList().getAllByText(t.row.queued)).toHaveLength(13);
    expect(personaList().getAllByText(t.row.running)).toHaveLength(5);
  });

  it("marks the current phase", () => {
    const state = [ev(1, "run_started"), ev(2, "personas_generated")].reduce(
      applyEvent,
      initialTraceState()
    );
    render(<TraceView topic="x" state={state} now={NOW} price={price} />);

    const phases = within(screen.getByRole("list", { name: t.phasesAriaLabel }));
    expect(phases.getByText(t.phases.personas).closest("li")).toHaveAttribute("aria-current", "step");
  });

  it("has no critical accessibility violations", async () => {
    const { container } = render(<TraceView topic="Árazás" state={done} now={NOW} price={price} />);

    const results = await axe(container);
    expect(results.violations.filter((v) => v.impact === "critical")).toEqual([]);
  });
});
