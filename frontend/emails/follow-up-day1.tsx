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
}

export function FollowUpDay1Email({ unsubscribe_url }: FollowUpEmailProps) {
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
                      <td style={{ padding: "28px 24px 12px 24px" }}>
                        <h1 style={{ margin: 0, fontSize: "28px", lineHeight: "34px" }}>{copy.day1.title}</h1>
                        <p style={{ margin: "12px 0 0 0", color: emailTextSecondary }}>{copy.day1.body}</p>
                      </td>
                    </tr>
                    <tr>
                      <td style={{ padding: "0 24px" }}>
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
