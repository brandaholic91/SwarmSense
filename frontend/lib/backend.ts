import "server-only";

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

// Cloudflare mögött a kliens címe a cf-connecting-ip fejlécben van: ezt a Cloudflare
// mindig felülírja, az x-forwarded-for ott már csak a proxy címét hordozza.
// Cloudflare nélkül az x-forwarded-for első eleme a kliens; a többi a közbenső proxyké.
export function clientIp(headers: Headers): string | null {
  const cloudflare = headers.get("cf-connecting-ip")?.trim();
  if (cloudflare) return cloudflare;

  const forwarded = headers.get("x-forwarded-for");
  if (!forwarded) return null;
  const first = forwarded.split(",")[0]?.trim();
  return first ? first : null;
}

// Hibás (nem 2xx) backendválaszból kifelé csak az állapotkód és egy hibakód megy;
// a backend nyers törzse (HTML, szöveg, részletek) sosem.
export async function upstreamErrorResponse(
  upstream: Response,
  headers: HeadersInit
): Promise<Response> {
  let code = "BACKEND_UNAVAILABLE";
  try {
    const body: unknown = await upstream.json();
    if (typeof body === "object" && body !== null) {
      const candidate = (body as { code?: unknown }).code;
      if (typeof candidate === "string" && candidate !== "") code = candidate;
    }
  } catch {
    // nem JSON törzs: marad az általános kód
  }
  return Response.json({ code }, { status: upstream.status, headers });
}
