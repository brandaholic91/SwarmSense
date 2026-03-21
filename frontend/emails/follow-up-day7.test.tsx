import { render } from "@react-email/render";

import { FollowUpDay7Email } from "@/emails/follow-up-day7";

describe("FollowUpDay7Email", () => {
  it("renders functional unsubscribe link", async () => {
    const html = await render(
      <FollowUpDay7Email unsubscribe_url="https://example.com/api/v1/unsubscribe?user_id=abc" />
    );

    expect(html).toContain("Leiratkozas");
    expect(html).toContain("https://example.com/api/v1/unsubscribe?user_id=abc");
  });
});
