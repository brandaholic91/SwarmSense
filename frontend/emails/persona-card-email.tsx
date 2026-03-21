import {
  emailBorder,
  emailSurface,
  emailTextPrimary,
  emailTextSecondary,
  stanceConditional,
  stanceReject,
  stanceSupport,
} from "@/lib/tokens";

export type PersonaStance = "reject" | "support" | "conditional";

const stanceColors: Record<PersonaStance, string> = {
  reject: stanceReject,
  support: stanceSupport,
  conditional: stanceConditional,
};

export type PersonaCardEmailProps = {
  name: string;
  role: string;
  stance: PersonaStance;
  stance_label: string;
  stanceLabelPrefix: string;
  primary_argument: string;
  change_condition: string;
  core_concern: string;
  buying_trigger: string;
  risk_appetite: string;
  decision_style: string;
  price_sensitivity: string;
  technology_adoption_curve: string;
  primaryArgumentLabel: string;
  changeConditionLabel: string;
  coreConcernLabel: string;
  buyingTriggerLabel: string;
};

export function PersonaCardEmail({
  name,
  role,
  stance,
  stance_label,
  stanceLabelPrefix,
  primary_argument,
  change_condition,
  core_concern,
  buying_trigger,
  risk_appetite,
  decision_style,
  price_sensitivity,
  technology_adoption_curve,
  primaryArgumentLabel,
  changeConditionLabel,
  coreConcernLabel,
  buyingTriggerLabel,
}: PersonaCardEmailProps) {
  const stanceColor = stanceColors[stance] ?? emailBorder;

  return (
    <table
      role="presentation"
      width="100%"
      cellPadding={0}
      cellSpacing={0}
      style={{
        border: `1px solid ${emailBorder}`,
        borderLeft: `4px solid ${stanceColor}`,
        backgroundColor: emailSurface,
      }}
    >
      <tbody>
        <tr>
          <td style={{ padding: "16px" }}>
            <p
              style={{
                margin: 0,
                color: emailTextPrimary,
                fontSize: "16px",
                lineHeight: "22px",
                fontWeight: 700,
              }}
            >
              {name}
            </p>
            <p
              style={{
                margin: "4px 0 0 0",
                color: emailTextSecondary,
                fontSize: "12px",
                lineHeight: "18px",
                textTransform: "uppercase",
                letterSpacing: "0.08em",
              }}
            >
              {role}
            </p>
            <p
              style={{
                margin: "8px 0 0 0",
                color: emailTextSecondary,
                fontSize: "11px",
                lineHeight: "16px",
              }}
            >
              {[risk_appetite, decision_style, price_sensitivity, technology_adoption_curve]
                .filter(Boolean)
                .join(" · ")}
            </p>
            <p
              style={{
                margin: "8px 0 0 0",
                color: stanceColor,
                fontSize: "12px",
                lineHeight: "18px",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
              }}
            >
              {`${stanceLabelPrefix}: ${stance_label}`}
            </p>
            <p
              style={{
                margin: "10px 0 0 0",
                color: emailTextSecondary,
                fontSize: "14px",
                lineHeight: "21px",
                fontWeight: 700,
              }}
            >
              {primaryArgumentLabel}
            </p>
            <p
              style={{
                margin: "4px 0 0 0",
                color: emailTextSecondary,
                fontSize: "14px",
                lineHeight: "21px",
              }}
            >
              {primary_argument}
            </p>
            <p
              style={{
                margin: "10px 0 0 0",
                color: emailTextSecondary,
                fontSize: "14px",
                lineHeight: "21px",
                fontWeight: 700,
              }}
            >
              {changeConditionLabel}
            </p>
            <p
              style={{
                margin: "4px 0 0 0",
                color: emailTextSecondary,
                fontSize: "14px",
                lineHeight: "21px",
              }}
            >
              {change_condition}
            </p>
            <p
              style={{
                margin: "10px 0 0 0",
                color: emailTextSecondary,
                fontSize: "14px",
                lineHeight: "21px",
                fontWeight: 700,
              }}
            >
              {coreConcernLabel}
            </p>
            <p
              style={{
                margin: "4px 0 0 0",
                color: emailTextSecondary,
                fontSize: "14px",
                lineHeight: "21px",
              }}
            >
              {core_concern}
            </p>
            <p
              style={{
                margin: "10px 0 0 0",
                color: emailTextSecondary,
                fontSize: "14px",
                lineHeight: "21px",
                fontWeight: 700,
              }}
            >
              {buyingTriggerLabel}
            </p>
            <p
              style={{
                margin: "4px 0 0 0",
                color: emailTextSecondary,
                fontSize: "14px",
                lineHeight: "21px",
              }}
            >
              {buying_trigger}
            </p>
          </td>
        </tr>
      </tbody>
    </table>
  );
}
