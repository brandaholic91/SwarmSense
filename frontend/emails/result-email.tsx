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
  core_concern: string;
  buying_trigger: string;
  risk_appetite: string;
  decision_style: string;
  price_sensitivity: string;
  technology_adoption_curve: string;
};

export type ResultEmailSynthesis = {
  summary: string;
  main_barriers: string[];
  winning_conditions: string;
  best_target_segment: string;
  strategic_recommendation: string;
};

export type ResultEmailProps = {
  topic: string;
  audience: string;
  personas: ResultEmailPersona[];
  persona_count: string;
  aggregate_score: string;
  consensus_flag?: string;
  synthesis?: ResultEmailSynthesis;
  user_email: string;
  unsubscribe_url?: string;
  waitlist_url?: string;
};

export function ResultEmail({
  topic,
  audience,
  personas,
  persona_count,
  aggregate_score,
  consensus_flag,
  synthesis,
  user_email,
  unsubscribe_url,
  waitlist_url,
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
                      <td
                        style={{
                          padding: "24px 24px",
                          borderBottom: `1px solid ${emailBorder}`,
                        }}
                      >
                        <span
                          style={{
                            fontSize: "18px",
                            fontWeight: 700,
                            color: emailTextPrimary,
                          }}
                        >
                          Swarm<span style={{ color: accent }}>Sense</span>
                        </span>
                      </td>
                    </tr>
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
                            label={`${copy.consensusIcon} ${copy.consensusLabel}`}
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

                    {synthesis ? (
                      <tr>
                        <td style={{ padding: "20px 24px 0 24px" }}>
                          <h2
                            style={{
                              margin: 0,
                              color: emailTextPrimary,
                              fontSize: "18px",
                              lineHeight: "24px",
                              fontWeight: 700,
                            }}
                          >
                            {copy.synthesisTitle}
                          </h2>
                          <p
                            style={{
                              margin: "10px 0 0 0",
                              color: emailTextSecondary,
                              fontSize: "14px",
                              lineHeight: "22px",
                            }}
                          >
                            {synthesis.summary}
                          </p>
                          <p
                            style={{
                              margin: "14px 0 4px 0",
                              color: emailTextSecondary,
                              fontSize: "13px",
                              lineHeight: "20px",
                              fontWeight: 700,
                            }}
                          >
                            {copy.synthesisBarriersLabel}
                          </p>
                          {synthesis.main_barriers.map((barrier, idx) => (
                            <p
                              key={idx}
                              style={{
                                margin: "2px 0 0 0",
                                color: emailTextSecondary,
                                fontSize: "13px",
                                lineHeight: "20px",
                              }}
                            >
                              {`• ${barrier}`}
                            </p>
                          ))}
                          <p
                            style={{
                              margin: "12px 0 4px 0",
                              color: emailTextSecondary,
                              fontSize: "13px",
                              lineHeight: "20px",
                              fontWeight: 700,
                            }}
                          >
                            {copy.synthesisWinningConditionsLabel}
                          </p>
                          <p
                            style={{
                              margin: "2px 0 0 0",
                              color: emailTextSecondary,
                              fontSize: "13px",
                              lineHeight: "20px",
                            }}
                          >
                            {synthesis.winning_conditions}
                          </p>
                          <p
                            style={{
                              margin: "12px 0 4px 0",
                              color: emailTextSecondary,
                              fontSize: "13px",
                              lineHeight: "20px",
                              fontWeight: 700,
                            }}
                          >
                            {copy.synthesisBestTargetLabel}
                          </p>
                          <p
                            style={{
                              margin: "2px 0 0 0",
                              color: emailTextSecondary,
                              fontSize: "13px",
                              lineHeight: "20px",
                            }}
                          >
                            {synthesis.best_target_segment}
                          </p>
                          <p
                            style={{
                              margin: "12px 0 4px 0",
                              color: emailTextSecondary,
                              fontSize: "13px",
                              lineHeight: "20px",
                              fontWeight: 700,
                            }}
                          >
                            {copy.synthesisRecommendationLabel}
                          </p>
                          <p
                            style={{
                              margin: "2px 0 0 0",
                              color: emailTextSecondary,
                              fontSize: "13px",
                              lineHeight: "20px",
                            }}
                          >
                            {synthesis.strategic_recommendation}
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

                    {personas.map((persona) => (
                      <tr key={persona.name}>
                        <td style={{ padding: "0 24px 8px 24px" }}>
                          <PersonaCardEmail
                            name={persona.name}
                            role={persona.role}
                            stance={persona.stance}
                            stance_label={persona.stance_label}
                            stanceLabelPrefix={copy.stanceLabelPrefix}
                            primary_argument={persona.primary_argument}
                            change_condition={persona.change_condition}
                            core_concern={persona.core_concern}
                            buying_trigger={persona.buying_trigger}
                            risk_appetite={persona.risk_appetite}
                            decision_style={persona.decision_style}
                            price_sensitivity={persona.price_sensitivity}
                            technology_adoption_curve={persona.technology_adoption_curve}
                            primaryArgumentLabel={copy.primaryArgumentLabel}
                            changeConditionLabel={copy.changeConditionLabel}
                            coreConcernLabel={copy.coreConcernLabel}
                            buyingTriggerLabel={copy.buyingTriggerLabel}
                          />
                        </td>
                      </tr>
                    ))}

                    <tr>
                      <td style={{ padding: "20px 24px 0 24px" }}>
                        <p
                          style={{
                            margin: 0,
                            color: emailTextPrimary,
                            fontSize: "16px",
                            lineHeight: "24px",
                            fontWeight: 700,
                          }}
                        >
                          {copy.reflectionQuestion}
                        </p>
                        {copy.reflectionHelper ? (
                          <p
                            style={{
                              margin: "8px 0 0 0",
                              color: emailTextSecondary,
                              fontSize: "13px",
                              lineHeight: "20px",
                            }}
                          >
                            {copy.reflectionHelper}
                          </p>
                        ) : null}
                        <p style={{ margin: "12px 0 0 0" }}>
                          <a
                            href={waitlist_url ?? `${copy.reflectionCtaHref}?email=${encodeURIComponent(user_email)}`}
                            style={{
                              display: "inline-block",
                              backgroundColor: accent,
                              color: "#ffffff",
                              textDecoration: "none",
                              fontSize: "14px",
                              lineHeight: "20px",
                              fontWeight: 700,
                              padding: "10px 16px",
                            }}
                          >
                            {copy.reflectionCtaLabel}
                          </a>
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

                    {unsubscribe_url ? (
                      <tr>
                        <td style={{ padding: "8px 24px 0 24px" }}>
                          <a
                            href={unsubscribe_url}
                            style={{
                              color: accent,
                              fontSize: "12px",
                              lineHeight: "18px",
                              textDecoration: "underline",
                            }}
                          >
                            {copy.unsubscribeLabel}
                          </a>
                        </td>
                      </tr>
                    ) : null}

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
