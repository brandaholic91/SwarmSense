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

    if (body.day !== "day1" && body.day !== "day3" && body.day !== "day7") {
      return NextResponse.json({ error: "Invalid day value" }, { status: 400 });
    }

    let html: string;
    if (body.day === "day1") {
      html = await render(
        FollowUpDay1Email({ unsubscribe_url: body.unsubscribe_url })
      );
    } else if (body.day === "day3") {
      html = await render(
        FollowUpDay3Email({ unsubscribe_url: body.unsubscribe_url })
      );
    } else {
      html = await render(
        FollowUpDay7Email({ unsubscribe_url: body.unsubscribe_url })
      );
    }

    return NextResponse.json({ html });
  } catch (error) {
    console.error("Failed to render follow-up email:", error);
    return NextResponse.json({ error: "Failed to render email" }, { status: 500 });
  }
}
