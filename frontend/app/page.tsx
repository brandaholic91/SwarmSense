import type { CSSProperties } from "react";
import Link from "next/link";
import { ArrowDown, ArrowRight, FilePlus, Mail, Zap } from "lucide-react";

import { PersonaCard } from "@/components/persona-card";
import { ScrollReveal } from "@/components/scroll-reveal";
import { messages } from "@/lib/messages";
import {
  accent,
  errorDim,
  onPrimary,
  onSurface,
  outlineVariant,
  surfaceContainer,
  surfaceContainerHigh,
  surfaceContainerHighest,
  surfaceContainerLow,
  tertiaryContainer,
  textSecondary,
} from "@/lib/tokens";

const formatAriaLabel = (template: string, values: Record<string, string>) =>
  template.replace(/\{(\w+)\}/g, (_, key: string) => values[key] ?? `{${key}}`);

const headlineFont: CSSProperties = { fontFamily: "var(--font-headline)" };
const labelFont: CSSProperties = { fontFamily: "var(--font-label)" };
const navBackground = `${surfaceContainer}cc`; // 8-digit hex = 80% opacity, widely supported

export default function Home() {
  const { landing } = messages;
  const previewCards = landing.preview.cards;

  return (
    <div className="min-h-dvh w-full" style={{ color: onSurface }}>
      <ScrollReveal />
      <nav
        className="sticky top-0 z-50 w-full border-b backdrop-blur-xl"
        style={{ backgroundColor: navBackground, borderColor: outlineVariant }}
      >
        <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-4">
          <span
            className="text-lg font-semibold tracking-tight"
            style={{ ...headlineFont, color: onSurface }}
          >
            Swarm<span style={{ color: accent }}>Sense</span>
          </span>
          <Link
            href="/research"
            className="inline-flex items-center justify-center rounded-md px-5 py-2 text-sm font-semibold transition-all hover:scale-[1.04] hover:opacity-90 active:scale-[0.97]"
            style={{ backgroundColor: accent, color: onPrimary, ...labelFont }}
          >
            {landing.nav.cta}
          </Link>
        </div>
      </nav>

      <main className="flex w-full flex-col">
        <header className="relative flex min-h-[60vh] flex-col items-center justify-center overflow-hidden px-6 pb-14 pt-20">
          <div className="relative z-10 mx-auto flex w-full max-w-5xl flex-col items-center text-center">
            <h1
              className="hero-h1 text-4xl font-bold leading-[1.1] md:text-6xl"
              style={{ ...headlineFont, color: onSurface }}
            >
              {landing.hero.headline}{" "}
              <span style={{ color: accent }}>{landing.hero.highlight}</span>{" "}
              {landing.hero.headlineSuffix}
            </h1>
            <p
              className="hero-sub mt-6 max-w-2xl text-base leading-relaxed md:text-lg"
              style={{ color: textSecondary }}
            >
              {landing.hero.subheadline}
            </p>
            <div className="hero-cta mt-10 flex w-full flex-col items-center justify-center gap-4 sm:flex-row">
              <Link
                href="/research"
                className="inline-flex w-full items-center justify-center gap-2 rounded-lg px-8 py-4 text-base font-semibold transition-all hover:scale-[1.03] hover:opacity-90 active:scale-[0.98] sm:w-auto"
                style={{ backgroundColor: accent, color: onPrimary, ...headlineFont }}
              >
                {landing.hero.cta}
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Link>
            </div>
          </div>

          <div
            aria-hidden="true"
            className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
          >
            <div
              className="hero-blob h-[200px] w-[200px] rounded-full blur-[70px] md:h-[300px] md:w-[300px] md:blur-[80px] lg:h-[400px] lg:w-[400px] lg:blur-[90px]"
              style={{ backgroundColor: accent }}
            />
          </div>
        </header>

        <section className="px-6 py-20">
          <div className="after-hero mx-auto flex w-full max-w-4xl flex-col items-center text-center">
            <h2
              className="text-2xl font-semibold md:text-3xl"
              style={{ ...headlineFont, color: onSurface }}
            >
              {landing.painBridge.heading}
            </h2>
            <div className="mt-12 grid w-full grid-cols-1 gap-6 md:grid-cols-3">
              {landing.painBridge.items.map((item) => (
                <div
                  key={item.before}
                  className="flex flex-col items-center gap-3 rounded-2xl border p-6 transition-transform duration-300 hover:-translate-y-1"
                  style={{
                    backgroundColor: surfaceContainerHigh,
                    borderColor: outlineVariant,
                  }}
                >
                  <span
                    className="text-sm line-through opacity-50"
                    style={{ color: onSurface }}
                  >
                    {item.before}
                  </span>
                  <ArrowDown
                    className="h-4 w-4"
                    style={{ color: accent }}
                    aria-hidden="true"
                  />
                  <span
                    className="text-base font-semibold"
                    style={{ color: accent }}
                  >
                    {item.after}
                  </span>
                </div>
              ))}
            </div>
            <p
              className="mt-10 max-w-xl text-sm leading-relaxed"
              style={{ color: textSecondary }}
            >
              {landing.painBridge.closing}
            </p>
          </div>
        </section>

        <section className="px-6 py-20" style={{ backgroundColor: surfaceContainerLow }}>
          <div className="mx-auto w-full max-w-6xl">
            <div className="sr mb-12 text-center md:text-left">
              <span
                className="block text-xs uppercase tracking-[0.2em]"
                style={{ color: accent, ...labelFont }}
              >
                {landing.preview.eyebrow}
              </span>
              <h2
                className="mt-4 text-2xl font-semibold md:text-3xl"
                style={{ ...headlineFont, color: onSurface }}
              >
                {landing.preview.heading}
              </h2>
            </div>

            <div
              className="sr-d1 rounded-2xl border p-6 shadow-2xl"
              style={{ backgroundColor: surfaceContainerHigh, borderColor: outlineVariant }}
            >
              <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
                <div className="space-y-5">
                  <div>
                    <p
                      className="text-[11px] uppercase tracking-[0.2em]"
                      style={{ color: textSecondary, ...labelFont }}
                    >
                      {landing.preview.researchLabel}
                    </p>
                    <p className="mt-2 text-lg font-medium" style={{ color: onSurface }}>
                      {landing.preview.researchValue}
                    </p>
                  </div>
                  <div>
                    <p
                      className="text-[11px] uppercase tracking-[0.2em]"
                      style={{ color: textSecondary, ...labelFont }}
                    >
                      {landing.preview.audienceLabel}
                    </p>
                    <p className="mt-2 text-sm" style={{ color: textSecondary }}>
                      {landing.preview.audienceValue}
                    </p>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-5">
                  <div
                    className="flex items-center gap-2 rounded-lg border px-4 py-2"
                    style={{ borderColor: tertiaryContainer, backgroundColor: surfaceContainer }}
                  >
                    <span className="text-sm" style={{ color: tertiaryContainer }}>
                      {landing.preview.consensusLabel}
                    </span>
                  </div>
                  <div className="w-full max-w-xs space-y-2">
                    <div
                      className="flex justify-between text-[11px] uppercase tracking-[0.2em]"
                      style={{ color: textSecondary, ...labelFont }}
                    >
                      <span>{landing.preview.supportLabel}</span>
                      <span>{landing.preview.rejectLabel}</span>
                    </div>
                    <div
                      className="flex h-2 w-full overflow-hidden rounded-full"
                      style={{ backgroundColor: surfaceContainerHighest }}
                    >
                      <div
                        className="h-full"
                        style={{
                          backgroundColor: accent,
                          width: `${landing.preview.supportPercent}%`,
                        }}
                      />
                      <div
                        className="h-full"
                        style={{
                          backgroundColor: errorDim,
                          width: `${landing.preview.rejectPercent}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-10 grid grid-cols-1 gap-6 md:grid-cols-3">
              {previewCards.map((card, i) => (
                <div key={`${card.name}-${card.stance}`} className={["sr", "sr-d1", "sr-d2"][i] ?? "sr"}>
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
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="px-6 py-24">
          <div className="mx-auto w-full max-w-6xl">
            <h2
              className="sr text-center text-3xl font-semibold md:text-4xl"
              style={{ ...headlineFont, color: onSurface }}
            >
              {landing.howItWorks.heading}
            </h2>
            <div className="mt-16 grid grid-cols-1 gap-12 md:grid-cols-3">
              {landing.howItWorks.steps.map((step, index) => {
                const icon =
                  index === 0 ? (
                    <FilePlus className="h-8 w-8" aria-hidden="true" />
                  ) : index === 1 ? (
                    <Zap className="h-8 w-8" aria-hidden="true" />
                  ) : (
                    <Mail className="h-8 w-8" aria-hidden="true" />
                  );

                return (
                  <div key={step.title} className={`${["sr", "sr-d1", "sr-d2"][index] ?? "sr"} flex flex-col items-center text-center`}>
                    <div
                      className="flex h-16 w-16 items-center justify-center rounded-2xl border transition-transform duration-300 hover:scale-110"
                      style={{
                        backgroundColor: surfaceContainerHigh,
                        borderColor: outlineVariant,
                        color: accent,
                      }}
                    >
                      {icon}
                    </div>
                    <h3
                      className="mt-6 text-lg font-semibold"
                      style={{ ...headlineFont, color: onSurface }}
                    >
                      {step.title}
                    </h3>
                    <p className="mt-3 text-sm" style={{ color: textSecondary }}>
                      {step.description}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        <section
          className="border-y px-6 py-10"
          style={{ backgroundColor: surfaceContainer, borderColor: outlineVariant }}
        >
          <div className="mx-auto flex w-full max-w-6xl flex-wrap items-center justify-center gap-8 md:justify-between">
            {landing.stats.items.map((item, i) => (
              <div key={item.label} className={`${["sr", "sr-d1", "sr-d2", "sr-d3"][i] ?? "sr"} flex flex-col items-center md:items-start`}>
                <span
                  className="text-lg font-semibold"
                  style={{ ...labelFont, color: onSurface }}
                >
                  {item.value}
                </span>
                <span
                  className="text-[11px] uppercase tracking-[0.2em]"
                  style={{ color: textSecondary, ...labelFont }}
                >
                  {item.label}
                </span>
              </div>
            ))}
          </div>
        </section>

        <section className="px-6 py-24 text-center">
          <div
            className="sr relative mx-auto max-w-3xl overflow-hidden rounded-3xl border p-12"
            style={{ backgroundColor: surfaceContainerHigh, borderColor: outlineVariant }}
          >
            <div className="relative z-10">
              <h2
                className="text-3xl font-semibold md:text-4xl"
                style={{ ...headlineFont, color: onSurface }}
              >
                {landing.closingCta.heading}
              </h2>
              <Link
                href="/research"
                className="mt-8 inline-flex w-full items-center justify-center rounded-xl px-10 py-4 text-lg font-semibold transition-all hover:scale-[1.03] hover:opacity-90 active:scale-[0.98] sm:w-auto"
                style={{ backgroundColor: accent, color: onPrimary, ...headlineFont }}
              >
                {landing.closingCta.cta}
              </Link>
              <p className="mt-4 text-sm" style={{ color: textSecondary }}>
                {landing.closingCta.helper}
              </p>
            </div>
            <div
              aria-hidden="true"
              className="cta-blob absolute -bottom-1/2 left-1/2 h-full w-full rounded-full blur-[90px]"
              style={{ backgroundColor: accent }}
            />
          </div>
        </section>
      </main>

      <footer className="border-t px-6 py-12" style={{ borderColor: outlineVariant }}>
        <div className="mx-auto flex w-full max-w-6xl flex-col items-center justify-center gap-6">
          <div className="flex gap-6">
            <Link
              href="/privacy"
              className="text-[11px] uppercase tracking-[0.3em]"
              style={{ color: textSecondary, ...labelFont }}
            >
              {landing.footer.privacy}
            </Link>
            <Link
              href="/terms"
              className="text-[11px] uppercase tracking-[0.3em]"
              style={{ color: textSecondary, ...labelFont }}
            >
              {landing.footer.terms}
            </Link>
          </div>
          <span
            className="text-base font-semibold tracking-tight"
            style={{ ...headlineFont, color: onSurface }}
          >
            Swarm<span style={{ color: accent }}>Sense</span>
          </span>
        </div>
      </footer>
    </div>
  );
}
