import Link from "next/link";

import { messages } from "@/lib/messages";
import { accent, onSurface } from "@/lib/tokens";

type Section = {
  title: string;
  paragraphs: string[];
  list?: string[];
  after?: string;
};

export default function MethodologyPage() {
  const m = messages.methodology;
  const sections = m.sections as Section[];

  return (
    <main className="mx-auto max-w-3xl px-6 py-16" style={{ color: onSurface }}>
      <h1 className="text-3xl font-semibold">{m.title}</h1>
      <p className="mt-6 text-sm leading-relaxed">{m.intro}</p>

      {sections.map((section) => (
        <section key={section.title} className="mt-8 space-y-2 text-sm leading-relaxed">
          <h2 className="text-xl font-semibold">{section.title}</h2>
          {section.paragraphs.map((p) => (
            <p key={p}>{p}</p>
          ))}
          {section.list ? (
            <ul className="list-disc space-y-1.5 pl-5">
              {section.list.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : null}
          {section.after ? <p>{section.after}</p> : null}
        </section>
      ))}

      <section className="mt-8 space-y-2 text-sm leading-relaxed">
        <h2 className="text-xl font-semibold">{m.sampleHeading}</h2>
        <p>{m.sampleText}</p>
        <p>
          <Link
            href="/minta"
            className="font-medium underline underline-offset-2"
            style={{ color: accent }}
          >
            {m.sampleLink}
          </Link>
        </p>
      </section>
    </main>
  );
}
