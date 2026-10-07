import Link from "next/link";

import { getContactLine } from "@/lib/contact";
import { messages } from "@/lib/messages";
import { accent, onSurface, textSecondary } from "@/lib/tokens";

type TermsSection = {
  title: string;
  paragraphs: string[];
  list?: string[];
  linkPrivacy?: boolean;
  methodologyLink?: boolean;
  contact?: boolean;
};

export default async function TermsPage() {
  const legal = messages.legal;
  const sections = legal.termsSections as TermsSection[];
  const contactLine = await getContactLine();

  return (
    <main className="mx-auto max-w-3xl px-6 py-16" style={{ color: onSurface }}>
      <h1 className="text-3xl font-semibold">{legal.termsTitle}</h1>
      <p className="mt-2 text-xs tracking-wide" style={{ color: textSecondary }}>
        {legal.effectiveDate}
      </p>
      <div className="mt-6 space-y-4 text-sm leading-relaxed">
        {legal.termsIntroParagraphs.map((paragraph, i) => (
          <p key={i}>{paragraph}</p>
        ))}
      </div>

      {sections.map((section) => (
        <section key={section.title} className="mt-8 space-y-2 text-sm leading-relaxed">
          <h2 className="text-xl font-semibold">{section.title}</h2>
          {section.paragraphs.map((p, i) => (
            <p key={i}>{p}</p>
          ))}
          {section.list ? (
            <ul className="list-disc space-y-1.5 pl-5">
              {section.list.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : null}
          {section.contact ? <p>{contactLine}</p> : null}
          {section.linkPrivacy ? (
            <p className="pt-1">
              <Link
                href="/privacy"
                className="font-medium underline underline-offset-2"
                style={{ color: accent }}
              >
                {legal.privacyTitle}
              </Link>
            </p>
          ) : null}
          {section.methodologyLink ? (
            <p className="pt-1">
              <Link
                href="/modszertan"
                className="font-medium underline underline-offset-2"
                style={{ color: accent }}
              >
                {legal.methodologyLinkLabel}
              </Link>
            </p>
          ) : null}
        </section>
      ))}
    </main>
  );
}
