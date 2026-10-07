"use client";

import * as React from "react";
import type { CSSProperties } from "react";
import Link from "next/link";
import { AlertTriangle, ArrowRight, CheckCircle2 } from "lucide-react";
import { QueryClient, QueryClientProvider, useQuery } from "@tanstack/react-query";

import { messages } from "@/lib/messages";
import {
  accent,
  errorDim,
  onPrimary,
  onSurface,
  outlineVariant,
  stanceSupport,
  surfaceContainer,
  surfaceContainerLow,
  textSecondary,
} from "@/lib/tokens";

type RunStatus = "queued" | "running" | "composing" | "completed" | "partial" | "failed";

type RunStatusResponse = {
  run_id: string;
  status: RunStatus;
  persona_count: number;
  total_personas: number;
  updated_at: string | null;
};

type WaitingScreenProps = {
  runId: string;
  apiBaseUrl: string;
};

type UiState = {
  label: string;
  status: RunStatus | "generating";
  current: number;
  total: number;
};

const FINAL_STATUSES: RunStatus[] = ["completed", "partial", "failed"];
const headlineFont: CSSProperties = { fontFamily: "var(--font-headline)" };
const labelFont: CSSProperties = { fontFamily: "var(--font-label)" };
function interpolate(template: string, values: Record<string, string | number>): string {
  return Object.entries(values).reduce(
    (text, [key, value]) => text.replaceAll(`{${key}}`, String(value)),
    template
  );
}

function buildUiState(payload: RunStatusResponse | undefined): UiState {
  const waiting = messages.waiting;
  const total = Math.max(1, payload?.total_personas ?? 18);
  const current = Math.min(Math.max(0, payload?.persona_count ?? 0), total);

  if (!payload) {
    return {
      label: waiting.states.generating,
      status: "generating",
      current: 0,
      total,
    };
  }

  if (payload.status === "running" && current === 0) {
    return {
      label: waiting.states.generating,
      status: "generating",
      current: 0,
      total,
    };
  }

  if (payload.status === "running") {
    return {
      label: interpolate(waiting.states.running, { current, total }),
      status: "running",
      current,
      total,
    };
  }

  if (payload.status === "partial") {
    return {
      label: waiting.states.partial,
      status: "partial",
      current: total,
      total,
    };
  }

  if (payload.status === "completed") {
    return {
      label: waiting.states.completed,
      status: "completed",
      current: total,
      total,
    };
  }

  if (payload.status === "failed") {
    return {
      label: waiting.states.failed,
      status: "failed",
      current,
      total,
    };
  }

  if (payload.status === "queued") {
    return {
      label: waiting.states.queued,
      status: "queued",
      current,
      total,
    };
  }

  return {
    label: waiting.states.composing,
    status: payload.status,
    current,
    total,
  };
}

function WaitingScreenContent({ runId, apiBaseUrl }: WaitingScreenProps) {
  const waiting = messages.waiting;
  const [showDelayedNotice, setShowDelayedNotice] = React.useState(false);
  const hasShownNoticeRef = React.useRef(false);

  const normalizedApiBaseUrl = apiBaseUrl.replace(/\/$/, "");

  const query = useQuery<RunStatusResponse>({
    queryKey: ["run-status", runId, normalizedApiBaseUrl],
    queryFn: async () => {
      if (!normalizedApiBaseUrl) {
        throw new Error("API base URL is not configured");
      }
      const endpoint = `${normalizedApiBaseUrl}/api/v1/runs/${encodeURIComponent(runId)}/status`;
      const response = await fetch(endpoint, { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`Status polling failed: ${response.status}`);
      }

      return (await response.json()) as RunStatusResponse;
    },
    refetchInterval: (queryState) => {
      const currentStatus = (queryState.state.data as RunStatusResponse | undefined)?.status;
      return currentStatus && FINAL_STATUSES.includes(currentStatus) ? false : 5000;
    },
  });

  const uiState = buildUiState(query.data);
  const isFinal = uiState.status !== "generating" && FINAL_STATUSES.includes(uiState.status);
  const isCompleted = uiState.status === "completed";
  const isPartial = uiState.status === "partial";
  const isFailed = uiState.status === "failed";

  const progressFillColor = isCompleted ? stanceSupport : isFailed ? errorDim : accent;

  React.useEffect(() => {
    if (isFinal) {
      setShowDelayedNotice(false);
      return;
    }

    if (hasShownNoticeRef.current) {
      setShowDelayedNotice(true);
      return;
    }

    const timeout = window.setTimeout(() => {
      hasShownNoticeRef.current = true;
      setShowDelayedNotice(true);
    }, 120_000);

    return () => window.clearTimeout(timeout);
  }, [isFinal]);

  const progressNow = Math.min(Math.max(0, uiState.current), uiState.total);

  return (
    <div className="relative min-h-dvh" style={{ color: onSurface }}>
      <header
        className="sticky top-0 z-40 flex h-20 items-center justify-center border-b"
        style={{ backgroundColor: surfaceContainer, borderColor: outlineVariant }}
      >
        <span className="text-lg font-semibold tracking-tight" style={{ ...headlineFont, color: onSurface }}>
          Swarm<span style={{ color: accent }}>Sense</span>
        </span>
      </header>

      <main className="flex min-h-[calc(100dvh-80px)] items-center justify-center px-6 py-24">
        <div className="w-full max-w-[600px] space-y-12">
          <section className="space-y-8">
            <div className="space-y-4">
              <span className="text-xs uppercase tracking-[0.3em]" style={{ color: textSecondary, ...labelFont }}>
                {waiting.eyebrow}
              </span>
              <h1
                aria-live="polite"
                className="text-3xl font-semibold md:text-4xl"
                style={{ ...headlineFont, color: onSurface }}
              >
                {query.isError ? messages.genericError : uiState.label}
              </h1>
              {query.isError ? null : (
                <p className="text-sm leading-relaxed" style={{ color: textSecondary }}>
                  {waiting.subheadline}
                </p>
              )}
            </div>

            <div className="space-y-3">
              <p
                className="text-xs uppercase tracking-[0.2em]"
                style={{ color: textSecondary, ...labelFont }}
              >
                {waiting.personaSectionLabel}
              </p>
              <div
                className="relative overflow-hidden rounded-lg px-5 py-8 text-center md:py-10"
                style={{ backgroundColor: surfaceContainerLow }}
              >
                <div className="flex flex-col items-center justify-center gap-3">
                  {isCompleted ? (
                    <CheckCircle2
                      className="h-12 w-12 md:h-14 md:w-14"
                      style={{ color: stanceSupport }}
                      strokeWidth={1.25}
                      aria-hidden="true"
                    />
                  ) : null}
                  {isPartial ? (
                    <AlertTriangle
                      className="h-12 w-12 md:h-14 md:w-14"
                      style={{ color: accent }}
                      strokeWidth={1.25}
                      aria-hidden="true"
                    />
                  ) : null}
                  {isCompleted ? (
                    <p className="text-sm font-medium" style={{ color: stanceSupport }}>
                      {waiting.completedStatusHint}
                    </p>
                  ) : null}
                  {isPartial ? (
                    <p className="text-sm font-medium" style={{ color: textSecondary }}>
                      {waiting.partialStatusHint}
                    </p>
                  ) : null}

                  <p
                    className="text-6xl font-semibold tabular-nums tracking-tight md:text-7xl"
                    style={headlineFont}
                    aria-live="polite"
                  >
                    {uiState.current}
                  </p>
                  <p className="text-sm tabular-nums" style={{ color: textSecondary }}>
                    / {uiState.total}
                  </p>
                </div>

                <div
                  className="mt-8 h-2.5 w-full overflow-hidden rounded-full"
                  style={{ backgroundColor: outlineVariant }}
                >
                  <div
                    role="progressbar"
                    aria-label={waiting.progressAriaLabel}
                    aria-valuemin={0}
                    aria-valuemax={uiState.total}
                    aria-valuenow={progressNow}
                    className="h-full rounded-full transition-all duration-700 ease-out"
                    style={{
                      width: `${(progressNow / uiState.total) * 100}%`,
                      backgroundColor: progressFillColor,
                    }}
                  />
                </div>
              </div>
            </div>

            {showDelayedNotice ? (
              <div className="rounded-lg border-l-2 px-5 py-4" style={{ borderColor: accent, backgroundColor: surfaceContainerLow }}>
                <p className="text-sm leading-relaxed" style={{ color: textSecondary }}>
                  {waiting.delayedNotice}
                </p>
              </div>
            ) : null}

            {uiState.status === "failed" ? (
              <div className="space-y-3">
                <p className="text-center text-sm font-semibold" style={{ color: errorDim }}>
                  {waiting.retrySuggestion}
                </p>
                <Link
                  href="/research"
                  className="flex w-full items-center justify-center gap-3 rounded-lg px-6 py-4 text-base font-semibold transition-all hover:opacity-90 active:scale-[0.98]"
                  style={{ backgroundColor: accent, color: onPrimary, ...headlineFont }}
                >
                  {messages.research.form.submitCta}
                  <ArrowRight className="h-4 w-4" aria-hidden="true" />
                </Link>
              </div>
            ) : null}
          </section>
        </div>
      </main>

      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-0 -z-10 overflow-hidden"
      >
        <div
          className="absolute right-[-10%] top-[-10%] h-[520px] w-[520px] rounded-full blur-[120px]"
          style={{ backgroundColor: accent, opacity: 0.1 }}
        />
        <div
          className="absolute bottom-[-5%] left-[-5%] h-[420px] w-[420px] rounded-full blur-[100px]"
          style={{ backgroundColor: accent, opacity: 0.06 }}
        />
      </div>
    </div>
  );
}

export function WaitingScreen(props: WaitingScreenProps) {
  const [queryClient] = React.useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <WaitingScreenContent {...props} />
    </QueryClientProvider>
  );
}
