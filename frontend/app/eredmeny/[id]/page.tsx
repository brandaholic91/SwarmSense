import { notFound, redirect } from "next/navigation";

import { ResultView } from "@/components/result-view";
import { fetchRun } from "@/lib/run";

// Futásonként változó adat: a build ne próbálja előállítani.
export const dynamic = "force-dynamic";

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

  return <ResultView run={run} />;
}
