import type { CSSProperties, ReactNode } from "react";
import { Check } from "lucide-react";

import { estimateCostUsd, formatCostUsd, type Price } from "@/lib/cost";
import { messages } from "@/lib/messages";
import {
  accent,
  errorDim,
  onSurface,
  outlineVariant,
  stanceSupport,
  surfaceContainer,
  surfaceContainerLow,
  textSecondary,
} from "@/lib/tokens";
import {
  countByStatus,
  MAX_ATTEMPTS,
  TOTAL_PERSONAS,
  type PersonaRow,
  type TracePhase,
  type TraceState,
} from "@/lib/trace";

type TraceViewProps = {
  topic: string;
  state: TraceState;
  /** Ezredmásodperc; a futó sorok és a fejléc órája ebből számol. */
  now: number;
  price: Price;
  banner?: ReactNode;
};

const t = messages.trace;
const headlineFont: CSSProperties = { fontFamily: "var(--font-headline)" };
const labelFont: CSSProperties = { fontFamily: "var(--font-label)" };

const PHASE_STEPS: { phase: TracePhase; label: string }[] = [
  { phase: "generating", label: t.phases.generating },
  { phase: "personas", label: t.phases.personas },
  { phase: "synthesis", label: t.phases.synthesis },
  { phase: "pdf", label: t.phases.pdf },
];

// A lépés sorszáma, amelynél a futás jelenleg tart; végállapotban mind kész.
function currentStep(phase: TracePhase): number {
  if (phase === "done") return PHASE_STEPS.length;
  const index = PHASE_STEPS.findIndex((step) => step.phase === phase);
  return index; // waiting és failed: nincs kiemelt lépés
}

export function formatDuration(ms: number): string {
  const totalSeconds = Math.max(0, Math.floor(ms / 1000));
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${String(seconds).padStart(2, "0")}`;
}

function elapsedMs(state: TraceState, now: number): number {
  if (!state.startedAt) return 0;
  const end = state.endedAt ? Date.parse(state.endedAt) : now;
  return end - Date.parse(state.startedAt);
}

function rowElapsed(row: PersonaRow, now: number): string {
  if (row.durationMs !== null) return formatDuration(row.durationMs);
  return formatDuration(now - Date.parse(row.startedAt));
}

function rowStatusColor(status: PersonaRow["status"]): string {
  if (status === "completed") return stanceSupport;
  if (status === "failed") return errorDim;
  return accent;
}

function PersonaListItem({ row, now }: { row: PersonaRow; now: number }) {
  return (
    <li
      className="flex flex-wrap items-center gap-x-4 gap-y-1 rounded-md px-4 py-3 text-sm"
      style={{ backgroundColor: surfaceContainerLow }}
    >
      <span className="min-w-0 flex-1 truncate font-semibold" style={{ color: onSurface }}>
        {row.name}
      </span>
      <span style={{ color: rowStatusColor(row.status), ...labelFont }}>{t.row[row.status]}</span>
      <span style={{ color: textSecondary, ...labelFont }}>{rowElapsed(row, now)}</span>
      <span style={{ color: textSecondary, ...labelFont }}>
        {t.row.attemptLabel} {row.attempt}/{MAX_ATTEMPTS}
      </span>
      {row.errorCode ? (
        <span style={{ color: errorDim, ...labelFont }}>{row.errorCode}</span>
      ) : null}
    </li>
  );
}

function QueuedListItem() {
  return (
    <li
      className="flex items-center rounded-md px-4 py-3 text-sm"
      style={{ backgroundColor: surfaceContainerLow, color: textSecondary, ...labelFont }}
    >
      {t.row.queued}
    </li>
  );
}

export function TraceView({ topic, state, now, price, banner }: TraceViewProps) {
  const counts = countByStatus(state);
  const step = currentStep(state.phase);
  const cost = estimateCostUsd(state.inputTokens, state.outputTokens, price);
  const showQueuedRows =
    state.phase === "waiting" || state.phase === "generating" || state.phase === "personas";

  const rows = Array.from({ length: TOTAL_PERSONAS }, (_, index) =>
    state.personas.find((row) => row.index === index)
  );

  const summary: { label: string; value: string }[] = [
    { label: t.summary.queued, value: String(counts.queued) },
    { label: t.summary.running, value: String(counts.running) },
    { label: t.summary.completed, value: String(counts.completed) },
    { label: t.summary.failed, value: String(counts.failed) },
    { label: t.summary.inputTokens, value: String(state.inputTokens) },
    { label: t.summary.outputTokens, value: String(state.outputTokens) },
    { label: `${t.summary.cost} (${t.summary.estimate})`, value: formatCostUsd(cost) },
  ];

  return (
    <div className="mx-auto w-full max-w-3xl space-y-8 px-6 py-12" style={{ color: onSurface }}>
      <header className="space-y-4">
        <span
          className="text-xs uppercase tracking-[0.3em]"
          style={{ color: textSecondary, ...labelFont }}
        >
          {t.eyebrow}
        </span>
        <h1 className="text-2xl font-semibold md:text-3xl" style={headlineFont}>
          {topic}
        </h1>
        <p className="text-sm" style={{ color: textSecondary, ...labelFont }}>
          {t.elapsedLabel}: <span style={{ color: onSurface }}>{formatDuration(elapsedMs(state, now))}</span>
        </p>
        <ol aria-label={t.phasesAriaLabel} className="flex flex-wrap gap-x-6 gap-y-2 text-sm">
          {PHASE_STEPS.map((phaseStep, index) => {
            const done = index < step;
            const current = index === step;
            return (
              <li
                key={phaseStep.phase}
                aria-current={current ? "step" : undefined}
                className="flex items-center gap-2"
                style={{
                  color: current ? accent : done ? onSurface : textSecondary,
                  fontWeight: current ? 600 : 400,
                }}
              >
                {done ? <Check className="h-4 w-4" aria-hidden="true" /> : null}
                {phaseStep.label}
              </li>
            );
          })}
        </ol>
      </header>

      {banner}
      {state.synthesisFailed ? (
        <p className="text-sm" style={{ color: errorDim }}>
          {t.synthesisFailedNotice}
        </p>
      ) : null}

      <dl
        aria-label={t.summaryAriaLabel}
        className="grid grid-cols-2 gap-3 rounded-lg p-4 sm:grid-cols-4"
        style={{ backgroundColor: surfaceContainer, border: `1px solid ${outlineVariant}` }}
      >
        {summary.map((item) => (
          <div key={item.label} className="space-y-1">
            <dt className="text-xs" style={{ color: textSecondary, ...labelFont }}>
              {item.label}
            </dt>
            <dd className="text-lg font-semibold" style={headlineFont}>
              {item.value}
            </dd>
          </div>
        ))}
      </dl>

      <ul aria-label={t.personasAriaLabel} className="grid grid-cols-1 gap-2">
        {rows.map((row, index) =>
          row ? (
            <PersonaListItem key={index} row={row} now={now} />
          ) : showQueuedRows ? (
            <QueuedListItem key={index} />
          ) : null
        )}
      </ul>
    </div>
  );
}
