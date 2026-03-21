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
      primary_argument:
        "Az áremelés túl nagy kockázatot jelent a lemorzsolódás szempontjából.",
      change_condition: "Ha az ügyfélmegtartási tervet előre hitelesen kommunikálják.",
    },
    {
      name: "Nagy Eszter",
      role: "Marketing vezető, B2B szolgáltató",
      stance: "conditional" as const,
      stance_label: "Feltételes",
      primary_argument: "A minőség és az ügyfélkiszolgálás fejlesztése mellett elfogadható.",
      change_condition: "Ha bizonyíthatóan nő az észlelt érték és a szolgáltatási szint.",
    },
    {
      name: "Horváth Gábor",
      role: "Termékvezető, prémium szegmens",
      stance: "support" as const,
      stance_label: "Támogatja",
      primary_argument: "A prémium pozicionálást erősíti a magasabb árszint.",
      change_condition: "Ha a termékdifferenciálás továbbra is jól látható marad.",
    },
  ],
  persona_count: "17/18",
  aggregate_score: "Támogatja: 9 | Elutasítja: 7 | Feltételes: 2",
  user_email: "teszt@example.com",
};

describe("ResultEmail", () => {
  it("renders above-the-fold order as consensus then aggregate score", async () => {
    const consensus = "15 persona támogatja";
    const html = await render(
      <ResultEmail {...sampleProps} consensus_flag={consensus} />
    );

    const consensusIndex = html.indexOf(consensus);
    const aggregateIndex = html.indexOf(sampleProps.aggregate_score);

    expect(consensusIndex).toBeGreaterThan(-1);
    expect(aggregateIndex).toBeGreaterThan(-1);
    expect(consensusIndex).toBeLessThan(aggregateIndex);
  });

  it("renders consensus block with alert role when consensus exists", async () => {
    const html = await render(
      <ResultEmail {...sampleProps} consensus_flag="15 persona támogatja" />
    );

    expect(html).toContain('role="alert"');
    expect(html).toContain("⚠ Konszenzus jelzés");
  });

  it("renders consensus pending label when consensus_flag is absent", async () => {
    const html = await render(<ResultEmail {...sampleProps} />);

    expect(html).toContain("Nincs megadott konszenzus jelzés");
    expect(html).not.toContain('role="alert"');
  });

  it("renders consensus pending label when consensus_flag is empty string", async () => {
    const html = await render(<ResultEmail {...sampleProps} consensus_flag="" />);

    expect(html).toContain("Nincs megadott konszenzus jelzés");
    expect(html).not.toContain('role="alert"');
  });

  it("renders full persona argument model and disclaimer", async () => {
    const html = await render(
      <ResultEmail {...sampleProps} consensus_flag="15 persona támogatja" />
    );

    expect(html).toContain("Álláspont: Elutasítja");
    expect(html).toContain("Elsődleges érv");
    expect(html).toContain(
      "Az áremelés túl nagy kockázatot jelent a lemorzsolódás szempontjából."
    );
    expect(html).toContain("Mi változtatná meg a véleményét");
    expect(html).toContain(
      "Ha az ügyfélmegtartási tervet előre hitelesen kommunikálják."
    );
    expect(html).toContain(
      "Fontos: az itt látható eredmények AI-alapú szintetikus szimulációból származnak, nem valós emberi kutatásból."
    );
  });

  it("renders semantic root attributes and responsive presentation table markers", async () => {
    const html = await render(<ResultEmail {...sampleProps} />);

    expect(html).toContain('lang="hu"');
    expect(html).toContain('role="presentation"');
    expect(html).toContain("persona-column");
    expect(html).toContain("@media only screen and (max-width: 620px)");
    expect(html).toContain("width:33.333%");
  });

  it("uses token-driven inline colors for canvas, accents and stance borders", async () => {
    const html = await render(
      <ResultEmail {...sampleProps} consensus_flag="15 persona támogatja" />
    );

    expect(html).toContain(`background-color:${emailCanvas}`);
    expect(html).toContain(`background-color:${emailSurface}`);
    expect(html).toContain(`border-top:2px solid ${accent}`);
    expect(html).toContain(`border:2px solid ${accent}`);
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
