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
    <div className="min-h-screen" style={{ backgroundColor: surfaceContainer, color: onSurface }}>
      <main className="mx-auto flex min-h-screen w-full max-w-[720px] items-center px-6 py-24">
        <section
          className="w-full space-y-5 rounded-xl border p-8"
          style={{ borderColor: outlineVariant, backgroundColor: surfaceContainerHigh }}
        >
          <h1 className="text-2xl font-semibold">{copy.successHeading}</h1>
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
            className="inline-flex items-center justify-center rounded-lg px-5 py-3 text-sm font-semibold"
            style={{ backgroundColor: accent, color: onPrimary }}
          >
            Vissza a kutatáshoz
          </Link>
        </section>
      </main>
    </div>
  );
}
