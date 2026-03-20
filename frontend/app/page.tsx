import { PersonaCard } from "@/components/persona-card";
import { messages } from "@/lib/messages";
import {
  accent,
  border,
  surface,
  textPrimary,
  textSecondary,
  trueBlack,
} from "@/lib/tokens";

const formatAriaLabel = (template: string, values: Record<string, string>) =>
  template.replace(/\{(\w+)\}/g, (_, key: string) => values[key] ?? "");

export default function Home() {
  const { landing } = messages;
  const personaCards = landing.preview.cards;

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
