"use client";

import * as React from "react";
import type { CSSProperties } from "react";
import Link from "next/link";
import { QueryClient, QueryClientProvider, useQuery } from "@tanstack/react-query";

import { messages } from "@/lib/messages";
import {
  accent,
  errorDim,
  onPrimary,
  onSurface,
  outlineVariant,
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
  email: string | null;
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

  if (payload.status === "partial" || payload.status === "completed") {
    return {
      label: waiting.states.completed,
      status: payload.status,
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

function WaitingScreenContent({ runId, email, apiBaseUrl }: WaitingScreenProps) {
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
    <div className="relative min-h-screen" style={{ color: onSurface }}>
      <header
        className="sticky top-0 z-40 flex h-20 items-center justify-center border-b"
        style={{ backgroundColor: surfaceContainer, borderColor: outlineVariant }}
      >
        <span className="text-lg font-semibold tracking-tight" style={{ ...headlineFont, color: onSurface }}>
          Swarm<span style={{ color: accent }}>Sense</span>
        </span>
      </header>

      <main className="flex min-h-[calc(100vh-80px)] items-center justify-center px-6 py-16">
      <section className="mx-auto w-full max-w-2xl space-y-10">
        <header className="space-y-3 text-center">
          <p aria-live="polite" className="text-sm md:text-base" style={{ color: textSecondary }}>
            {query.isError ? messages.genericError : uiState.label}
          </p>
        </header>

        <div
          className="rounded-2xl border px-6 py-10 text-center"
          style={{ borderColor: outlineVariant, backgroundColor: surfaceContainerLow }}
        >
          <p className="text-xs uppercase tracking-[0.22em]" style={{ color: textSecondary }}>
            Persona
          </p>
          <p className="mt-4 text-7xl font-semibold md:text-8xl" style={headlineFont}>
            {uiState.status === "running" ? uiState.current : uiState.total}
          </p>
          <p className="mt-2 text-sm" style={{ color: textSecondary }}>
            / {uiState.total}
          </p>
          <div
            className="mt-8 h-3 w-full overflow-hidden rounded-full"
            style={{ backgroundColor: outlineVariant }}
          >
            <div
              role="progressbar"
              aria-label="Elemzés folyamata"
              aria-valuemin={0}
              aria-valuemax={uiState.total}
              aria-valuenow={progressNow}
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${(progressNow / uiState.total) * 100}%`,
                backgroundColor: accent,
              }}
            />
          </div>
        </div>

        {email ? (
          <p className="text-center text-sm" style={{ color: textSecondary }}>
            {interpolate(waiting.emailDeliveryNotice, { email })}
          </p>
        ) : null}

        {showDelayedNotice ? (
          <p className="text-center text-sm" style={{ color: textSecondary }}>
            {waiting.delayedNotice}
          </p>
        ) : null}

        {uiState.status === "failed" ? (
          <div className="space-y-4 text-center">
            <p className="text-sm font-semibold" style={{ color: errorDim }}>
              {waiting.retrySuggestion}
            </p>
            <Link
              href="/research"
              className="inline-flex rounded-lg px-6 py-3 text-sm font-semibold"
              style={{ backgroundColor: accent, color: onPrimary }}
            >
              {messages.research.form.submitCta}
            </Link>
          </div>
        ) : null}
      </section>
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
