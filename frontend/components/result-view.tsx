import type { CSSProperties, ReactNode } from "react";
import Link from "next/link";

import { estimateCostUsd, formatCostUsd } from "@/lib/cost";
import { messages } from "@/lib/messages";
import type { RunDetail } from "@/lib/run";
import {
  accent,
  errorDim,
  onSurface,
  outlineVariant,
  stanceConditional,
  stanceReject,
  stanceSupport,
  surfaceContainer,
  surfaceContainerHigh,
  textSecondary,
} from "@/lib/tokens";

type ResultViewProps = {
  run: RunDetail;
  /** A 7. feladat e-mail-űrlapjának helye. */
  children?: ReactNode;
};

const t = messages.result;
const headlineFont: CSSProperties = { fontFamily: "var(--font-headline)" };
const labelFont: CSSProperties = { fontFamily: "var(--font-label)" };
const linkClass = "underline underline-offset-4";

const STANCES = [
  { key: "support", label: t.stance.support, color: stanceSupport },
  { key: "reject", label: t.stance.reject, color: stanceReject },
  { key: "conditional", label: t.stance.conditional, color: stanceConditional },
] as const;

function Shell({ children }: { children: ReactNode }) {
  return (
    <div className="mx-auto w-full max-w-3xl space-y-8 px-6 py-12" style={{ color: onSurface }}>
      {children}
    </div>
  );
}

function Header({ run }: { run: RunDetail }) {
  return (
    <header className="space-y-3">
      <span
        className="text-xs uppercase tracking-[0.3em]"
        style={{ color: textSecondary, ...labelFont }}
      >
        {t.eyebrow}
      </span>
      <h1 className="text-2xl font-semibold md:text-3xl" style={headlineFont}>
        {run.topic}
      </h1>
      <p className="text-sm" style={{ color: textSecondary, ...labelFont }}>
        {t.audienceLabel}: <span style={{ color: onSurface }}>{run.audience}</span>
      </p>
    </header>
  );
}

function FailedPanel({ run }: { run: RunDetail }) {
  return (
    <Shell>
      <Header run={run} />
      <div
        role="alert"
        className="space-y-3 rounded-lg p-4"
        style={{ border: `1px solid ${errorDim}` }}
      >
        <p className="font-semibold" style={{ color: errorDim }}>
          {t.failedHeading}
        </p>
        <p className="text-sm">{t.failedFallback}</p>
        <div className="flex flex-wrap gap-6 text-sm font-semibold">
          <Link href="/minta" style={{ color: accent }} className={linkClass}>
            {messages.trace.sampleLink}
          </Link>
          <Link href="/research" style={{ color: accent }} className={linkClass}>
            {messages.trace.formLink}
          </Link>
        </div>
      </div>
    </Shell>
  );
}

export function ResultView({ run, children }: ResultViewProps) {
  const result = run.result;
  if (run.status === "failed" || result === null) {
    return <FailedPanel run={run} />;
  }

  const cost = estimateCostUsd(run.input_tokens, run.output_tokens, run.price);
  const counts = result.stance_counts;
  const total = counts.support + counts.reject + counts.conditional;
  const runData: { label: string; value: string }[] = [
    {
      label: t.duration,
      value: run.duration_ms === null ? "-" : `${Math.round(run.duration_ms / 1000)} ${t.seconds}`,
    },
    { label: t.inputTokens, value: String(run.input_tokens) },
    { label: t.outputTokens, value: String(run.output_tokens) },
    { label: t.cost, value: `${formatCostUsd(cost)} (${t.estimate})` },
  ];

  return (
    <Shell>
      <Header run={run} />

      {result.synthesis ? (
        <section className="space-y-3">
          <h2 className="text-xl font-semibold" style={headlineFont}>
            {t.summaryHeading}
          </h2>
          <p className="leading-relaxed">{result.synthesis.summary}</p>
        </section>
      ) : (
        <p className="leading-relaxed" style={{ color: textSecondary }}>
          {t.synthesisMissing}
        </p>
      )}

      <section className="space-y-3">
        <h2 className="text-xl font-semibold" style={headlineFont}>
          {t.stanceHeading}
        </h2>
        <ul className="space-y-3">
          {STANCES.map(({ key, label, color }) => {
            const count = counts[key];
            const share = total > 0 ? (count / total) * 100 : 0;
            return (
              <li key={key} className="space-y-1">
                <span className="text-sm" style={labelFont}>{`${label}: ${count}`}</span>
                <div
                  aria-hidden="true"
                  className="h-2 w-full overflow-hidden rounded-full"
                  style={{ backgroundColor: surfaceContainerHigh }}
                >
                  <div
                    className="h-full rounded-full"
                    style={{ width: `${share}%`, backgroundColor: color }}
                  />
                </div>
              </li>
            );
          })}
        </ul>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold" style={headlineFont}>
          {t.runDataHeading}
        </h2>
        <dl
          className="grid grid-cols-2 gap-3 rounded-lg p-4 sm:grid-cols-4"
          style={{ backgroundColor: surfaceContainer, border: `1px solid ${outlineVariant}` }}
        >
          {runData.map((item) => (
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
        <p className="text-sm" style={labelFont}>
          {`${result.completed_persona_count}/${result.total_persona_count} ${t.personasAnswered}`}
        </p>
        <p className="text-sm" style={{ color: textSecondary, ...labelFont }}>
          {`${t.retries}: ${run.retry_count}`}
        </p>
        <Link
          href={`/eredmeny/${run.run_id}/visszajatszas`}
          className={`text-sm font-semibold ${linkClass}`}
          style={{ color: accent }}
        >
          {t.replayLink}
        </Link>
      </section>

      <div>
        {/* sima <a>: a letöltés route handler, nem oldal, a Link előbetöltené */}
        <a
          href={`/api/runs/${run.run_id}/pdf`}
          className="inline-block rounded-md px-5 py-3 text-sm font-semibold"
          style={{ backgroundColor: accent, color: "#5c3800" }}
        >
          {t.pdfLink}
        </a>
      </div>

      {children}

      <section className="space-y-2">
        <h2 className="text-lg font-semibold" style={headlineFont}>
          {t.limitsHeading}
        </h2>
        <p className="text-sm leading-relaxed" style={{ color: textSecondary }}>
          {t.limitsText}
        </p>
        <Link
          href="/modszertan"
          className={`text-sm font-semibold ${linkClass}`}
          style={{ color: accent }}
        >
          {t.methodologyLink}
        </Link>
      </section>
    </Shell>
  );
}
