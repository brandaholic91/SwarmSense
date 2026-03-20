import Link from "next/link";

import { messages } from "@/lib/messages";

export default function BlockedPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col items-start justify-center px-6 py-16">
      <h1 className="text-3xl font-semibold">{messages.blockingHeadline}</h1>
      <p className="mt-4 text-base">{messages.blockingPage.description}</p>
      <Link href="/" className="mt-8 inline-flex rounded-lg border px-4 py-2 text-sm font-semibold">
        {messages.blockingPage.cta}
      </Link>
    </main>
  );
}
