import { notFound } from "next/navigation";

import { LiveTrace } from "@/components/live-trace";
import { isRunId } from "@/lib/backend";

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
