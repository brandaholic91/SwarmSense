import { render } from "@react-email/render";

import { FollowUpDay1Email } from "@/emails/follow-up-day1";

describe("FollowUpDay1Email", () => {
  it("renders functional unsubscribe link", async () => {
    const html = await render(
      <FollowUpDay1Email unsubscribe_url="https://example.com/api/v1/unsubscribe?user_id=abc" />
    );

    expect(html).toContain("Leiratkozas");
    expect(html).toContain("https://example.com/api/v1/unsubscribe?user_id=abc");
  });
});
