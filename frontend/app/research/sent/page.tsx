import type { CSSProperties } from "react";
import { Mail } from "lucide-react";

import { messages } from "@/lib/messages";
import {
  accent,
  onSurface,
  outlineVariant,
  surfaceContainer,
  surfaceContainerLow,
  textSecondary,
} from "@/lib/tokens";

type ResearchSentPageProps = {
  searchParams?: Promise<{ email?: string }> | { email?: string };
};

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const headlineFont: CSSProperties = { fontFamily: "var(--font-headline)" };
const labelFont: CSSProperties = { fontFamily: "var(--font-label)" };

function normalizeEmail(rawValue: string | undefined): string | null {
  if (!rawValue) {
    return null;
  }

  const normalized = rawValue.trim().toLowerCase();
  if (!EMAIL_PATTERN.test(normalized)) {
    return null;
  }

  return normalized;
}

export default async function ResearchSentPage({ searchParams }: ResearchSentPageProps) {
  const copy = messages.research.form.email;
  const resolvedSearchParams = await Promise.resolve(searchParams ?? {});
  const rawEmail = Array.isArray(resolvedSearchParams.email)
    ? resolvedSearchParams.email[0]
    : resolvedSearchParams.email;
  const normalizedEmail = normalizeEmail(rawEmail);

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
                {copy.successEyebrow}
              </span>
              <h1
                className="text-3xl font-semibold md:text-4xl"
                style={{ ...headlineFont, color: onSurface }}
              >
                {copy.successHeading}
              </h1>
              <p className="text-sm leading-relaxed" style={{ color: textSecondary }}>
                {copy.successBodyPrefix}
              </p>
            </div>

            <div
              className="relative overflow-hidden rounded-lg px-5 py-8 text-center md:py-10"
              style={{ backgroundColor: surfaceContainerLow }}
            >
              <div className="flex flex-col items-center justify-center gap-4">
                <Mail
                  className="h-12 w-12 md:h-14 md:w-14"
                  style={{ color: accent }}
                  strokeWidth={1.25}
                  aria-hidden="true"
                />
                {normalizedEmail ? (
                  <p
                    className="break-all text-lg font-semibold md:text-xl"
                    style={{ ...headlineFont, color: onSurface }}
                  >
                    {normalizedEmail}
                  </p>
                ) : null}
                <p className="max-w-md text-sm leading-relaxed" style={{ color: textSecondary }}>
                  {copy.successHint}
                </p>
              </div>
            </div>
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
