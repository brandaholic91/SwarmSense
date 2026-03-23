"use client";

import * as React from "react";
import type { CSSProperties } from "react";
import Link from "next/link";
import { Loader2, Send, ShieldCheck } from "lucide-react";
import { useSearchParams } from "next/navigation";

import { submitRunAction } from "@/app/actions/submit-run";
import { Input } from "@/components/ui/input";
import { messages } from "@/lib/messages";
import {
  accent,
  onPrimary,
  onSurface,
  outlineVariant,
  surfaceContainer,
  surfaceContainerHigh,
  surfaceContainerLow,
  errorDim,
  textSecondary,
} from "@/lib/tokens";

const headlineFont: CSSProperties = { fontFamily: "var(--font-headline)" };
const labelFont: CSSProperties = { fontFamily: "var(--font-label)" };
const focusLineStyle = {
  "--focus-color": accent,
  "--base-color": outlineVariant,
} as CSSProperties;

export default function ResearchEmailPage() {
  return (
    <React.Suspense fallback={null}>
      <ResearchEmailContent />
    </React.Suspense>
  );
}

function ResearchEmailContent() {
  const { form } = messages.research;
  const copy = form.email;
  const searchParams = useSearchParams();
  const topic = searchParams.get("topic") ?? "";
  const audience = searchParams.get("audience") ?? "";

  const [email, setEmail] = React.useState("");
  const [hasConsent, setHasConsent] = React.useState(false);
  const [isSubmitting, startTransition] = React.useTransition();
  const [error, setError] = React.useState<string | undefined>();

  const canSubmit = email.trim().length > 0 && hasConsent && !isSubmitting;

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = email.trim();
    if (!trimmed || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
      setError(form.errors.email);
      return;
    }
    if (!hasConsent) return;

    setError(undefined);
    startTransition(async () => {
      try {
        const result = await submitRunAction({
          email: trimmed,
          hasConsent: true,
          consentTimestamp: new Date().toISOString(),
          topic,
          audience,
        });
        window.location.assign(result.redirectTo);
      } catch (err) {
        setError(messages.genericError);
      }
    });
  };

  return (
    <div className="relative min-h-dvh" style={{ color: onSurface }}>
      <header
        className="sticky top-0 z-40 flex h-20 items-center justify-center border-b"
        style={{ backgroundColor: surfaceContainer, borderColor: outlineVariant }}
      >
        <span
          className="text-lg font-semibold tracking-tight"
          style={{ ...headlineFont, color: onSurface }}
        >
          Swarm<span style={{ color: accent }}>Sense</span>
        </span>
      </header>

      <main className="flex min-h-[calc(100dvh-80px)] items-center justify-center px-6 py-24">
        <div className="w-full max-w-[600px] space-y-12">
          <section className="space-y-8">
            <div className="space-y-4">
              <span
                className="text-xs uppercase tracking-[0.3em]"
                style={{ color: textSecondary, ...labelFont }}
              >
                {form.eyebrow}
              </span>
              <h1
                className="text-3xl font-semibold md:text-4xl"
                style={{ ...headlineFont, color: onSurface }}
              >
                {copy.heading}
              </h1>
              <p className="text-sm leading-relaxed" style={{ color: textSecondary }}>
                {copy.subheadline}
              </p>
            </div>

            <form
              className="space-y-6 rounded-lg px-5 py-8 md:px-6 md:py-10"
              style={{ backgroundColor: surfaceContainerLow }}
              onSubmit={handleSubmit}
            >
              <div className="space-y-3">
                <label
                  className="text-xs uppercase tracking-[0.2em]"
                  htmlFor="email"
                  style={{ color: textSecondary, ...labelFont }}
                >
                  {copy.label}
                </label>
                <div className="relative group">
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    placeholder={copy.placeholder}
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    className="w-full border-none bg-transparent p-5 text-sm focus-visible:ring-0 focus-visible:ring-offset-0"
                    style={{ backgroundColor: surfaceContainerHigh, color: onSurface }}
                  />
                  <div
                    className="pointer-events-none absolute bottom-0 left-0 h-px w-full bg-[var(--base-color)] opacity-20 transition-all duration-200 group-focus-within:bg-[var(--focus-color)] group-focus-within:opacity-100"
                    style={focusLineStyle}
                  />
                </div>
                {error ? (
                  <p className="text-xs font-semibold" style={{ color: errorDim }}>
                    {error}
                  </p>
                ) : null}
              </div>

              <div className="flex items-start gap-3">
                <input
                  id="gdpr-consent"
                  name="gdprConsent"
                  type="checkbox"
                  checked={hasConsent}
                  onChange={(event) => setHasConsent(event.target.checked)}
                  className="mt-0.5 h-4 w-4 rounded border"
                  style={{ borderColor: outlineVariant }}
                />
                <label
                  htmlFor="gdpr-consent"
                  className="text-xs leading-relaxed"
                  style={{ color: textSecondary }}
                >
                  {copy.consentPrefix}
                  <Link href="/privacy" target="_blank" rel="noopener" className="underline">
                    {copy.privacyPolicyLink}
                  </Link>
                  {copy.consentConnector}
                  <Link href="/terms" target="_blank" rel="noopener" className="underline">
                    {copy.termsOfServiceLink}
                  </Link>
                  .
                </label>
              </div>

              <button
                type="submit"
                disabled={!canSubmit}
                aria-disabled={!canSubmit ? "true" : undefined}
                className="flex w-full items-center justify-center gap-3 rounded-lg px-6 py-4 text-base font-semibold transition-all hover:opacity-90 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60"
                style={{ backgroundColor: accent, color: onPrimary, ...headlineFont }}
              >
                {copy.cta}
                {isSubmitting ? (
                  <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                ) : (
                  <Send className="h-4 w-4" aria-hidden="true" />
                )}
              </button>

              <div
                className="flex items-center justify-center gap-2 text-[11px]"
                style={{ color: textSecondary, ...labelFont }}
              >
                <ShieldCheck className="h-4 w-4" aria-hidden="true" />
                <span>{copy.privacyNote}</span>
              </div>
            </form>
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
