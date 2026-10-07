import type { Metadata } from "next";
import { notFound, redirect } from "next/navigation";

import { EmailRequestForm } from "@/components/email-request-form";
import { ResultView } from "@/components/result-view";
import { fetchRun } from "@/lib/run";

// Futásonként változó adat: a build ne próbálja előállítani.
export const dynamic = "force-dynamic";

// Futásonkénti, linkkel megosztott oldal: keresők ne indexeljék.
export const metadata: Metadata = {
  robots: { index: false, follow: false },
};

type ResultPageProps = {
  params: Promise<{ id: string }>;
};

export default async function ResultPage({ params }: ResultPageProps) {
  const { id } = await params;
  const run = await fetchRun(id);
  if (run === null) {
    notFound();
  }
  if (run.status === "queued" || run.status === "running" || run.status === "composing") {
    redirect(`/waiting/${id}`);
  }

  const hasResult = run.status === "completed" || run.status === "partial";

  return (
    <ResultView run={run}>
      {hasResult ? (
        <EmailRequestForm runId={run.run_id} emailsRemaining={run.emails_remaining} />
      ) : null}
    </ResultView>
  );
}
