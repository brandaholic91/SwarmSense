"use client";

import * as React from "react";
import type { CSSProperties } from "react";
import Link from "next/link";

import { requestEmailAction } from "@/app/actions/request-email";
import { getErrorMessageByCode } from "@/lib/errors";
import { messages } from "@/lib/messages";
import {
  accent,
  errorDim,
  onSurface,
  outlineVariant,
  surfaceContainerLow,
  textSecondary,
} from "@/lib/tokens";

type EmailRequestFormProps = {
  runId: string;
  emailsRemaining: number;
};

const t = messages.result.email;
const headlineFont: CSSProperties = { fontFamily: "var(--font-headline)" };
const labelFont: CSSProperties = { fontFamily: "var(--font-label)" };

export function EmailRequestForm({ runId, emailsRemaining }: EmailRequestFormProps) {
  const [email, setEmail] = React.useState("");
  const [remaining, setRemaining] = React.useState(emailsRemaining);
  const [sent, setSent] = React.useState(false);
  const [errorCode, setErrorCode] = React.useState<string | null>(null);
  const [isSending, startTransition] = React.useTransition();

  const exhausted = remaining <= 0;

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (isSending || exhausted) return;

    setSent(false);
    setErrorCode(null);
    startTransition(async () => {
      const result = await requestEmailAction({ runId, email });
      if (result.ok) {
        setSent(true);
        setEmail("");
        setRemaining(result.emailsRemaining);
      } else {
        setErrorCode(result.code);
      }
    });
  };

  return (
    <section className="space-y-3">
      <h2 className="text-xl font-semibold" style={headlineFont}>
        {t.heading}
      </h2>
      <form className="space-y-3" onSubmit={handleSubmit} noValidate>
        <label
          htmlFor="email-request"
          className="block text-xs uppercase tracking-[0.2em]"
          style={{ color: textSecondary, ...labelFont }}
        >
          {t.label}
        </label>
        <div className="flex flex-col gap-3 sm:flex-row">
          <input
            id="email-request"
            type="email"
            name="email"
            autoComplete="email"
            maxLength={254}
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            disabled={exhausted}
            className="w-full rounded-md p-3 text-sm"
            style={{
              backgroundColor: surfaceContainerLow,
              color: onSurface,
              border: `1px solid ${outlineVariant}`,
            }}
          />
          <button
            type="submit"
            disabled={isSending || exhausted}
            className="rounded-md px-5 py-3 text-sm font-semibold disabled:opacity-50"
            style={{ backgroundColor: accent, color: "#5c3800" }}
          >
            {isSending ? t.sending : t.submit}
          </button>
        </div>
      </form>

      {exhausted ? (
        <p className="text-sm" style={{ color: textSecondary }}>
          {getErrorMessageByCode("EMAIL_RUN_LIMIT_REACHED")}
        </p>
      ) : null}
      {sent ? (
        <p role="status" className="text-sm" style={{ color: onSurface }}>
          {t.sent}
        </p>
      ) : null}
      {errorCode ? (
        <p role="alert" className="text-sm font-semibold" style={{ color: errorDim }}>
          {getErrorMessageByCode(errorCode)}
        </p>
      ) : null}

      <p className="text-xs leading-relaxed" style={{ color: textSecondary }}>
        {t.retentionNote}{" "}
        <Link href="/privacy" className="underline underline-offset-4" style={{ color: accent }}>
          {t.privacyLink}
        </Link>
      </p>
    </section>
  );
}
