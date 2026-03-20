import {
  border,
  stanceConditional,
  stanceReject,
  stanceSupport,
  surface,
  textPrimary,
  textSecondary,
} from "@/lib/tokens";
import { cn } from "@/lib/utils";
import type { CSSProperties } from "react";

type PersonaStance = "reject" | "support" | "conditional";

const stanceColors: Record<PersonaStance, string> = {
  reject: stanceReject,
  support: stanceSupport,
  conditional: stanceConditional,
};

export type PersonaCardProps = {
  name: string;
  role: string;
  stance: PersonaStance;
  stanceLabel: string;
  summary: string;
  ariaLabel: string;
  variant?: "compact" | "default";
};

export function PersonaCard({
  name,
  role,
  stance,
  stanceLabel,
  summary,
  ariaLabel,
  variant = "default",
}: PersonaCardProps) {
  const isCompact = variant === "compact";
  const stanceColor = stanceColors[stance] ?? border;
  const summaryStyle: CSSProperties | undefined = isCompact
    ? {
        display: "-webkit-box",
        WebkitLineClamp: 3,
        WebkitBoxOrient: "vertical",
        overflow: "hidden",
      }
    : undefined;

  return (
    <article
      aria-label={ariaLabel}
      className={cn(
        "flex h-full flex-col gap-3 rounded-xl border border-l-4 p-4",
        isCompact ? "text-sm" : "p-6"
      )}
      style={{
        backgroundColor: surface,
        borderColor: border,
        borderLeftColor: stanceColor,
        color: textPrimary,
      }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-col gap-1">
          <p className="text-base font-semibold" style={{ color: textPrimary }}>
            {name}
          </p>
          <p className="text-xs uppercase tracking-[0.12em]" style={{ color: textSecondary }}>
            {role}
          </p>
        </div>
        <span
          className="text-xs font-semibold uppercase tracking-[0.12em]"
          style={{ color: stanceColor }}
        >
          {stanceLabel}
        </span>
      </div>
      <p className="text-sm leading-relaxed" style={{ color: textSecondary, ...summaryStyle }}>
        {summary}
      </p>
    </article>
  );
}
