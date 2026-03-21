import { Body, Head, Html, Preview } from "@react-email/components";

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
  summary: string;
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

  return (
    <Html lang="hu">
      <Head />
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

                    <tr>
                      <td style={{ padding: "20px 24px 8px 24px" }}>
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
                        <table role="presentation" width="100%" cellPadding={0} cellSpacing={0}>
                          <tbody>
                            <tr>
                              <td
                                style={{
                                  width: "50%",
                                  paddingRight: "8px",
                                  verticalAlign: "top",
                                }}
                              >
                                <p
                                  style={{
                                    margin: 0,
                                    color: emailTextSecondary,
                                    fontSize: "12px",
                                    lineHeight: "18px",
                                  }}
                                >
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
                              <td
                                style={{
                                  width: "50%",
                                  paddingLeft: "8px",
                                  verticalAlign: "top",
                                }}
                              >
                                <p
                                  style={{
                                    margin: 0,
                                    color: emailTextSecondary,
                                    fontSize: "12px",
                                    lineHeight: "18px",
                                  }}
                                >
                                  {copy.aggregateScoreLabel}
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
                                  {aggregate_score}
                                </p>
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </td>
                    </tr>

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
                          {consensus_flag || copy.consensusPending}
                        </p>
                      </td>
                    </tr>

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

                    {(personas ?? []).map((persona, index) => (
                      <tr key={`${persona.name}-${index}`}>
                        <td style={{ padding: "0 24px 12px 24px" }}>
                          <PersonaCardEmail
                            name={persona.name}
                            role={persona.role}
                            stance={persona.stance}
                            stance_label={persona.stance_label}
                            stanceLabelPrefix={copy.stanceLabelPrefix}
                            summary={persona.summary}
                          />
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
                      <td style={{ padding: "12px 24px 24px 24px" }}>
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
