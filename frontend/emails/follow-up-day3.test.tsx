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

  it("renders research summary section when topic is present", async () => {
    const html = await render(
      <FollowUpDay3Email
        unsubscribe_url="https://example.com/unsubscribe"
        topic="AI piac felmérés"
        audience="KKV döntéshozók"
        support_count={10}
        reject_count={3}
        conditional_count={7}
        synthesis_summary="Összefoglalás szövege"
      />
    );

    expect(html).toContain("A kutatásod eredménye");
    expect(html).toContain("AI piac felmérés");
    expect(html).toContain("KKV döntéshozók");
    expect(html).toContain("Összefoglalás szövege");
  });

  it("omits research summary section when topic is null", async () => {
    const html = await render(
      <FollowUpDay3Email unsubscribe_url="https://example.com/unsubscribe" topic={null} />
    );

    expect(html).not.toContain("A kutatásod eredménye");
  });
});
