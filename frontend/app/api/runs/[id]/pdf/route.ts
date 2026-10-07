import { backendFetch, isRunId } from "@/lib/backend";

export const dynamic = "force-dynamic";

const NO_STORE = { "Cache-Control": "no-store" };
// A backend első kérésre legenerálja a PDF-et (Chromium-indítással), ezért hosszabb a várakozás.
const PDF_TIMEOUT_MS = 90_000;

function json(body: unknown, status: number): Response {
  return Response.json(body, { status, headers: NO_STORE });
}

type RouteContext = { params: Promise<{ id: string }> };

// A böngésző csak ezt a végpontot hívja; a backend címe és a belső titok szerveroldalon marad.
export async function GET(_request: Request, { params }: RouteContext): Promise<Response> {
  const { id } = await params;
  if (!isRunId(id)) {
    return json({ code: "RUN_NOT_FOUND" }, 404);
  }

  try {
    const upstream = await backendFetch(`/api/v1/runs/${id}/pdf`, { timeoutMs: PDF_TIMEOUT_MS });
    // Bináris törzs: arrayBuffer, nem text(), különben a PDF bájtjai megsérülnének.
    const body = await upstream.arrayBuffer();
    const headers = new Headers(NO_STORE);
    for (const name of ["Content-Type", "Content-Disposition"]) {
      const value = upstream.headers.get(name);
      if (value) headers.set(name, value);
    }
    return new Response(body, { status: upstream.status, headers });
  } catch {
    return json({ code: "BACKEND_UNAVAILABLE" }, 502);
  }
}
