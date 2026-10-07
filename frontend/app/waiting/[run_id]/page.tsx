import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { LiveTrace } from "@/components/live-trace";
import { isRunId } from "@/lib/backend";

// Futásonkénti, linkkel megosztott oldal: keresők ne indexeljék.
export const metadata: Metadata = {
  robots: { index: false, follow: false },
};

type WaitingPageProps = {
  params: Promise<{ run_id: string }>;
};

export default async function WaitingPage({ params }: WaitingPageProps) {
  const { run_id } = await params;
  if (!isRunId(run_id)) {
    notFound();
  }

  return <LiveTrace runId={run_id} />;
}
