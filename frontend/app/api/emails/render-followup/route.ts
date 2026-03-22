import { NextRequest, NextResponse } from "next/server";

import { render } from "@react-email/render";

import { FollowUpDay1Email } from "@/emails/follow-up-day1";
import { FollowUpDay3Email } from "@/emails/follow-up-day3";
import { FollowUpDay7Email } from "@/emails/follow-up-day7";

export interface FollowUpEmailRenderRequest {
  day: "day1" | "day3" | "day7";
  unsubscribe_url: string;
  topic?: string | null;
  audience?: string | null;
  support_count?: number | null;
  reject_count?: number | null;
  conditional_count?: number | null;
  synthesis_summary?: string | null;
  synthesis_main_barriers?: string[] | null;
  synthesis_winning_conditions?: string | null;
  synthesis_best_target_segment?: string | null;
  synthesis_strategic_recommendation?: string | null;
}

export async function POST(request: NextRequest) {
  try {
    const body: FollowUpEmailRenderRequest = await request.json();

    if (body.day !== "day1" && body.day !== "day3" && body.day !== "day7") {
      return NextResponse.json({ error: "Invalid day value" }, { status: 400 });
    }

    const researchProps = {
      topic: body.topic,
      audience: body.audience,
      support_count: body.support_count,
      reject_count: body.reject_count,
      conditional_count: body.conditional_count,
      synthesis_summary: body.synthesis_summary,
      synthesis_main_barriers: body.synthesis_main_barriers,
      synthesis_winning_conditions: body.synthesis_winning_conditions,
      synthesis_best_target_segment: body.synthesis_best_target_segment,
      synthesis_strategic_recommendation: body.synthesis_strategic_recommendation,
    };

    let html: string;
    if (body.day === "day1") {
      html = await render(
        FollowUpDay1Email({ unsubscribe_url: body.unsubscribe_url, ...researchProps })
      );
    } else if (body.day === "day3") {
      html = await render(
        FollowUpDay3Email({ unsubscribe_url: body.unsubscribe_url, ...researchProps })
      );
    } else {
      html = await render(
        FollowUpDay7Email({ unsubscribe_url: body.unsubscribe_url, ...researchProps })
      );
    }

    return NextResponse.json({ html });
  } catch (error) {
    console.error("Failed to render follow-up email:", error);
    return NextResponse.json({ error: "Failed to render email" }, { status: 500 });
  }
}
