import Link from "next/link";

import { messages } from "@/lib/messages";
import { accent, onSurface, textSecondary } from "@/lib/tokens";

export default function PrivacyPage() {
  const legal = messages.legal;

  return (
    <main className="mx-auto max-w-3xl px-6 py-16" style={{ color: onSurface }}>
      <h1 className="text-3xl font-semibold">{legal.privacyTitle}</h1>
      <p className="mt-2 text-xs tracking-wide" style={{ color: textSecondary }}>
        {legal.privacyEffectiveDate}
      </p>
      <div className="mt-6 space-y-4 text-sm leading-relaxed">
        {legal.privacyIntroParagraphs.map((paragraph, i) => (
          <p key={i}>{paragraph}</p>
        ))}
      </div>

      <section className="mt-10 space-y-2 text-sm leading-relaxed">
        <h2 className="text-xl font-semibold">{legal.controllerTitle}</h2>
        <p>{legal.controllerBody}</p>
      </section>

      <section className="mt-8 space-y-2 text-sm leading-relaxed">
        <h2 className="text-xl font-semibold">{legal.processedDataTitle}</h2>
        <ul className="list-disc space-y-1.5 pl-5">
          {legal.processedDataItems.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="mt-8 space-y-2 text-sm leading-relaxed">
        <h2 className="text-xl font-semibold">{legal.legalBasisTitle}</h2>
        <p>{legal.legalBasisBody}</p>
      </section>

      <section className="mt-8 space-y-2 text-sm leading-relaxed">
        <h2 className="text-xl font-semibold">{legal.aiProcessingTitle}</h2>
        <p>{legal.aiProcessingBody}</p>
      </section>

      <section className="mt-8 space-y-2 text-sm leading-relaxed">
        <h2 className="text-xl font-semibold">{legal.cookiesTitle}</h2>
        <p>{legal.cookiesBody}</p>
      </section>

      <section className="mt-8 space-y-2 text-sm leading-relaxed">
        <h2 className="text-xl font-semibold">{legal.processorsTitle}</h2>
        <p>{legal.processorsBody}</p>
      </section>

      <section className="mt-8 space-y-2 text-sm leading-relaxed">
        <h2 className="text-xl font-semibold">{legal.retentionTitle}</h2>
        <p>{legal.retentionBody}</p>
      </section>

      <section className="mt-8 space-y-2 text-sm leading-relaxed">
        <h2 className="text-xl font-semibold">{legal.marketingCommsTitle}</h2>
        <p>{legal.marketingCommsBody}</p>
      </section>

      <section className="mt-8 space-y-3 text-sm leading-relaxed">
        <h2 className="text-xl font-semibold">{legal.userRightsTitle}</h2>
        <p>{legal.userRightsBody}</p>
        <p>
          {legal.userRightsSupervisoryBody}{" "}
          <Link
            href={legal.userRightsSupervisoryHref}
            className="underline underline-offset-2"
            style={{ color: accent }}
            target="_blank"
            rel="noopener noreferrer"
          >
            {legal.userRightsSupervisoryLinkLabel}
          </Link>
        </p>
      </section>

      <section className="mt-8 space-y-2 text-sm leading-relaxed">
        <h2 className="text-xl font-semibold">{legal.deletionTitle}</h2>
        <p>{legal.deletionMvpScope}</p>
        <ul className="list-disc space-y-1.5 pl-5">
          <li>
            {legal.deletionContactLabel}: {legal.deletionContactEmail}
          </li>
          <li>
            {legal.deletionAckSlaLabel}: {legal.deletionAckSlaValue}
          </li>
          <li>
            {legal.deletionCompletionSlaLabel}: {legal.deletionCompletionSlaValue}
          </li>
        </ul>
      </section>

      <section className="mt-8 space-y-2 text-sm leading-relaxed">
        <h2 className="text-xl font-semibold">{legal.updatesTitle}</h2>
        <p>{legal.updatesBody}</p>
      </section>
    </main>
  );
}
