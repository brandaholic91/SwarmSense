import { messages } from "@/lib/messages";

export default function TermsPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-16">
      <h1 className="text-3xl font-semibold">{messages.legal.termsTitle}</h1>
      <p className="mt-4 text-sm">A használati feltételek hamarosan elérhetők.</p>
    </main>
  );
}
