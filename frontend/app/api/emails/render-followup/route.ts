import { NextRequest, NextResponse } from "next/server";

import { render } from "@react-email/render";

import { FollowUpDay1Email } from "@/emails/follow-up-day1";
import { FollowUpDay3Email } from "@/emails/follow-up-day3";
import { FollowUpDay7Email } from "@/emails/follow-up-day7";

export interface FollowUpEmailRenderRequest {
  day: "day1" | "day3" | "day7";
  unsubscribe_url: string;
}

export async function POST(request: NextRequest) {
  try {
    const body: FollowUpEmailRenderRequest = await request.json();

    let html: string;
    if (body.day === "day1") {
      html = render(FollowUpDay1Email({ unsubscribe_url: body.unsubscribe_url }));
    } else if (body.day === "day3") {
      html = render(FollowUpDay3Email({ unsubscribe_url: body.unsubscribe_url }));
    } else {
      html = render(FollowUpDay7Email({ unsubscribe_url: body.unsubscribe_url }));
    }

    return NextResponse.json({ html });
  } catch (error) {
    console.error("Failed to render follow-up email:", error);
    return NextResponse.json({ error: "Failed to render email" }, { status: 500 });
  }
}
