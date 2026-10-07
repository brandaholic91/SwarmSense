import Link from "next/link";

import { ReplayTrace } from "@/components/replay-trace";
import { messages } from "@/lib/messages";
import { fetchSampleRunId } from "@/lib/run";
import { accent, onSurface } from "@/lib/tokens";

// A minta a háttértől függ: a build ne próbálja előállítani.
export const dynamic = "force-dynamic";

export default async function SamplePage() {
  const runId = await fetchSampleRunId();
  if (runId === null) {
    return (
      <div className="mx-auto w-full max-w-3xl space-y-6 px-6 py-12" style={{ color: onSurface }}>
        <p className="text-lg font-semibold">{messages.replay.sampleUnavailable}</p>
        <Link href="/research" style={{ color: accent }} className="text-sm font-semibold underline underline-offset-4">
          {messages.trace.formLink}
        </Link>
      </div>
    );
  }
  return <ReplayTrace runId={runId} />;
}
