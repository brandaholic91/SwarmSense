import { Body, Head, Html, Preview } from "@react-email/components";

import { messages } from "@/lib/messages";
import {
  accent,
  emailBorder,
  emailCanvas,
  emailSurface,
  emailTextPrimary,
  emailTextSecondary,
} from "@/lib/tokens";

export interface FollowUpEmailProps {
  unsubscribe_url: string;
  topic?: string | null;
  audience?: string | null;
  support_count?: number | null;
  reject_count?: number | null;
  conditional_count?: number | null;
  synthesis_summary?: string | null;
  synthesis_main_barriers?: string[] | null;
  synthesis_winning_conditions?: string | null;
  synthesis_best_target_segment?: string | null;
  synthesis_strategic_recommendation?: string | null;
}

export function ResearchSummarySection({
  topic,
  audience,
  support_count,
  reject_count,
  conditional_count,
  synthesis_summary,
  synthesis_main_barriers,
  synthesis_winning_conditions,
  synthesis_best_target_segment,
  synthesis_strategic_recommendation,
}: Omit<FollowUpEmailProps, "unsubscribe_url">) {
  const hasSynthesisData =
    Boolean(synthesis_summary) ||
    Boolean(synthesis_main_barriers && synthesis_main_barriers.length > 0) ||
    Boolean(synthesis_winning_conditions) ||
    Boolean(synthesis_best_target_segment) ||
    Boolean(synthesis_strategic_recommendation);

  if (!topic || !hasSynthesisData) return null;

  const total = (support_count ?? 0) + (reject_count ?? 0) + (conditional_count ?? 0);

  return (
    <tr>
      <td style={{ padding: "20px 24px 0 24px", borderTop: `1px solid ${emailBorder}` }}>
        <p
          style={{
            margin: "0 0 12px 0",
            color: emailTextSecondary,
            fontSize: "11px",
            fontWeight: 700,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
          }}
        >
          A kutatásod eredménye
        </p>
        <p style={{ margin: 0, color: emailTextSecondary, fontSize: "12px", lineHeight: "18px" }}>Téma</p>
        <p style={{ margin: "4px 0 0 0", color: emailTextPrimary, fontSize: "15px", lineHeight: "22px", fontWeight: 600 }}>
          {topic}
        </p>
        {audience ? (
          <>
            <p style={{ margin: "10px 0 0 0", color: emailTextSecondary, fontSize: "12px", lineHeight: "18px" }}>
              Célközönség
            </p>
            <p style={{ margin: "4px 0 0 0", color: emailTextPrimary, fontSize: "14px", lineHeight: "22px" }}>{audience}</p>
          </>
        ) : null}
        {total > 0 ? (
          <>
            <p style={{ margin: "10px 0 0 0", color: emailTextSecondary, fontSize: "12px", lineHeight: "18px" }}>
              Eredmény
            </p>
            <p style={{ margin: "4px 0 0 0", color: emailTextPrimary, fontSize: "14px", lineHeight: "22px" }}>
              {support_count ?? 0} támogatta · {conditional_count ?? 0} feltételes · {reject_count ?? 0} elutasította
            </p>
          </>
        ) : null}
        {synthesis_summary ? (
          <>
            <p style={{ margin: "10px 0 0 0", color: emailTextSecondary, fontSize: "12px", lineHeight: "18px" }}>
              Összefoglalás
            </p>
            <p style={{ margin: "4px 0 0 0", color: emailTextPrimary, fontSize: "13px", lineHeight: "20px" }}>
              {synthesis_summary}
            </p>
          </>
        ) : null}
        {synthesis_main_barriers && synthesis_main_barriers.length > 0 ? (
          <>
            <p
              style={{
                margin: "10px 0 4px 0",
                color: emailTextSecondary,
                fontSize: "12px",
                lineHeight: "18px",
                fontWeight: 700,
              }}
            >
              Fő akadályok
            </p>
            {synthesis_main_barriers.map((barrier, idx) => (
              <p key={idx} style={{ margin: "2px 0 0 0", color: emailTextPrimary, fontSize: "13px", lineHeight: "20px" }}>
                {`• ${barrier}`}
              </p>
            ))}
          </>
        ) : null}
        {synthesis_winning_conditions ? (
          <>
            <p style={{ margin: "10px 0 0 0", color: emailTextSecondary, fontSize: "12px", lineHeight: "18px" }}>
              Sikerhez szükséges
            </p>
            <p style={{ margin: "4px 0 0 0", color: emailTextPrimary, fontSize: "13px", lineHeight: "20px" }}>
              {synthesis_winning_conditions}
            </p>
          </>
        ) : null}
        {synthesis_best_target_segment ? (
          <>
            <p style={{ margin: "10px 0 0 0", color: emailTextSecondary, fontSize: "12px", lineHeight: "18px" }}>
              Kire érdemes fókuszálni
            </p>
            <p style={{ margin: "4px 0 0 0", color: emailTextPrimary, fontSize: "13px", lineHeight: "20px" }}>
              {synthesis_best_target_segment}
            </p>
          </>
        ) : null}
        {synthesis_strategic_recommendation ? (
          <>
            <p style={{ margin: "10px 0 0 0", color: emailTextSecondary, fontSize: "12px", lineHeight: "18px" }}>
              Stratégiai ajánlás
            </p>
            <p style={{ margin: "4px 0 12px 0", color: emailTextPrimary, fontSize: "13px", lineHeight: "20px" }}>
              {synthesis_strategic_recommendation}
            </p>
          </>
        ) : null}
      </td>
    </tr>
  );
}

export function FollowUpDay1Email({
  unsubscribe_url,
  topic,
  audience,
  support_count,
  reject_count,
  conditional_count,
  synthesis_summary,
  synthesis_main_barriers,
  synthesis_winning_conditions,
  synthesis_best_target_segment,
  synthesis_strategic_recommendation,
}: FollowUpEmailProps) {
  const copy = messages.email.followup;

  return (
    <Html lang="hu">
      <Head />
      <Preview>{copy.day1.preview}</Preview>
      <Body
        style={{
          margin: 0,
          padding: 0,
          backgroundColor: emailCanvas,
          color: emailTextPrimary,
          fontFamily: "Arial, sans-serif",
        }}
      >
        <table role="presentation" width="100%" cellPadding={0} cellSpacing={0} style={{ width: "100%", padding: "24px 12px" }}>
          <tbody>
            <tr>
              <td align="center">
                <table
                  role="presentation"
                  width="100%"
                  cellPadding={0}
                  cellSpacing={0}
                  style={{ maxWidth: "640px", border: `1px solid ${emailBorder}`, backgroundColor: emailSurface }}
                >
                  <tbody>
                    <tr>
                      <td style={{ padding: "24px 24px", borderBottom: `1px solid ${emailBorder}` }}>
                        <span style={{ fontSize: "18px", fontWeight: 700, color: emailTextPrimary }}>
                          Swarm<span style={{ color: accent }}>Sense</span>
                        </span>
                      </td>
                    </tr>
                    <tr>
                      <td style={{ padding: "28px 24px 20px 24px" }}>
                        <h1 style={{ margin: 0, fontSize: "28px", lineHeight: "34px" }}>{copy.day1.title}</h1>
                        <p style={{ margin: "12px 0 0 0", color: emailTextSecondary }}>{copy.day1.body}</p>
                      </td>
                    </tr>
                    <ResearchSummarySection
                      topic={topic}
                      audience={audience}
                      support_count={support_count}
                      reject_count={reject_count}
                      conditional_count={conditional_count}
                      synthesis_summary={synthesis_summary}
                      synthesis_main_barriers={synthesis_main_barriers}
                      synthesis_winning_conditions={synthesis_winning_conditions}
                      synthesis_best_target_segment={synthesis_best_target_segment}
                      synthesis_strategic_recommendation={synthesis_strategic_recommendation}
                    />
                    <tr>
                      <td style={{ padding: "20px 24px 0 24px" }}>
                        <a
                          href={copy.ctaHref}
                          style={{
                            display: "inline-block",
                            backgroundColor: accent,
                            color: "#ffffff",
                            textDecoration: "none",
                            fontWeight: 700,
                            padding: "10px 16px",
                          }}
                        >
                          {copy.ctaLabel}
                        </a>
                      </td>
                    </tr>
                    <tr>
                      <td style={{ padding: "18px 24px 6px 24px", color: emailTextSecondary, fontSize: "12px" }}>
                        {copy.footerNote}
                      </td>
                    </tr>
                    <tr>
                      <td style={{ padding: "0 24px 24px 24px" }}>
                        <a href={unsubscribe_url} style={{ color: accent, fontSize: "12px", textDecoration: "underline" }}>
                          {copy.unsubscribeLabel}
                        </a>
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
