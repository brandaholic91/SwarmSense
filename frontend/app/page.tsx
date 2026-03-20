"use client";

import * as React from "react";

import { PersonaCard } from "@/components/persona-card";
import { RotatingPlaceholder } from "@/components/rotating-placeholder";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { messages } from "@/lib/messages";
import {
  accent,
  border,
  surface,
  stanceReject,
  textPrimary,
  textSecondary,
  trueBlack,
} from "@/lib/tokens";

const formatAriaLabel = (template: string, values: Record<string, string>) =>
  template.replace(/\{(\w+)\}/g, (_, key: string) => values[key] ?? "");

export default function Home() {
  const { landing } = messages;
  const personaCards = landing.preview.cards;
  const [researchTopic, setResearchTopic] = React.useState("");
  const [audienceDescription, setAudienceDescription] = React.useState("");
  const [showEmailCapture, setShowEmailCapture] = React.useState(false);
  const [errors, setErrors] = React.useState<{
    researchTopic?: string;
    audienceDescription?: string;
  }>({});

  const isComplete =
    researchTopic.trim().length > 0 && audienceDescription.trim().length > 0;

  React.useEffect(() => {
    if (!isComplete) setShowEmailCapture(false);
  }, [isComplete]);

  const handleBlur = (
    field: "researchTopic" | "audienceDescription",
    event: React.FocusEvent<HTMLTextAreaElement>
  ) => {
    const value = event.target.value;
    const message =
      field === "researchTopic"
        ? landing.form.errors.researchTopic
        : landing.form.errors.audienceDescription;

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
          : landing.form.errors.researchTopic,
        audienceDescription: audienceDescription.trim()
          ? undefined
          : landing.form.errors.audienceDescription,
      });
      return;
    }

    setErrors({});
    setShowEmailCapture(true);
  };

  return (
    <div
      className="flex min-h-screen w-full flex-col"
      style={{ backgroundColor: trueBlack, color: textPrimary }}
    >
      <main className="flex w-full flex-1 flex-col">
        <section className="mx-auto flex w-full max-w-2xl flex-col gap-6 px-4 pb-16 pt-20 sm:px-6">
          <h1
            className="text-[44px] font-extrabold leading-tight"
            style={{ letterSpacing: "-1px" }}
          >
            {landing.hero.headline}
          </h1>
          <p className="text-lg leading-8" style={{ color: textSecondary }}>
            {landing.hero.subheadline}
          </p>
          <p className="text-base leading-7" style={{ color: textSecondary }}>
            {landing.hero.supporting}
          </p>
        </section>

        <section className="mx-auto flex w-full max-w-2xl flex-col gap-6 px-4 pb-20 sm:px-6">
          <form
            className="mx-auto flex w-full max-w-lg flex-col gap-5 font-sans"
            onSubmit={handleSubmit}
          >
            <div className="flex flex-col gap-3 md:flex-row">
              <div className="flex flex-1 flex-col gap-2">
                <label className="text-sm font-semibold" htmlFor="research-topic">
                  {landing.form.researchLabel}
                </label>
                <RotatingPlaceholder
                  id="research-topic"
                  name="researchTopic"
                  value={researchTopic}
                  onChange={(event) => setResearchTopic(event.target.value)}
                  onBlur={(event) => handleBlur("researchTopic", event)}
                  maxLength={500}
                  className="min-h-[160px]"
                  examples={landing.form.researchExamples}
                  style={{
                    backgroundColor: trueBlack,
                    borderColor: border,
                    color: textPrimary,
                  }}
                />
                <p className="text-xs" style={{ color: textSecondary }}>
                  {landing.form.piiWarning}
                </p>
                {errors.researchTopic ? (
                  <p className="text-xs font-semibold" style={{ color: stanceReject }}>
                    {errors.researchTopic}
                  </p>
                ) : null}
              </div>

              <div className="flex flex-1 flex-col gap-2">
                <label className="text-sm font-semibold" htmlFor="audience-description">
                  {landing.form.audienceLabel}
                </label>
                <RotatingPlaceholder
                  id="audience-description"
                  name="audienceDescription"
                  value={audienceDescription}
                  onChange={(event) => setAudienceDescription(event.target.value)}
                  onBlur={(event) => handleBlur("audienceDescription", event)}
                  maxLength={500}
                  className="min-h-[160px]"
                  examples={landing.form.audienceExamples}
                  style={{
                    backgroundColor: trueBlack,
                    borderColor: border,
                    color: textPrimary,
                  }}
                />
                {errors.audienceDescription ? (
                  <p className="text-xs font-semibold" style={{ color: stanceReject }}>
                    {errors.audienceDescription}
                  </p>
                ) : null}
              </div>
            </div>

            <Button
              type="submit"
              className="min-h-[44px] px-6 text-base font-extrabold"
              style={{ backgroundColor: accent, color: trueBlack }}
              disabled={!isComplete}
              aria-disabled={!isComplete ? "true" : undefined}
            >
              {landing.form.cta}
            </Button>
          </form>

          {showEmailCapture ? (
            <div className="mx-auto flex w-full max-w-lg flex-col gap-2">
              <label className="text-sm font-semibold" htmlFor="email-capture">
                {landing.form.emailLabel}
              </label>
              <Input
                id="email-capture"
                name="email"
                type="email"
                placeholder={landing.form.emailPlaceholder}
                className="min-h-[44px]"
                style={{
                  backgroundColor: trueBlack,
                  borderColor: border,
                  color: textPrimary,
                }}
              />
              <p className="text-xs" style={{ color: textSecondary }}>
                {messages.emailCaptureNotice}
              </p>
            </div>
          ) : null}
        </section>

        <section className="mx-auto flex w-full max-w-2xl flex-col gap-6 px-4 pb-24 sm:px-6">
          <p
            className="text-xs font-semibold uppercase tracking-[0.28em]"
            style={{ color: accent }}
          >
            {landing.preview.eyebrow}
          </p>
          <div
            className="rounded-2xl border p-5"
            style={{ backgroundColor: surface, borderColor: border }}
          >
            <p className="text-sm font-semibold" style={{ color: accent }}>
              {landing.preview.title}
            </p>
            <p className="mt-3 text-4xl font-semibold tabular-nums">
              {landing.preview.stat}
            </p>
            <p className="mt-2 text-sm" style={{ color: textSecondary }}>
              {landing.preview.statSupporting}
            </p>
          </div>

          <blockquote
            className="border-l-4 pl-4 text-lg italic"
            style={{ borderLeftColor: accent, color: textSecondary }}
          >
            {landing.preview.objection}
          </blockquote>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {personaCards.map((card) => (
              <PersonaCard
                key={`${card.name}-${card.stance}`}
                name={card.name}
                role={card.role}
                stance={card.stance}
                stanceLabel={card.stanceLabel}
                summary={card.summary}
                variant="compact"
                ariaLabel={formatAriaLabel(landing.preview.cardAriaTemplate, {
                  name: card.name,
                  stanceLabel: card.stanceLabel,
                  role: card.role,
                })}
              />
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
