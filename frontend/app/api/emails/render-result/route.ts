import { NextRequest, NextResponse } from "next/server";

import { render } from "@react-email/render";

import { ResultEmail, type ResultEmailPersona, type ResultEmailSynthesis } from "@/emails/result-email";

export interface ResultEmailRenderRequest {
  topic: string;
  audience: string;
  personas: ResultEmailPersona[];
  persona_count: string;
  aggregate_score: string;
  consensus_flag?: string;
  synthesis?: ResultEmailSynthesis;
  user_email: string;
  unsubscribe_url?: string;
  waitlist_url?: string;
}

export async function POST(request: NextRequest) {
  try {
    const body: ResultEmailRenderRequest = await request.json();

    const html = await render(
      ResultEmail({
        topic: body.topic,
        audience: body.audience,
        personas: body.personas,
        persona_count: body.persona_count,
        aggregate_score: body.aggregate_score,
        consensus_flag: body.consensus_flag,
        synthesis: body.synthesis,
        user_email: body.user_email,
        unsubscribe_url: body.unsubscribe_url,
        waitlist_url: body.waitlist_url,
      })
    );

    return NextResponse.json({ html });
  } catch (error) {
    console.error("Failed to render result email:", error);
    return NextResponse.json(
      { error: "Failed to render email" },
      { status: 500 }
    );
  }
}
