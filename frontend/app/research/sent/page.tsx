import type { CSSProperties } from "react";
import Link from "next/link";

import { messages } from "@/lib/messages";
import {
  accent,
  onPrimary,
  onSurface,
  outlineVariant,
  surfaceContainer,
  surfaceContainerHigh,
  textSecondary,
} from "@/lib/tokens";

type ResearchSentPageProps = {
  searchParams?: Promise<{ email?: string }> | { email?: string };
};

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const headlineFont: CSSProperties = { fontFamily: "var(--font-headline)" };

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
        <div className="w-full max-w-[600px]">
          <section
            className="w-full space-y-5 rounded-xl border p-8"
            style={{ borderColor: outlineVariant, backgroundColor: surfaceContainerHigh }}
          >
            <h1 className="text-2xl font-semibold" style={headlineFont}>{copy.successHeading}</h1>
            <p className="text-sm leading-relaxed" style={{ color: textSecondary }}>
              {copy.successBodyPrefix}
            </p>
            {normalizedEmail ? (
              <p className="text-base font-semibold">{normalizedEmail}</p>
            ) : null}
            <p className="text-sm" style={{ color: textSecondary }}>
              {copy.successHint}
            </p>
            <Link
              href="/research"
              className="inline-flex items-center justify-center rounded-lg px-5 py-3 text-sm font-semibold transition-opacity hover:opacity-90"
              style={{ backgroundColor: accent, color: onPrimary, ...headlineFont }}
            >
              Vissza a kutatáshoz
            </Link>
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
