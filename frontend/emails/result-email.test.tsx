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
  topic: "Érdemes-e 15%-os áremelést végrehajtani?",
  audience: "KKV marketing döntéshozók",
  personas: [
    {
      name: "Kovács Péter",
      role: "CFO, 280 fős SaaS",
      stance: "reject" as const,
      stance_label: "Elutasítja",
      summary: "Az áremelés túl nagy kockázatot jelent a lemorzsolódás szempontjából.",
    },
    {
      name: "Nagy Eszter",
      role: "Marketing vezető, B2B szolgáltató",
      stance: "conditional" as const,
      stance_label: "Feltételes",
      summary: "A minőség és az ügyfélkiszolgálás fejlesztése mellett elfogadható.",
    },
    {
      name: "Horváth Gábor",
      role: "Termékvezető, prémium szegmens",
      stance: "support" as const,
      stance_label: "Támogatja",
      summary: "A prémium pozicionálást erősíti a magasabb árszint.",
    },
  ],
  persona_count: "17/18",
  aggregate_score: "50% támogatja",
  user_email: "teszt@example.com",
};

describe("ResultEmail", () => {
  it("renders all required props and content blocks", async () => {
    const html = await render(
      <ResultEmail
        {...sampleProps}
        consensus_flag="9/18 elutasítja - megosztott eredmény"
      />
    );

    expect(html).toContain(sampleProps.topic);
    expect(html).toContain(sampleProps.audience);
    expect(html).toContain(sampleProps.persona_count);
    expect(html).toContain(sampleProps.aggregate_score);
    expect(html).toContain("9/18 elutasítja - megosztott eredmény");
    expect(html).toContain(sampleProps.user_email);
    expect(html).toContain("Álláspont: Elutasítja");
    expect(html).toContain("Álláspont: Feltételes");
    expect(html).toContain("Álláspont: Támogatja");
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

  it("renders consensus pending label when consensus_flag is absent", async () => {
    const html = await render(<ResultEmail {...sampleProps} />);

    expect(html).toContain("Nincs megadott konszenzus jelzés");
  });

  it("renders consensus pending label when consensus_flag is empty string", async () => {
    const html = await render(<ResultEmail {...sampleProps} consensus_flag="" />);

    expect(html).toContain("Nincs megadott konszenzus jelzés");
  });

  it("renders empty personas array without crashing", async () => {
    const html = await render(<ResultEmail {...sampleProps} personas={[]} />);

    expect(html).toContain("Persona visszajelzések");
    expect(html).not.toContain("Álláspont:");
  });
});
