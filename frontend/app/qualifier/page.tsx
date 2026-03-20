"use client";

import * as React from "react";
import type { CSSProperties } from "react";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { messages } from "@/lib/messages";
import {
  accent,
  errorDim,
  onPrimary,
  onSurface,
  outlineVariant,
  surfaceContainer,
  surfaceContainerLow,
  textSecondary,
} from "@/lib/tokens";

type QualifierField = "role_answer" | "use_case_answer";

type QualifierPayload = {
  role_answer: string;
  use_case_answer: string;
};

const headlineFont: CSSProperties = { fontFamily: "var(--font-headline)" };
const labelFont: CSSProperties = { fontFamily: "var(--font-label)" };

function createQualifierPayload(
  roleAnswer: string,
  useCaseAnswer: string
): QualifierPayload {
  return {
    role_answer: roleAnswer,
    use_case_answer: useCaseAnswer,
  };
}

export default function QualifierPage() {
  const { qualifier } = messages;
  const [roleAnswer, setRoleAnswer] = React.useState("");
  const [useCaseAnswer, setUseCaseAnswer] = React.useState("");
  const [errors, setErrors] = React.useState<Partial<Record<QualifierField, string>>>({});

  const roleContainerRef = React.useRef<HTMLDivElement>(null);
  const useCaseContainerRef = React.useRef<HTMLDivElement>(null);

  const isComplete = roleAnswer.length > 0 && useCaseAnswer.length > 0;

  const validateField = React.useCallback(
    (field: QualifierField, value: string) => {
      const message =
        field === "role_answer"
          ? qualifier.form.errors.roleAnswer
          : qualifier.form.errors.useCaseAnswer;

      setErrors((prev) => ({
        ...prev,
        [field]: value ? undefined : message,
      }));
    },
    [qualifier.form.errors.roleAnswer, qualifier.form.errors.useCaseAnswer]
  );

  const handleContainerBlur = (
    field: QualifierField,
    value: string,
    containerRef: React.RefObject<HTMLDivElement | null>,
    event: React.FocusEvent<HTMLDivElement>
  ) => {
    const nextTarget = event.relatedTarget;
    if (nextTarget && containerRef.current?.contains(nextTarget)) {
      return;
    }

    validateField(field, value);
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!isComplete) {
      validateField("role_answer", roleAnswer);
      validateField("use_case_answer", useCaseAnswer);
      return;
    }

    const payload = createQualifierPayload(roleAnswer, useCaseAnswer);
    void payload;
  };

  return (
    <div className="relative min-h-screen" style={{ color: onSurface }}>
      <header
        className="sticky top-0 z-40 flex h-20 items-center justify-center border-b"
        style={{ backgroundColor: surfaceContainer, borderColor: outlineVariant }}
      >
        <span
          className="text-lg font-semibold tracking-tight"
          style={{ ...headlineFont, color: onSurface }}
        >
          Swarm<span style={{ color: accent }}>Sense</span>
        </span>
      </header>

      <main className="flex min-h-[calc(100vh-80px)] items-center justify-center px-6 py-20">
        <section className="w-full max-w-lg space-y-8">
          <h1
            className="text-3xl font-semibold md:text-4xl"
            style={{ ...headlineFont, color: onSurface }}
          >
            {qualifier.intro}
          </h1>

          <form className="space-y-8" onSubmit={handleSubmit}>
            <div className="space-y-3">
              <label
                htmlFor="role-answer"
                className="text-xs uppercase tracking-[0.2em]"
                style={{ color: textSecondary, ...labelFont }}
              >
                {qualifier.form.roleLabel}
              </label>
              <div
                ref={roleContainerRef}
                onBlur={(event) =>
                  handleContainerBlur("role_answer", roleAnswer, roleContainerRef, event)
                }
              >
                <Select
                  value={roleAnswer}
                  onValueChange={(value) => {
                    setRoleAnswer(value);
                    setErrors((prev) => ({ ...prev, role_answer: undefined }));
                  }}
                >
                  <SelectTrigger
                    id="role-answer"
                    aria-label={qualifier.form.roleLabel}
                    className="h-12 w-full"
                    style={{ backgroundColor: surfaceContainerLow, borderColor: outlineVariant }}
                  >
                    <SelectValue placeholder={qualifier.form.rolePlaceholder} />
                  </SelectTrigger>
                  <SelectContent>
                    {qualifier.form.roleOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              {errors.role_answer ? (
                <p className="text-xs font-semibold" style={{ color: errorDim }}>
                  {errors.role_answer}
                </p>
              ) : null}
            </div>

            <div className="space-y-3">
              <p
                id="use-case-label"
                className="text-xs uppercase tracking-[0.2em]"
                style={{ color: textSecondary, ...labelFont }}
              >
                {qualifier.form.useCaseLabel}
              </p>
              <div
                ref={useCaseContainerRef}
                onBlur={(event) =>
                  handleContainerBlur(
                    "use_case_answer",
                    useCaseAnswer,
                    useCaseContainerRef,
                    event
                  )
                }
              >
                <RadioGroup
                  aria-labelledby="use-case-label"
                  value={useCaseAnswer}
                  onValueChange={(value) => {
                    setUseCaseAnswer(value);
                    setErrors((prev) => ({ ...prev, use_case_answer: undefined }));
                  }}
                >
                  {qualifier.form.useCaseOptions.map((option) => (
                    <label
                      key={option.value}
                      htmlFor={option.value}
                      className="flex w-full min-h-12 cursor-pointer items-start gap-3 rounded-lg border px-4 py-3 focus-within:outline focus-within:outline-2 focus-within:outline-offset-2"
                      style={{
                        borderColor: outlineVariant,
                        backgroundColor: surfaceContainerLow,
                        outlineColor: accent,
                      }}
                    >
                      <RadioGroupItem
                        id={option.value}
                        value={option.value}
                        aria-label={option.label}
                        className="mt-1"
                      />
                      <span className="space-y-1">
                        <span className="block text-sm font-medium" style={{ color: onSurface }}>
                          {option.label}
                        </span>
                        <span className="block text-xs" style={{ color: textSecondary }}>
                          {option.description}
                        </span>
                      </span>
                    </label>
                  ))}
                </RadioGroup>
              </div>
              {errors.use_case_answer ? (
                <p className="text-xs font-semibold" style={{ color: errorDim }}>
                  {errors.use_case_answer}
                </p>
              ) : null}
            </div>

            <button
              type="submit"
              className="flex w-full items-center justify-center rounded-lg px-6 py-4 text-base font-semibold transition-transform active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60"
              style={{ backgroundColor: accent, color: onPrimary, ...headlineFont }}
              disabled={!isComplete}
              aria-disabled={!isComplete ? "true" : undefined}
            >
              {qualifier.form.submitCta}
            </button>
          </form>
        </section>
      </main>
    </div>
  );
}
