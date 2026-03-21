import { render } from "@react-email/render";

import { FollowUpDay3Email } from "@/emails/follow-up-day3";

describe("FollowUpDay3Email", () => {
  it("renders functional unsubscribe link", async () => {
    const html = await render(
      <FollowUpDay3Email unsubscribe_url="https://example.com/api/v1/unsubscribe?user_id=abc" />
    );

    expect(html).toContain("Leiratkozás");
    expect(html).toContain("https://example.com/api/v1/unsubscribe?user_id=abc");
  });
});
