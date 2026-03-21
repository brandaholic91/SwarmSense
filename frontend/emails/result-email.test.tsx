import { render } from "@react-email/render";

import { ResultEmail } from "@/emails/result-email";
import {
  accent,
  emailCanvas,
  emailSurface,
  stanceConditional,
  stanceReject,
  stanceSupport,
} from "@/lib/tokens";

const sampleProps = {
  topic: "Erdemes-e 15%-os aremelest vegrehajtani?",
  audience: "KKV marketing donteshozok",
  personas: [
    {
      name: "Kovacs Peter",
      role: "CFO, 280 fos SaaS",
      stance: "reject" as const,
      stance_label: "Elutasitja",
      summary: "Az aremeles tul nagy kockazatot jelent a lemorzsolodas szempontjabol.",
    },
    {
      name: "Nagy Eszter",
      role: "Marketing vezeto, B2B szolgaltato",
      stance: "conditional" as const,
      stance_label: "Felteteles",
      summary: "A minoseg es az ugyfelkiszolgalas fejlesztese mellett elfogadhato.",
    },
    {
      name: "Horvath Gabor",
      role: "Termekvezeto, premium szegmens",
      stance: "support" as const,
      stance_label: "Tamogatja",
      summary: "A premium pozicionalast erositi a magasabb arszint.",
    },
  ],
  persona_count: "17/18",
  aggregate_score: "50% tamogatja",
  user_email: "teszt@example.com",
};

describe("ResultEmail", () => {
  it("renders all required props and content blocks", async () => {
    const html = await render(
      <ResultEmail
        {...sampleProps}
        consensus_flag="9/18 elutasitja - megosztott eredmeny"
      />
    );

    expect(html).toContain(sampleProps.topic);
    expect(html).toContain(sampleProps.audience);
    expect(html).toContain(sampleProps.persona_count);
    expect(html).toContain(sampleProps.aggregate_score);
    expect(html).toContain("9/18 elutasitja - megosztott eredmeny");
    expect(html).toContain(sampleProps.user_email);
    expect(html).toContain("Allaspont: Elutasitja");
    expect(html).toContain("Allaspont: Felteteles");
    expect(html).toContain("Allaspont: Tamogatja");
  });

  it("sets semantic root attributes and presentation table roles", async () => {
    const html = await render(<ResultEmail {...sampleProps} />);

    expect(html).toContain('lang="hu"');
    expect(html).toContain('role="presentation"');
  });

  it("uses token-driven inline colors for canvas, accents and stances", async () => {
    const html = await render(<ResultEmail {...sampleProps} />);

    expect(html).toContain(`background-color:${emailCanvas}`);
    expect(html).toContain(`background-color:${emailSurface}`);
    expect(html).toContain(`border-top:2px solid ${accent}`);
    expect(html).toContain(`border-left:4px solid ${stanceReject}`);
    expect(html).toContain(`border-left:4px solid ${stanceConditional}`);
    expect(html).toContain(`border-left:4px solid ${stanceSupport}`);
  });

  it("renders deterministic html without runtime errors", async () => {
    const firstRender = await render(<ResultEmail {...sampleProps} />);
    const secondRender = await render(<ResultEmail {...sampleProps} />);

    expect(firstRender).toBe(secondRender);
  });
});
