import { Body, Head, Html, Preview } from "@react-email/components";

import { ConsensusFlagEmail } from "@/emails/consensus-flag-email";
import { PersonaCardEmail, type PersonaStance } from "@/emails/persona-card-email";
import { messages } from "@/lib/messages";
import {
  accent,
  emailBorder,
  emailCanvas,
  emailSurface,
  emailTextPrimary,
  emailTextSecondary,
} from "@/lib/tokens";

export type ResultEmailPersona = {
  name: string;
  role: string;
  stance: PersonaStance;
  stance_label: string;
  primary_argument: string;
  change_condition: string;
};

export type ResultEmailProps = {
  topic: string;
  audience: string;
  personas: ResultEmailPersona[];
  persona_count: string;
  aggregate_score: string;
  consensus_flag?: string;
  user_email: string;
};

function groupPersonas(personas: ResultEmailPersona[]): ResultEmailPersona[][] {
  const rows: ResultEmailPersona[][] = [];
  for (let index = 0; index < personas.length; index += 3) {
    rows.push(personas.slice(index, index + 3));
  }
  return rows;
}

export function ResultEmail({
  topic,
  audience,
  personas,
  persona_count,
  aggregate_score,
  consensus_flag,
  user_email,
}: ResultEmailProps) {
  const copy = messages.email.result;
  const personaRows = groupPersonas(personas ?? []);

  return (
    <Html lang="hu">
      <Head>
        <style>{`
          @media only screen and (max-width: 620px) {
            .persona-column {
              display: block !important;
              width: 100% !important;
              padding-right: 0 !important;
              padding-left: 0 !important;
              padding-bottom: 12px !important;
            }
          }
        `}</style>
      </Head>
      <Preview>{copy.preview}</Preview>
      <Body
        style={{
          margin: 0,
          padding: 0,
          backgroundColor: emailCanvas,
          color: emailTextPrimary,
          fontFamily: "Arial, sans-serif",
        }}
      >
        <table
          role="presentation"
          width="100%"
          cellPadding={0}
          cellSpacing={0}
          style={{ width: "100%", padding: "24px 12px", backgroundColor: emailCanvas }}
        >
          <tbody>
            <tr>
              <td align="center">
                <table
                  role="presentation"
                  width="100%"
                  cellPadding={0}
                  cellSpacing={0}
                  style={{
                    width: "100%",
                    maxWidth: "640px",
                    border: `1px solid ${emailBorder}`,
                    backgroundColor: emailSurface,
                  }}
                >
                  <tbody>
                    <tr>
                      <td style={{ padding: "28px 24px 12px 24px" }}>
                        <h1
                          style={{
                            margin: 0,
                            color: emailTextPrimary,
                            fontSize: "28px",
                            lineHeight: "34px",
                            fontWeight: 700,
                          }}
                        >
                          {copy.title}
                        </h1>
                        <p
                          style={{
                            margin: "12px 0 0 0",
                            color: emailTextSecondary,
                            fontSize: "15px",
                            lineHeight: "24px",
                          }}
                        >
                          {copy.intro}
                        </p>
                      </td>
                    </tr>

                    <tr>
                      <td style={{ padding: "4px 24px 0 24px" }}>
                        <table role="presentation" width="100%" cellPadding={0} cellSpacing={0}>
                          <tbody>
                            <tr>
                              <td
                                style={{
                                  width: "100%",
                                  borderTop: `2px solid ${accent}`,
                                  fontSize: 0,
                                  lineHeight: 0,
                                  height: "2px",
                                }}
                              >
                                &nbsp;
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </td>
                    </tr>

                    {consensus_flag ? (
                      <tr>
                        <td style={{ padding: "20px 24px 0 24px" }}>
                          <ConsensusFlagEmail
                            label={copy.consensusLabel}
                            value={consensus_flag}
                          />
                        </td>
                      </tr>
                    ) : null}

                    <tr>
                      <td style={{ padding: "20px 24px 0 24px" }}>
                        <p style={{ margin: 0, color: emailTextSecondary, fontSize: "12px", lineHeight: "18px" }}>
                          {copy.aggregateScoreLabel}
                        </p>
                        <p
                          style={{
                            margin: "4px 0 0 0",
                            color: emailTextPrimary,
                            fontSize: "20px",
                            lineHeight: "30px",
                            fontWeight: 700,
                          }}
                        >
                          {aggregate_score}
                        </p>
                      </td>
                    </tr>

                    <tr>
                      <td style={{ padding: "16px 24px 8px 24px" }}>
                        <p style={{ margin: 0, color: emailTextSecondary, fontSize: "12px", lineHeight: "18px" }}>
                          {copy.topicLabel}
                        </p>
                        <p
                          style={{
                            margin: "4px 0 0 0",
                            color: emailTextPrimary,
                            fontSize: "16px",
                            lineHeight: "24px",
                            fontWeight: 600,
                          }}
                        >
                          {topic}
                        </p>
                      </td>
                    </tr>

                    <tr>
                      <td style={{ padding: "8px 24px" }}>
                        <p style={{ margin: 0, color: emailTextSecondary, fontSize: "12px", lineHeight: "18px" }}>
                          {copy.audienceLabel}
                        </p>
                        <p
                          style={{
                            margin: "4px 0 0 0",
                            color: emailTextPrimary,
                            fontSize: "16px",
                            lineHeight: "24px",
                            fontWeight: 600,
                          }}
                        >
                          {audience}
                        </p>
                      </td>
                    </tr>

                    <tr>
                      <td style={{ padding: "8px 24px" }}>
                        <p style={{ margin: 0, color: emailTextSecondary, fontSize: "12px", lineHeight: "18px" }}>
                          {copy.personaCountLabel}
                        </p>
                        <p
                          style={{
                            margin: "4px 0 0 0",
                            color: emailTextPrimary,
                            fontSize: "16px",
                            lineHeight: "24px",
                            fontWeight: 700,
                          }}
                        >
                          {persona_count}
                        </p>
                      </td>
                    </tr>

                    {!consensus_flag ? (
                      <tr>
                        <td style={{ padding: "8px 24px 0 24px" }}>
                          <p style={{ margin: 0, color: emailTextSecondary, fontSize: "12px", lineHeight: "18px" }}>
                            {copy.consensusLabel}
                          </p>
                          <p
                            style={{
                              margin: "4px 0 0 0",
                              color: emailTextPrimary,
                              fontSize: "15px",
                              lineHeight: "24px",
                              fontWeight: 600,
                            }}
                          >
                            {copy.consensusPending}
                          </p>
                        </td>
                      </tr>
                    ) : null}

                    <tr>
                      <td style={{ padding: "18px 24px 10px 24px" }}>
                        <h2
                          style={{
                            margin: 0,
                            color: emailTextPrimary,
                            fontSize: "18px",
                            lineHeight: "24px",
                            fontWeight: 700,
                          }}
                        >
                          {copy.personasTitle}
                        </h2>
                      </td>
                    </tr>

                    {personaRows.map((row, rowIndex) => (
                      <tr key={`row-${rowIndex}`}>
                        <td style={{ padding: "0 24px 0 24px" }}>
                          <table role="presentation" width="100%" cellPadding={0} cellSpacing={0}>
                            <tbody>
                              <tr>
                                {row.map((persona, columnIndex) => (
                                  <td
                                    key={`${persona.name}-${columnIndex}`}
                                    className="persona-column"
                                    style={{
                                      width: "33.333%",
                                      verticalAlign: "top",
                                      paddingBottom: "12px",
                                      paddingRight: columnIndex < 2 ? "8px" : "0",
                                      paddingLeft: columnIndex > 0 ? "8px" : "0",
                                    }}
                                  >
                                    <PersonaCardEmail
                                      name={persona.name}
                                      role={persona.role}
                                      stance={persona.stance}
                                      stance_label={persona.stance_label}
                                      stanceLabelPrefix={copy.stanceLabelPrefix}
                                      primary_argument={persona.primary_argument}
                                      change_condition={persona.change_condition}
                                      primaryArgumentLabel={copy.primaryArgumentLabel}
                                      changeConditionLabel={copy.changeConditionLabel}
                                    />
                                  </td>
                                ))}
                              </tr>
                            </tbody>
                          </table>
                        </td>
                      </tr>
                    ))}

                    <tr>
                      <td style={{ padding: "8px 24px 0 24px" }}>
                        <p
                          style={{
                            margin: 0,
                            color: emailTextSecondary,
                            fontSize: "12px",
                            lineHeight: "20px",
                          }}
                        >
                          {`${copy.sentToPrefix} ${user_email}`}
                        </p>
                      </td>
                    </tr>

                    <tr>
                      <td style={{ padding: "12px 24px 0 24px" }}>
                        <p
                          style={{
                            margin: 0,
                            color: emailTextSecondary,
                            fontSize: "12px",
                            lineHeight: "20px",
                          }}
                        >
                          {copy.footerNote}
                        </p>
                      </td>
                    </tr>

                    <tr>
                      <td style={{ padding: "8px 24px 24px 24px" }}>
                        <p
                          style={{
                            margin: 0,
                            color: emailTextSecondary,
                            fontSize: "11px",
                            lineHeight: "18px",
                          }}
                        >
                          {copy.interpretiveDisclaimer}
                        </p>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </td>
            </tr>
          </tbody>
        </table>
      </Body>
    </Html>
  );
}
