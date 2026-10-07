import { render, screen } from "@testing-library/react";
import { axe } from "jest-axe";

import { ResultView } from "@/components/result-view";
import { estimateCostUsd, formatCostUsd } from "@/lib/cost";
import { messages } from "@/lib/messages";
import type { RunDetail } from "@/lib/run";

const RUN_ID = "3f1c2a52-8a54-4c3e-9d57-0a6c6f9b1e11";
const t = messages.result;
const price = { input_per_million_usd: 0.5, output_per_million_usd: 1.5 };

function makeRun(overrides: Partial<RunDetail> = {}): RunDetail {
  return {
    run_id: RUN_ID,
    status: "completed",
    is_sample: false,
    topic: "Árazás",
    audience: "KKV vezetők",
    created_at: "2026-10-07T12:00:00Z",
    completed_at: "2026-10-07T12:01:26Z",
    duration_ms: 86500,
    input_tokens: 16134,
    output_tokens: 36335,
    retry_count: 2,
    price,
    result: {
      completed_persona_count: 18,
      total_persona_count: 18,
      stance_counts: { support: 10, reject: 5, conditional: 3 },
      personas: [{ name: "Persona 1", primary_argument: "TITKOS-ERV-SZOVEG" }],
      synthesis: {
        summary: "Az ár a fő akadály.",
        main_barriers: ["Ár"],
        winning_conditions: "Referenciák",
        best_target_segment: "KKV",
        strategic_recommendation: "Pilot",
      },
      failed_personas: [],
    },
    ...overrides,
  };
}

describe("ResultView", () => {
  it("shows summary, stance counts, run data and the links for a full run", () => {
    render(<ResultView run={makeRun()} />);

    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Árazás");
    expect(screen.getByText("KKV vezetők")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: t.summaryHeading })).toBeInTheDocument();
    expect(screen.getByText("Az ár a fő akadály.")).toBeInTheDocument();
    expect(screen.getByText(`${t.stance.support}: 10`)).toBeInTheDocument();
    expect(screen.getByText(`${t.stance.reject}: 5`)).toBeInTheDocument();
    expect(screen.getByText(`${t.stance.conditional}: 3`)).toBeInTheDocument();
    expect(screen.getByText("18/18 persona válaszolt")).toBeInTheDocument();
    expect(screen.getByText(`${t.retries}: 2`)).toBeInTheDocument();
    expect(screen.getByText("16134")).toBeInTheDocument();
    expect(screen.getByText("36335")).toBeInTheDocument();
    const cost = formatCostUsd(estimateCostUsd(16134, 36335, price));
    expect(screen.getByText(`${cost} (${t.estimate})`)).toBeInTheDocument();

    expect(screen.getByRole("link", { name: t.pdfLink })).toHaveAttribute(
      "href",
      `/api/runs/${RUN_ID}/pdf`
    );
    expect(screen.getByRole("link", { name: t.replayLink })).toHaveAttribute(
      "href",
      `/eredmeny/${RUN_ID}/visszajatszas`
    );
    expect(screen.getByRole("link", { name: t.methodologyLink })).toHaveAttribute(
      "href",
      "/modszertan"
    );
    expect(screen.getByText(t.limitsHeading)).toBeInTheDocument();
  });

  it("shows 16/18 for a partial run with two failed personas", () => {
    const run = makeRun({ status: "partial" });
    run.result = {
      ...run.result!,
      completed_persona_count: 16,
      failed_personas: [
        { name: "A", error_code: "X" },
        { name: "B", error_code: "Y" },
      ],
    };
    render(<ResultView run={run} />);

    expect(screen.getByText("16/18 persona válaszolt")).toBeInTheDocument();
  });

  it("shows the fallback sentence when the synthesis is missing", () => {
    const run = makeRun({ status: "partial" });
    run.result = { ...run.result!, synthesis: null };
    render(<ResultView run={run} />);

    expect(screen.getByText(t.synthesisMissing)).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: t.summaryHeading })).not.toBeInTheDocument();
  });

  it("does not show the persona arguments", () => {
    render(<ResultView run={makeRun()} />);

    expect(screen.queryByText(/TITKOS-ERV-SZOVEG/)).not.toBeInTheDocument();
  });

  it("renders its children in the e-mail slot", () => {
    render(
      <ResultView run={makeRun()}>
        <p>email-urlap-helye</p>
      </ResultView>
    );

    expect(screen.getByText("email-urlap-helye")).toBeInTheDocument();
  });

  it("shows an error panel without the PDF link for a failed run", () => {
    render(<ResultView run={makeRun({ status: "failed", result: null })} />);

    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: t.pdfLink })).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: messages.trace.sampleLink })).toHaveAttribute(
      "href",
      "/minta"
    );
    expect(screen.getByRole("link", { name: messages.trace.formLink })).toBeInTheDocument();
  });

  it("has no critical accessibility violations", async () => {
    const { container } = render(<ResultView run={makeRun()} />);

    const results = await axe(container);
    expect(results.violations.filter((v) => v.impact === "critical")).toEqual([]);
  });
});
