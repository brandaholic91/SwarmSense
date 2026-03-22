import type { CSSProperties } from "react";
import { CheckCircle, XCircle, AlertCircle } from "lucide-react";

import { joinWaitlistAction } from "@/app/actions/join-waitlist";
import {
  accent,
  onSurface,
  outlineVariant,
  surfaceContainer,
  surfaceContainerHigh,
  textSecondary,
} from "@/lib/tokens";

type ProPageProps = {
  searchParams?: Promise<{ email?: string }> | { email?: string };
};

const headlineFont: CSSProperties = { fontFamily: "var(--font-headline)" };

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default async function ProPage({ searchParams }: ProPageProps) {
  const resolved = await Promise.resolve(searchParams ?? {});
  const rawEmail = Array.isArray(resolved.email) ? resolved.email[0] : resolved.email;
  const email = rawEmail?.trim().toLowerCase() ?? "";

  let status: "joined" | "already_joined" | "invalid" | "error" = "invalid";

  if (email && EMAIL_PATTERN.test(email)) {
    const result = await joinWaitlistAction({ email });
    status = result.ok ? result.status : "error";
  }

  const content = {
    joined: {
      icon: <CheckCircle className="h-8 w-8" style={{ color: accent }} aria-hidden="true" />,
      heading: "Rajta vagy a Pro várólistán",
      body: "Értesítünk, amint a Pro verzió elérhető lesz.",
    },
    already_joined: {
      icon: <CheckCircle className="h-8 w-8" style={{ color: accent }} aria-hidden="true" />,
      heading: "Már rajta vagy a várólistán",
      body: "Ezt az e-mail címet már felírtuk. Szólunk, amint a Pro elérhető.",
    },
    error: {
      icon: <XCircle className="h-8 w-8" style={{ color: textSecondary }} aria-hidden="true" />,
      heading: "Hiba történt",
      body: "Nem sikerült feliratkozni. Kérjük, próbáld újra később.",
    },
    invalid: {
      icon: <AlertCircle className="h-8 w-8" style={{ color: textSecondary }} aria-hidden="true" />,
      heading: "Érvénytelen link",
      body: "A feliratkozási link nem tartalmaz érvényes e-mail címet. Menj vissza az e-mailhez és próbáld újra.",
    },
  }[status];

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
            className="w-full space-y-6 rounded-xl border p-8"
            style={{ borderColor: outlineVariant, backgroundColor: surfaceContainerHigh }}
          >
            {content.icon}
            <div className="space-y-2">
              <h1
                className="text-2xl font-semibold"
                style={{ ...headlineFont, color: onSurface }}
              >
                {content.heading}
              </h1>
              <p className="text-sm leading-relaxed" style={{ color: textSecondary }}>
                {content.body}
              </p>
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
