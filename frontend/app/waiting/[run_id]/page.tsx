import { WaitingScreen } from "@/components/waiting-screen";

type WaitingPageProps = {
  params: Promise<{ run_id: string }>;
};

export default async function WaitingPage({ params }: WaitingPageProps) {
  const { run_id } = await params;
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL ?? process.env.API_URL ?? "";

  return <WaitingScreen runId={run_id} apiBaseUrl={apiBaseUrl} />;
}
