"use client";

import * as React from "react";
import type { CSSProperties } from "react";
import Link from "next/link";
import { ArrowRight, Info, Send, ShieldCheck } from "lucide-react";

import { isRedirectError } from "next/dist/client/components/redirect-error";

import { submitRunAction } from "@/app/actions/submit-run";
import { RotatingPlaceholder } from "@/components/rotating-placeholder";
import { Input } from "@/components/ui/input";
import { messages } from "@/lib/messages";
import {
  accent,
  errorDim,
  onPrimary,
  onSurface,
  outlineVariant,
  surfaceContainer,
  surfaceContainerHigh,
  surfaceContainerLow,
  textSecondary,
} from "@/lib/tokens";

const headlineFont: CSSProperties = { fontFamily: "var(--font-headline)" };
const labelFont: CSSProperties = { fontFamily: "var(--font-label)" };
const focusLineStyle = {
  "--focus-color": accent,
  "--base-color": outlineVariant,
} as CSSProperties;

export default function ResearchPage() {
  const { form } = messages.research;
  const [researchTopic, setResearchTopic] = React.useState("");
  const [audienceDescription, setAudienceDescription] = React.useState("");
  const [isSubmitted, setIsSubmitted] = React.useState(false);
  const [email, setEmail] = React.useState("");
  const [hasConsent, setHasConsent] = React.useState(false);
  const [isCheckingEmail, startEmailCheckTransition] = React.useTransition();
  const [errors, setErrors] = React.useState<{
    researchTopic?: string;
    audienceDescription?: string;
    email?: string;
  }>({});

  const isComplete =
    researchTopic.trim().length > 0 && audienceDescription.trim().length > 0;
  const canSubmitEmail =
    email.trim().length > 0 && hasConsent && !isCheckingEmail;

  React.useEffect(() => {
    if (!isComplete) {
      setIsSubmitted(false);
      setErrors({});
    }
  }, [isComplete]);

  const handleBlur = (
    field: "researchTopic" | "audienceDescription",
    event: React.FocusEvent<HTMLTextAreaElement>
  ) => {
    const value = event.target.value;
    const message =
      field === "researchTopic"
        ? form.errors.researchTopic
        : form.errors.audienceDescription;

    setErrors((prev) => ({
      ...prev,
      [field]: value.trim() ? undefined : message,
    }));
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!isComplete) {
      setErrors({
        researchTopic: researchTopic.trim()
          ? undefined
          : form.errors.researchTopic,
        audienceDescription: audienceDescription.trim()
          ? undefined
          : form.errors.audienceDescription,
      });
      return;
    }

    setErrors({});
    setIsSubmitted(true);
  };

  return (
    <div className="relative min-h-screen" style={{ color: onSurface }}>
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

      <main className="flex min-h-[calc(100vh-80px)] items-center justify-center px-6 py-24">
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
                {form.headline}
              </h1>
              <p className="text-sm leading-relaxed" style={{ color: textSecondary }}>
                {form.subheadline}
              </p>
            </div>

            <form className="space-y-10" onSubmit={handleSubmit}>
              <div className="space-y-3">
                <label
                  className="text-xs uppercase tracking-[0.2em]"
                  htmlFor="research-topic"
                  style={{ color: textSecondary, ...labelFont }}
                >
                  {form.researchLabel}
                </label>
                <div className="relative group">
                  <RotatingPlaceholder
                    id="research-topic"
                    name="researchTopic"
                    value={researchTopic}
                    onChange={(event) => setResearchTopic(event.target.value)}
                    onBlur={(event) => handleBlur("researchTopic", event)}
                    maxLength={500}
                    examples={form.researchExamples}
                    readOnly={isSubmitted}
                    aria-readonly={isSubmitted ? "true" : undefined}
                    className={`min-h-[140px] w-full resize-none border-none bg-transparent p-5 text-sm leading-relaxed focus-visible:ring-0 focus-visible:ring-offset-0 ${
                      isSubmitted ? "opacity-80" : ""
                    }`}
                    style={{ backgroundColor: surfaceContainerLow, color: onSurface }}
                  />
                  <div
                    className="pointer-events-none absolute bottom-0 left-0 h-px w-full bg-[var(--base-color)] opacity-20 transition-all duration-200 group-focus-within:bg-[var(--focus-color)] group-focus-within:opacity-100"
                    style={focusLineStyle}
                  />
                </div>
                <div className="flex items-center gap-2 text-[11px]" style={{ color: textSecondary }}>
                  <Info className="h-3.5 w-3.5" aria-hidden="true" />
                  <span style={labelFont}>{form.piiWarning}</span>
                </div>
                {errors.researchTopic ? (
                  <p className="text-xs font-semibold" style={{ color: errorDim }}>
                    {errors.researchTopic}
                  </p>
                ) : null}
              </div>

              <div className="space-y-3">
                <label
                  className="text-xs uppercase tracking-[0.2em]"
                  htmlFor="audience-description"
                  style={{ color: textSecondary, ...labelFont }}
                >
                  {form.audienceLabel}
                </label>
                <div className="relative group">
                  <RotatingPlaceholder
                    id="audience-description"
                    name="audienceDescription"
                    value={audienceDescription}
                    onChange={(event) => setAudienceDescription(event.target.value)}
                    onBlur={(event) => handleBlur("audienceDescription", event)}
                    maxLength={500}
                    examples={form.audienceExamples}
                    readOnly={isSubmitted}
                    aria-readonly={isSubmitted ? "true" : undefined}
                    className={`min-h-[110px] w-full resize-none border-none bg-transparent p-5 text-sm leading-relaxed focus-visible:ring-0 focus-visible:ring-offset-0 ${
                      isSubmitted ? "opacity-80" : ""
                    }`}
                    style={{ backgroundColor: surfaceContainerLow, color: onSurface }}
                  />
                  <div
                    className="pointer-events-none absolute bottom-0 left-0 h-px w-full bg-[var(--base-color)] opacity-20 transition-all duration-200 group-focus-within:bg-[var(--focus-color)] group-focus-within:opacity-100"
                    style={focusLineStyle}
                  />
                </div>
                {errors.audienceDescription ? (
                  <p className="text-xs font-semibold" style={{ color: errorDim }}>
                    {errors.audienceDescription}
                  </p>
                ) : null}
              </div>

              <div className="space-y-3">
                <button
                  type="submit"
                  className="flex w-full items-center justify-center gap-3 rounded-lg px-6 py-4 text-base font-semibold transition-transform active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60"
                  style={{ backgroundColor: accent, color: onPrimary, ...headlineFont }}
                  disabled={!isComplete}
                  aria-disabled={!isComplete ? "true" : undefined}
                >
                  {form.submitCta}
                  <ArrowRight className="h-4 w-4" aria-hidden="true" />
                </button>
                <p
                  className="text-center text-xs"
                  style={{ color: textSecondary, ...labelFont }}
                >
                  {form.helper}
                </p>
              </div>
            </form>
          </section>

          {isSubmitted ? (
            <section
              className="space-y-8 rounded-lg border p-6 animate-in fade-in slide-in-from-top-2"
              style={{ backgroundColor: surfaceContainerHigh, borderColor: outlineVariant }}
            >
              <div className="space-y-2">
                <h2
                  className="text-2xl font-semibold"
                  style={{ ...headlineFont, color: onSurface }}
                >
                  {form.email.heading}
                </h2>
                <p className="text-sm" style={{ color: textSecondary }}>
                  {form.email.subheadline}
                </p>
              </div>
              <form
                className="space-y-6"
                onSubmit={(event) => {
                  event.preventDefault();
                  const trimmed = email.trim();
                  if (!trimmed || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
                    setErrors((prev) => ({ ...prev, email: form.errors.email }));
                    return;
                  }

                  if (!hasConsent) {
                    return;
                  }

                  setErrors((prev) => ({ ...prev, email: undefined }));

                  startEmailCheckTransition(async () => {
                    try {
                      await submitRunAction({
                        email: trimmed,
                        hasConsent: true,
                        consentTimestamp: new Date().toISOString(),
                        topic: researchTopic,
                        audience: audienceDescription,
                      });
                    } catch (error) {
                      if (isRedirectError(error)) {
                        throw error;
                      }
                      setErrors((prev) => ({ ...prev, email: messages.genericError }));
                    }
                  });
                }}
              >
                <div className="space-y-3">
                  <label
                    className="text-xs uppercase tracking-[0.2em]"
                    htmlFor="email"
                    style={{ color: textSecondary, ...labelFont }}
                  >
                    {form.email.label}
                  </label>
                  <div className="relative group">
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      placeholder={form.email.placeholder}
                      value={email}
                      onChange={(event) => setEmail(event.target.value)}
                      className="w-full border-none bg-transparent p-5 text-sm focus-visible:ring-0 focus-visible:ring-offset-0"
                      style={{ backgroundColor: surfaceContainerLow, color: onSurface }}
                    />
                    <div
                      className="pointer-events-none absolute bottom-0 left-0 h-px w-full bg-[var(--base-color)] opacity-20 transition-all duration-200 group-focus-within:bg-[var(--focus-color)] group-focus-within:opacity-100"
                      style={focusLineStyle}
                    />
                  </div>
                  {errors.email ? (
                    <p className="text-xs font-semibold" style={{ color: errorDim }}>
                      {errors.email}
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
                  <label htmlFor="gdpr-consent" className="text-xs leading-relaxed" style={{ color: textSecondary }}>
                    {form.email.consentPrefix}
                    <Link href="/privacy" target="_blank" rel="noopener" className="underline">
                      {form.email.privacyPolicyLink}
                    </Link>
                    {form.email.consentConnector}
                    <Link href="/terms" target="_blank" rel="noopener" className="underline">
                      {form.email.termsOfServiceLink}
                    </Link>
                    .
                  </label>
                </div>
                <div className="space-y-4">
                  <button
                    type="submit"
                    className="flex w-full items-center justify-center gap-3 rounded-lg px-6 py-4 text-base font-semibold transition-transform active:scale-[0.98]"
                    style={{ backgroundColor: accent, color: onPrimary, ...headlineFont }}
                    disabled={!canSubmitEmail}
                    aria-disabled={!canSubmitEmail ? "true" : undefined}
                  >
                    {form.email.cta}
                    <Send className="h-4 w-4" aria-hidden="true" />
                  </button>
                  <div
                    className="flex items-center justify-center gap-2 text-[11px]"
                    style={{ color: textSecondary, ...labelFont }}
                  >
                    <ShieldCheck className="h-4 w-4" aria-hidden="true" />
                    <span>{form.email.privacyNote}</span>
                  </div>
                </div>
              </form>
            </section>
          ) : null}
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
