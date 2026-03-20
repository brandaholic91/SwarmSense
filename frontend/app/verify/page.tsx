import Link from "next/link";
import { redirect } from "next/navigation";

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

type VerifyPageProps = {
  searchParams?: Promise<{ token?: string }> | { token?: string };
};

export default async function VerifyPage({ searchParams }: VerifyPageProps) {
  const resolvedSearchParams = await Promise.resolve(searchParams ?? {});
  const token = resolvedSearchParams.token ?? "";
  const verifyResult = await verifyTokenAction({ token });

  if (verifyResult.ok) {
    redirect(`/qualifier?user_id=${encodeURIComponent(verifyResult.user_id)}`);
  }

  const verifyMessages = messages.verify;
  const errorMessage = getErrorMessageByCode(verifyResult.code);

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
