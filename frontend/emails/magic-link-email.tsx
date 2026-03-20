import { messages } from "@/lib/messages";
import {
  accent,
  border,
  surface,
  textPrimary,
  textSecondary,
  trueBlack,
} from "@/lib/tokens";

type MagicLinkEmailProps = {
  verifyUrl: string;
};

export function MagicLinkEmail({ verifyUrl }: MagicLinkEmailProps) {
  const copy = messages.email.magicLink;

  return (
    <html>
      <body
        style={{
          margin: 0,
          backgroundColor: trueBlack,
          color: textPrimary,
          fontFamily: "Arial, sans-serif",
        }}
      >
        <table
          width="100%"
          cellPadding={0}
          cellSpacing={0}
          style={{ padding: "24px" }}
        >
          <tbody>
            <tr>
              <td align="center">
                <table
                  width="100%"
                  cellPadding={0}
                  cellSpacing={0}
                  style={{
                    maxWidth: "560px",
                    border: `1px solid ${border}`,
                    borderRadius: "12px",
                    backgroundColor: surface,
                    padding: "32px",
                  }}
                >
                  <tbody>
                    <tr>
                      <td>
                        <h1 style={{ margin: 0, fontSize: "24px", lineHeight: "32px" }}>
                          {copy.heading}
                        </h1>
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <p
                          style={{
                            margin: "16px 0 0 0",
                            color: textSecondary,
                            fontSize: "16px",
                            lineHeight: "24px",
                          }}
                        >
                          {copy.intro}
                        </p>
                      </td>
                    </tr>
                    <tr>
                      <td style={{ paddingTop: "24px" }}>
                        <a
                          href={verifyUrl}
                          style={{
                            display: "inline-block",
                            backgroundColor: accent,
                            color: trueBlack,
                            borderRadius: "8px",
                            textDecoration: "none",
                            fontWeight: 700,
                            padding: "12px 18px",
                            fontSize: "14px",
                          }}
                        >
                          {copy.buttonLabel}
                        </a>
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <p
                          style={{
                            margin: "20px 0 0 0",
                            color: textSecondary,
                            fontSize: "13px",
                            lineHeight: "20px",
                          }}
                        >
                          {copy.expiry}
                        </p>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </td>
            </tr>
          </tbody>
        </table>
      </body>
    </html>
  );
}
