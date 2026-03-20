import { BlockingScreen } from "@/components/blocking-screen";

type BlockedPageProps = {
  searchParams?: Promise<{ email?: string }> | { email?: string };
};

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function normalizeEmail(rawValue: string | undefined): string | null {
  if (!rawValue) {
    return null;
  }

  const normalized = rawValue.trim().toLowerCase();
  if (!EMAIL_PATTERN.test(normalized)) {
    return null;
  }

  return normalized;
}

export default async function BlockedPage({ searchParams }: BlockedPageProps) {
  const resolvedSearchParams = await Promise.resolve(searchParams ?? {});
  const rawEmail = Array.isArray(resolvedSearchParams.email)
    ? resolvedSearchParams.email[0]
    : resolvedSearchParams.email;
  const normalizedEmail = normalizeEmail(rawEmail);

  return <BlockingScreen email={normalizedEmail} canSubmitWaitlist={Boolean(normalizedEmail)} />;
}
