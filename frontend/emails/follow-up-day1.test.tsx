import { render } from "@react-email/render";

import { FollowUpDay1Email } from "@/emails/follow-up-day1";

describe("FollowUpDay1Email", () => {
  it("renders functional unsubscribe link", async () => {
    const html = await render(
      <FollowUpDay1Email unsubscribe_url="https://example.com/api/v1/unsubscribe?user_id=abc" />
    );

    expect(html).toContain("Leiratkozás");
    expect(html).toContain("https://example.com/api/v1/unsubscribe?user_id=abc");
  });

  it("renders research summary section when topic is present", async () => {
    const html = await render(
      <FollowUpDay1Email
        unsubscribe_url="https://example.com/unsubscribe"
        topic="AI piac felmérés"
        audience="KKV döntéshozók"
        support_count={10}
        reject_count={3}
        conditional_count={7}
        synthesis_summary="Összefoglalás szövege"
        synthesis_main_barriers={["Akadály 1", "Akadály 2"]}
        synthesis_winning_conditions="Siker feltételei"
        synthesis_best_target_segment="Szegmens leírás"
        synthesis_strategic_recommendation="Stratégiai ajánlás"
      />
    );

    expect(html).toContain("A kutatásod eredménye");
    expect(html).toContain("AI piac felmérés");
    expect(html).toContain("KKV döntéshozók");
    // React Email inserts comment nodes between JSX expressions, check parts separately
    expect(html).toContain("támogatta");
    expect(html).toContain("feltételes");
    expect(html).toContain("elutasította");
    expect(html).toContain("Összefoglalás szövege");
    expect(html).toContain("Akadály 1");
    expect(html).toContain("Akadály 2");
    expect(html).toContain("Siker feltételei");
    expect(html).toContain("Szegmens leírás");
    expect(html).toContain("Stratégiai ajánlás");
  });

  it("omits research summary section when topic is null", async () => {
    const html = await render(
      <FollowUpDay1Email
        unsubscribe_url="https://example.com/unsubscribe"
        topic={null}
        synthesis_summary={null}
      />
    );

    expect(html).not.toContain("A kutatásod eredménye");
    expect(html).toContain("Leiratkozás");
  });

  it("omits research summary section when synthesis is missing", async () => {
    const html = await render(
      <FollowUpDay1Email
        unsubscribe_url="https://example.com/unsubscribe"
        topic="AI piac felmérés"
        audience="KKV döntéshozók"
        synthesis_summary={null}
        synthesis_main_barriers={null}
        synthesis_winning_conditions={null}
        synthesis_best_target_segment={null}
        synthesis_strategic_recommendation={null}
      />
    );

    expect(html).not.toContain("A kutatásod eredménye");
  });

  it("omits research summary section when topic is undefined", async () => {
    const html = await render(
      <FollowUpDay1Email unsubscribe_url="https://example.com/unsubscribe" />
    );

    expect(html).not.toContain("A kutatásod eredménye");
  });
});
