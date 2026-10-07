const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const DEFAULT_TIMEOUT_MS = 10_000;

// Csak szerveroldalon importálható: a backend címe és a belső titok nem kerülhet a böngészőbe.
export async function backendFetch(
  path: string,
  init: RequestInit & { timeoutMs?: number } = {}
): Promise<Response> {
  const apiUrl = process.env.API_URL;
  const internalSecret = process.env.INTERNAL_SECRET;
  if (!apiUrl || !internalSecret) {
    throw new Error("API_URL or INTERNAL_SECRET is not configured");
  }

  const { timeoutMs = DEFAULT_TIMEOUT_MS, headers, ...rest } = init;
  const merged = new Headers(headers);
  merged.set("X-Internal-Secret", internalSecret);

  return fetch(`${apiUrl}${path}`, {
    ...rest,
    headers: merged,
    cache: "no-store",
    signal: AbortSignal.timeout(timeoutMs),
  });
}

export function isRunId(value: string): boolean {
  return UUID_PATTERN.test(value);
}

// Az x-forwarded-for első eleme a kliens címe; a többi a közbenső proxykoké.
export function clientIp(headers: Headers): string | null {
  const forwarded = headers.get("x-forwarded-for");
  if (!forwarded) return null;
  const first = forwarded.split(",")[0]?.trim();
  return first ? first : null;
}
