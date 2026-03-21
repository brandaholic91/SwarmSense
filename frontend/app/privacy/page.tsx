import { messages } from "@/lib/messages";

export default function PrivacyPage() {
  const legal = messages.legal;

  return (
    <main className="mx-auto max-w-3xl px-6 py-16">
      <h1 className="text-3xl font-semibold">{legal.privacyTitle}</h1>
      <p className="mt-4 text-sm">{legal.privacyIntro}</p>

      <section className="mt-8 space-y-2 text-sm">
        <h2 className="text-xl font-semibold">{legal.controllerTitle}</h2>
        <p>{legal.controllerBody}</p>
      </section>

      <section className="mt-8 space-y-2 text-sm">
        <h2 className="text-xl font-semibold">{legal.processedDataTitle}</h2>
        <ul className="list-disc space-y-1 pl-5">
          {legal.processedDataItems.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="mt-8 space-y-2 text-sm">
        <h2 className="text-xl font-semibold">{legal.legalBasisTitle}</h2>
        <p>{legal.legalBasisBody}</p>
      </section>

      <section className="mt-8 space-y-2 text-sm">
        <h2 className="text-xl font-semibold">{legal.retentionTitle}</h2>
        <p>{legal.retentionBody}</p>
      </section>

      <section className="mt-8 space-y-2 text-sm">
        <h2 className="text-xl font-semibold">{legal.deletionTitle}</h2>
        <p>{legal.deletionMvpScope}</p>
        <ul className="list-disc space-y-1 pl-5">
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

      <section className="mt-8 space-y-2 text-sm">
        <h2 className="text-xl font-semibold">{legal.userRightsTitle}</h2>
        <p>{legal.userRightsBody}</p>
      </section>

      <section className="mt-8 space-y-2 text-sm">
        <h2 className="text-xl font-semibold">{legal.updatesTitle}</h2>
        <p>{legal.updatesBody}</p>
      </section>
    </main>
  );
}
