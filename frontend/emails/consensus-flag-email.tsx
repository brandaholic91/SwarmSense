import { accent, emailTextPrimary } from "@/lib/tokens";

type ConsensusFlagEmailProps = {
  label: string;
  value: string;
};

export function ConsensusFlagEmail({ label, value }: ConsensusFlagEmailProps) {
  return (
    <table
      role="alert"
      width="100%"
      cellPadding={0}
      cellSpacing={0}
      style={{
        width: "100%",
        border: `2px solid ${accent}`,
      }}
    >
      <tbody>
        <tr>
          <td style={{ padding: "14px 16px" }}>
            <p
              style={{
                margin: 0,
                color: emailTextPrimary,
                fontSize: "12px",
                lineHeight: "18px",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
              }}
            >
              {label}
            </p>
            <p
              style={{
                margin: "6px 0 0 0",
                color: emailTextPrimary,
                fontSize: "18px",
                lineHeight: "25px",
                fontWeight: 700,
              }}
            >
              {value}
            </p>
          </td>
        </tr>
      </tbody>
    </table>
  );
}
