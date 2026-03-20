"use client";

import * as React from "react";
import type { CSSProperties } from "react";

import { joinWaitlistAction } from "@/app/actions/join-waitlist";
import { messages } from "@/lib/messages";
import {
  accent,
  onPrimary,
  onSurface,
  outlineVariant,
  surfaceContainer,
  surfaceContainerHigh,
  surfaceContainerLow,
  textSecondary,
} from "@/lib/tokens";

type BlockingScreenProps = {
  email: string | null;
  canSubmitWaitlist: boolean;
};

type BlockingState = "default" | "waitlist-submitted";

const headlineFont: CSSProperties = { fontFamily: "var(--font-headline)" };
const labelFont: CSSProperties = { fontFamily: "var(--font-label)" };

export function BlockingScreen({ email, canSubmitWaitlist }: BlockingScreenProps) {
  const [state, setState] = React.useState<BlockingState>("default");
  const [error, setError] = React.useState<string | null>(null);
  const [isSubmitting, startTransition] = React.useTransition();

  const { blockingScreen } = messages;

  const handleSubmit = () => {
    if (!canSubmitWaitlist || !email) {
      return;
    }

    setError(null);

    startTransition(async () => {
      const result = await joinWaitlistAction({ email });

      if (!result.ok) {
        setError(result.message);
        return;
      }

      setState("waitlist-submitted");
    });
  };

  return (
    <main
      role="main"
      className="relative flex min-h-screen items-center justify-center overflow-hidden px-6 py-16"
      style={{ color: onSurface }}
    >
      <section
        className="relative z-10 w-full max-w-2xl space-y-7 rounded-2xl border p-8 md:p-10"
        style={{ backgroundColor: surfaceContainerHigh, borderColor: outlineVariant }}
      >
        <div className="space-y-4">
          <h1 className="text-3xl font-semibold md:text-4xl" style={headlineFont}>
            {blockingScreen.heading}
          </h1>
          <p className="text-sm leading-relaxed md:text-base" style={{ color: textSecondary }}>
            {blockingScreen.body}
          </p>
          {canSubmitWaitlist ? (
            <p className="text-xs" style={{ color: textSecondary, ...labelFont }}>
              {blockingScreen.emailPrefix} <strong>{email}</strong>
            </p>
          ) : (
            <p className="text-xs" style={{ color: textSecondary, ...labelFont }}>
              {blockingScreen.invalidEmail}
            </p>
          )}
        </div>

        {state === "default" ? (
          <div className="space-y-3">
            <button
              type="button"
              onClick={handleSubmit}
              className="inline-flex w-full items-center justify-center rounded-lg px-6 py-4 text-base font-semibold transition-transform active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60"
              style={{ backgroundColor: accent, color: onPrimary, ...headlineFont }}
              disabled={!canSubmitWaitlist || isSubmitting}
              aria-disabled={!canSubmitWaitlist || isSubmitting ? "true" : undefined}
            >
              {blockingScreen.cta}
            </button>
            {error ? (
              <p className="text-sm" style={{ color: textSecondary }}>
                {error}
              </p>
            ) : null}
          </div>
        ) : (
          <p className="rounded-lg px-4 py-3 text-sm" style={{ backgroundColor: surfaceContainerLow }}>
            {blockingScreen.submitted}
          </p>
        )}
      </section>

      <div aria-hidden="true" className="pointer-events-none fixed inset-0 -z-10">
        <div
          className="absolute right-[-10%] top-[-10%] h-[420px] w-[420px] rounded-full blur-[120px]"
          style={{ backgroundColor: accent, opacity: 0.12 }}
        />
        <div
          className="absolute bottom-[-10%] left-[-10%] h-[360px] w-[360px] rounded-full blur-[100px]"
          style={{ backgroundColor: surfaceContainer, opacity: 0.9 }}
        />
      </div>
    </main>
  );
}
