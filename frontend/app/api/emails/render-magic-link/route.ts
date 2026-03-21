import { NextRequest, NextResponse } from "next/server";

import { render } from "@react-email/render";

import { MagicLinkEmail } from "@/emails/magic-link-email";

export interface MagicLinkEmailRenderRequest {
  verify_url: string;
}

export async function POST(request: NextRequest) {
  try {
    const body: MagicLinkEmailRenderRequest = await request.json();

    const html = await render(MagicLinkEmail({ verifyUrl: body.verify_url }));

    return NextResponse.json({ html });
  } catch (error) {
    console.error("Failed to render magic link email:", error);
    return NextResponse.json({ error: "Failed to render email" }, { status: 500 });
  }
}
