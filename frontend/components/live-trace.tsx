"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { TraceView } from "@/components/trace-view";
import type { Price } from "@/lib/cost";
import { getErrorMessageByCode } from "@/lib/errors";
import { messages } from "@/lib/messages";
import { accent, errorDim, onSurface } from "@/lib/tokens";
import { applyEvent, initialTraceState, type TraceEvent, type TraceState } from "@/lib/trace";

const POLL_INTERVAL_MS = 1000;
const MAX_CONSECUTIVE_FAILURES = 3;
const NO_PRICE: Price = { input_per_million_usd: 0, output_per_million_usd: 0 };

type EventsResponse = {
  topic?: string;
  price?: Price;
  events?: TraceEvent[];
};

type StopReason = "connection" | "not_found" | null;

function isTerminal(state: TraceState, stop: StopReason): boolean {
  return state.phase === "done" || state.phase === "failed" || stop !== null;
}

function NavLinks({ showSample = true, showForm = true }: { showSample?: boolean; showForm?: boolean }) {
  const t = messages.trace;
  return (
    <div className="flex flex-wrap gap-6 text-sm font-semibold">
      {showSample ? (
        <Link href="/minta" style={{ color: accent }} className="underline underline-offset-4">
          {t.sampleLink}
        </Link>
      ) : null}
      {showForm ? (
        <Link href="/research" style={{ color: accent }} className="underline underline-offset-4">
          {t.formLink}
        </Link>
      ) : null}
    </div>
  );
}

export function LiveTrace({ runId }: { runId: string }) {
  const router = useRouter();
  // A router a pollingciklusban csak az átirányításhoz kell; ref-ben tartjuk, hogy a
  // ciklus ne induljon újra, ha az objektum azonossága renderenként változna.
  const routerRef = React.useRef(router);
  React.useEffect(() => {
    routerRef.current = router;
  }, [router]);
  const [state, setState] = React.useState<TraceState>(initialTraceState);
  const [topic, setTopic] = React.useState("");
  const [price, setPrice] = React.useState<Price>(NO_PRICE);
  const [stop, setStop] = React.useState<StopReason>(null);
  const [now, setNow] = React.useState(() => Date.now());

  React.useEffect(() => {
    let cancelled = false;
    let stopped = false;
    let inFlight = false;
    let failures = 0;
    let current = initialTraceState();
    let timer: ReturnType<typeof setTimeout> | undefined;

    const halt = (reason: StopReason) => {
      stopped = true;
      clearTimeout(timer);
      if (reason) setStop(reason);
    };

    const recordFailure = () => {
      failures += 1;
      if (failures >= MAX_CONSECUTIVE_FAILURES) halt("connection");
    };

    const poll = async () => {
      if (cancelled || stopped || inFlight) return;
      inFlight = true;
      clearTimeout(timer);
      try {
        const response = await fetch(`/api/runs/${runId}/events?after=${current.lastEventId}`, {
          cache: "no-store",
        });
        if (cancelled) return;
        if (response.status === 404) {
          halt("not_found");
        } else if (!response.ok) {
          recordFailure();
        } else {
          const data = (await response.json()) as EventsResponse;
          if (cancelled) return;
          failures = 0;
          current = (data.events ?? []).reduce(applyEvent, current);
          setState(current);
          if (typeof data.topic === "string") setTopic(data.topic);
          if (data.price) setPrice(data.price);
          setNow(Date.now());
          if (current.phase === "done") {
            halt(null);
            routerRef.current.replace(`/eredmeny/${runId}`);
          } else if (current.phase === "failed") {
            halt(null);
          }
        }
      } catch {
        if (cancelled) return;
        recordFailure();
      } finally {
        inFlight = false;
      }
      if (!cancelled && !stopped) {
        timer = setTimeout(poll, POLL_INTERVAL_MS);
      }
    };

    const onVisibility = () => {
      if (document.visibilityState === "visible") void poll();
    };

    document.addEventListener("visibilitychange", onVisibility);
    void poll();

    return () => {
      cancelled = true;
      clearTimeout(timer);
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, [runId]);

  const terminal = isTerminal(state, stop);
  React.useEffect(() => {
    if (terminal) return;
    const interval = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(interval);
  }, [terminal]);

  const t = messages.trace;

  if (stop === "not_found") {
    return (
      <div className="mx-auto w-full max-w-3xl space-y-6 px-6 py-12" style={{ color: onSurface }}>
        <p role="alert" className="text-lg font-semibold" style={{ color: errorDim }}>
          {t.notFound}
        </p>
        <NavLinks showSample={false} />
      </div>
    );
  }

  let banner: React.ReactNode = null;
  if (state.phase === "failed") {
    banner = (
      <div role="alert" className="space-y-3 rounded-lg p-4" style={{ border: `1px solid ${errorDim}` }}>
        <p className="font-semibold" style={{ color: errorDim }}>
          {t.failedHeading}
        </p>
        <p className="text-sm">{getErrorMessageByCode(state.failureCode ?? "INTERNAL_ERROR")}</p>
        <NavLinks />
      </div>
    );
  } else if (stop === "connection") {
    banner = (
      <div role="alert" className="space-y-3 rounded-lg p-4" style={{ border: `1px solid ${errorDim}` }}>
        <p className="text-sm font-semibold" style={{ color: errorDim }}>
          {t.connectionLost}
        </p>
        <NavLinks showForm={false} />
      </div>
    );
  }

  return <TraceView topic={topic} state={state} now={now} price={price} banner={banner} />;
}
