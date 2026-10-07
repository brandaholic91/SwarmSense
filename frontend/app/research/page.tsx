"use client";

import * as React from "react";
import type { CSSProperties } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Info } from "lucide-react";

import { startRunAction } from "@/app/actions/start-run";
import { RotatingPlaceholder } from "@/components/rotating-placeholder";
import { getErrorMessageByCode } from "@/lib/errors";
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


const headlineFont: CSSProperties = { fontFamily: "var(--font-headline)" };
const labelFont: CSSProperties = { fontFamily: "var(--font-label)" };
const focusLineStyle = {
  "--focus-color": accent,
  "--base-color": outlineVariant,
} as CSSProperties;

export default function ResearchPage() {
  const { form } = messages.research;
  const router = useRouter();
  const [researchTopic, setResearchTopic] = React.useState("");
  const [audienceDescription, setAudienceDescription] = React.useState("");
  const [errors, setErrors] = React.useState<{
    researchTopic?: string;
    audienceDescription?: string;
  }>({});

  const [startError, setStartError] = React.useState<string | null>(null);
  const [isStarting, startTransition] = React.useTransition();

  const isComplete =
    researchTopic.trim().length > 0 && audienceDescription.trim().length > 0;

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

    if (isStarting) {
      return;
    }

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
    setStartError(null);
    startTransition(async () => {
      const result = await startRunAction({
        topic: researchTopic.trim(),
        audience: audienceDescription.trim(),
      });
      if (result.ok) {
        router.push(`/waiting/${result.run_id}`);
      } else {
        setStartError(getErrorMessageByCode(result.code));
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
                    className="min-h-[140px] w-full resize-none border-none bg-transparent p-5 text-sm leading-relaxed focus-visible:ring-0 focus-visible:ring-offset-0"
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
                    className="min-h-[110px] w-full resize-none border-none bg-transparent p-5 text-sm leading-relaxed focus-visible:ring-0 focus-visible:ring-offset-0"
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
                {startError ? (
                  <p role="alert" className="text-sm font-semibold" style={{ color: errorDim }}>
                    {startError}
                  </p>
                ) : null}
                <button
                  type="submit"
                  className="flex w-full items-center justify-center gap-3 rounded-lg px-6 py-4 text-base font-semibold transition-all hover:opacity-90 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60"
                  style={{ backgroundColor: accent, color: onPrimary, ...headlineFont }}
                  disabled={!isComplete || isStarting}
                  aria-disabled={!isComplete || isStarting ? "true" : undefined}
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
