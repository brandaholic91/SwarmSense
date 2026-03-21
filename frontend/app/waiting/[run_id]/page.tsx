import { cookies } from "next/headers";

import { WaitingScreen } from "@/components/waiting-screen";

type WaitingPageProps = {
  params: Promise<{ run_id: string }>;
};

export default async function WaitingPage({ params }: WaitingPageProps) {
  const { run_id } = await params;
  const cookieStore = await cookies();
  const email = cookieStore.get("swarmsense_result_email")?.value ?? null;
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL ?? process.env.API_URL ?? "";

  return <WaitingScreen runId={run_id} email={email} apiBaseUrl={apiBaseUrl} />;
}
