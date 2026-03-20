import { VerifyClient } from "./verify-client";

type VerifyPageProps = {
  searchParams?: Promise<{ token?: string }> | { token?: string };
};

export default async function VerifyPage({ searchParams }: VerifyPageProps) {
  const resolvedSearchParams = await Promise.resolve(searchParams ?? {});
  const token = resolvedSearchParams.token ?? "";
  return <VerifyClient token={token} />;
}
