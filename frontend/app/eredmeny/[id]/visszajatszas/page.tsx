import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { ReplayTrace } from "@/components/replay-trace";
import { isRunId } from "@/lib/backend";

// Futásonkénti, linkkel megosztott oldal: keresők ne indexeljék.
export const metadata: Metadata = {
  robots: { index: false, follow: false },
};

type ReplayPageProps = {
  params: Promise<{ id: string }>;
};

export default async function ReplayPage({ params }: ReplayPageProps) {
  const { id } = await params;
  if (!isRunId(id)) {
    notFound();
  }
  return <ReplayTrace runId={id} />;
}
