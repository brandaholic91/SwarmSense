"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { verifyTokenAction } from "@/app/actions/verify-token";
import { getErrorMessageByCode } from "@/lib/errors";
import { messages } from "@/lib/messages";
import {
  accent,
  onPrimary,
  onSurface,
  outlineVariant,
  surfaceContainer,
  textSecondary,
} from "@/lib/tokens";

type State = { status: "verifying" } | { status: "error"; code: string };

export function VerifyClient({ token }: { token: string }) {
  const router = useRouter();
  const [state, setState] = useState<State>(() =>
    token ? { status: "verifying" } : { status: "error", code: "NO_TOKEN" }
  );

  useEffect(() => {
    // P-1: Verification fires client-side to prevent link-preview bots from
    // burning single-use tokens during server-side render.
    if (!token) return;

    (async () => {
      try {
        const result = await verifyTokenAction({ token });
        if (result.ok) {
          router.push("/qualifier");
        } else {
          setState({ status: "error", code: result.code });
        }
      } catch {
        setState({ status: "error", code: "TOKEN_INVALID" });
      }
    })();
  }, [token, router]);

  const verifyMessages = messages.verify;

  if (state.status === "verifying") {
    return (
      <main
        className="flex min-h-screen items-center justify-center px-6"
        style={{ backgroundColor: surfaceContainer, color: onSurface }}
      >
        <p className="text-sm" style={{ color: textSecondary }}>
          {verifyMessages.verifying}
        </p>
      </main>
    );
  }

  const errorMessage = getErrorMessageByCode(state.code);

  return (
    <main
      className="flex min-h-screen items-center justify-center px-6"
      style={{ backgroundColor: surfaceContainer, color: onSurface }}
    >
      <section
        className="w-full max-w-xl rounded-xl border p-8 text-center"
        style={{ borderColor: outlineVariant }}
      >
        <h1 className="text-2xl font-semibold">{verifyMessages.title}</h1>
        <p className="mt-4 text-sm" style={{ color: textSecondary }}>
          {verifyMessages.descriptionPrefix}
        </p>
        <p className="mt-2 text-base">{errorMessage}</p>
        <Link
          href="/research"
          className="mt-8 inline-flex rounded-lg px-6 py-3 text-sm font-semibold"
          style={{ backgroundColor: accent, color: onPrimary }}
        >
          {verifyMessages.requestNewLinkCta}
        </Link>
      </section>
    </main>
  );
}
