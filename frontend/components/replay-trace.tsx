"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { TraceView } from "@/components/trace-view";
import type { Price } from "@/lib/cost";
import { messages } from "@/lib/messages";
import { buildSchedule, type ScheduledEvent } from "@/lib/replay";
import { accent, errorDim, onSurface, textSecondary } from "@/lib/tokens";
import { applyEvent, initialTraceState, type TraceEvent, type TraceState } from "@/lib/trace";

const CLOCK_INTERVAL_MS = 1000;
const NO_PRICE: Price = { input_per_million_usd: 0, output_per_million_usd: 0 };
const FINISHED_STATUSES = ["completed", "partial", "failed"];

type EventsResponse = {
  status?: string;
  topic?: string;
  created_at?: string;
  price?: Price;
  events?: TraceEvent[];
};

type Recording = {
  topic: string;
  price: Price;
  createdAt: string;
  schedule: ScheduledEvent[];
};

function formatRunDate(iso: string): string {
  return new Date(iso).toLocaleDateString("hu-HU", {
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "Europe/Budapest",
  });
}

const t = messages.replay;
const linkClass = "underline underline-offset-4";

export function ReplayTrace({ runId }: { runId: string }) {
  const router = useRouter();
  const routerRef = React.useRef(router);
  React.useEffect(() => {
    routerRef.current = router;
  }, [router]);

  const [recording, setRecording] = React.useState<Recording | null>(null);
  const [failed, setFailed] = React.useState(false);
  const [state, setState] = React.useState<TraceState>(initialTraceState);
  const [now, setNow] = React.useState(() => Date.now());
  const [finished, setFinished] = React.useState(false);
  const [playKey, setPlayKey] = React.useState(0);
  const virtualNowRef = React.useRef<() => number>(() => Date.now());

  // Egyszeri lekérés: a teljes eseménysort egyben kapjuk meg.
  React.useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const response = await fetch(`/api/runs/${runId}/events?after=0`, { cache: "no-store" });
        if (cancelled) return;
        if (!response.ok) {
          setFailed(true);
          return;
        }
        const data = (await response.json()) as EventsResponse;
        if (cancelled) return;
        if (!data.status || !FINISHED_STATUSES.includes(data.status)) {
          routerRef.current.replace(`/waiting/${runId}`);
          return;
        }
        setRecording({
          topic: data.topic ?? "",
          price: data.price ?? NO_PRICE,
          createdAt: data.created_at ?? "",
          schedule: buildSchedule(data.events ?? []),
        });
      } catch {
        if (!cancelled) setFailed(true);
      }
    };
    void load();
    return () => {
      cancelled = true;
    };
  }, [runId]);

  // Lejátszás: minden esemény a saját késleltetésével, a virtuális óra az első esemény
  // időbélyegétől a lejátszás kezdete óta eltelt valós idővel halad.
  React.useEffect(() => {
    if (!recording) return;
    const { schedule } = recording;
    const virtualStart = schedule.length > 0 ? Date.parse(schedule[0].event.at) : Date.now();
    const realStart = Date.now();
    const virtualNow = () => virtualStart + (Date.now() - realStart);
    virtualNowRef.current = virtualNow;
    let current = initialTraceState();
    const timers: ReturnType<typeof setTimeout>[] = [];

    schedule.forEach(({ event, delayMs }, index) => {
      timers.push(
        setTimeout(() => {
          current = applyEvent(current, event);
          setState(current);
          setNow(virtualNow());
          if (index === schedule.length - 1) setFinished(true);
        }, delayMs)
      );
    });
    if (schedule.length === 0) timers.push(setTimeout(() => setFinished(true), 0));

    return () => timers.forEach(clearTimeout);
  }, [recording, playKey]);

  // A virtuális óra a lejátszás végén megáll.
  React.useEffect(() => {
    if (!recording || finished) return;
    const clock = setInterval(() => setNow(virtualNowRef.current()), CLOCK_INTERVAL_MS);
    return () => clearInterval(clock);
  }, [recording, finished, playKey]);

  const restart = () => {
    setState(initialTraceState());
    setFinished(false);
    setPlayKey((key) => key + 1);
  };

  if (failed) {
    return (
      <div className="mx-auto w-full max-w-3xl space-y-6 px-6 py-12" style={{ color: onSurface }}>
        <p role="alert" className="text-lg font-semibold" style={{ color: errorDim }}>
          {t.error}
        </p>
        <Link href="/research" style={{ color: accent }} className={`text-sm font-semibold ${linkClass}`}>
          {messages.trace.formLink}
        </Link>
      </div>
    );
  }

  const banner = (
    <div className="flex flex-wrap items-center gap-x-6 gap-y-3 text-sm">
      {recording ? (
        <span style={{ color: textSecondary }}>
          {t.recorded}, {formatRunDate(recording.createdAt)}
        </span>
      ) : null}
      <Link href={`/eredmeny/${runId}`} style={{ color: accent }} className={`font-semibold ${linkClass}`}>
        {t.jumpToResult}
      </Link>
      {finished ? (
        <button
          type="button"
          onClick={restart}
          className="font-semibold underline underline-offset-4"
          style={{ color: accent }}
        >
          {t.again}
        </button>
      ) : null}
    </div>
  );

  return (
    <TraceView
      topic={recording?.topic ?? ""}
      state={state}
      now={now}
      price={recording?.price ?? NO_PRICE}
      banner={banner}
      eyebrow={t.eyebrow}
    />
  );
}
