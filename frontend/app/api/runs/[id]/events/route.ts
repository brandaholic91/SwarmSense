import { backendFetch, isRunId } from "@/lib/backend";

export const dynamic = "force-dynamic";

const NO_STORE = { "Cache-Control": "no-store" };

function json(body: unknown, status: number): Response {
  return Response.json(body, { status, headers: NO_STORE });
}

type RouteContext = { params: Promise<{ id: string }> };

// A böngésző csak ezt a végpontot hívja; a backend címe és a belső titok szerveroldalon marad.
export async function GET(request: Request, { params }: RouteContext): Promise<Response> {
  const { id } = await params;
  if (!isRunId(id)) {
    return json({ code: "RUN_NOT_FOUND" }, 404);
  }

  const rawAfter = new URL(request.url).searchParams.get("after") ?? "0";
  if (!/^\d+$/.test(rawAfter)) {
    return json({ code: "INVALID_INPUT" }, 400);
  }

  try {
    const upstream = await backendFetch(`/api/v1/runs/${id}/events?after=${Number(rawAfter)}`);
    const body = await upstream.text();
    return new Response(body, {
      status: upstream.status,
      headers: {
        "Content-Type": upstream.headers.get("content-type") ?? "application/json",
        ...NO_STORE,
      },
    });
  } catch {
    return json({ code: "BACKEND_UNAVAILABLE" }, 502);
  }
}
