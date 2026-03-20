"use client";

import * as React from "react";

import { Textarea } from "@/components/ui/textarea";

type RotatingPlaceholderProps = React.ComponentProps<typeof Textarea> & {
  examples: string[];
  intervalMs?: number;
};

export function RotatingPlaceholder({
  examples,
  intervalMs = 4000,
  onFocus,
  onBlur,
  placeholder,
  ...props
}: RotatingPlaceholderProps) {
  const [currentIndex, setCurrentIndex] = React.useState(0);
  const [hasFocused, setHasFocused] = React.useState(false);
  const [prefersReducedMotion, setPrefersReducedMotion] = React.useState(false);
  const intervalRef = React.useRef<number | null>(null);

  React.useEffect(() => {
    if (typeof window === "undefined") return;

    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    const updatePreference = () => setPrefersReducedMotion(mediaQuery.matches);

    updatePreference();

    if ("addEventListener" in mediaQuery) {
      mediaQuery.addEventListener("change", updatePreference);
      return () => mediaQuery.removeEventListener("change", updatePreference);
    }
  }, []);

  React.useEffect(() => {
    if (intervalRef.current !== null) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    if (hasFocused || prefersReducedMotion || examples.length < 2) {
      return;
    }

    intervalRef.current = window.setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % examples.length);
    }, intervalMs);

    return () => {
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [examples, hasFocused, intervalMs, prefersReducedMotion]);

  const activePlaceholder =
    examples.length > 0 ? examples[currentIndex % examples.length] : placeholder;

  const handleFocus = (event: React.FocusEvent<HTMLTextAreaElement>) => {
    setHasFocused(true);

    if (intervalRef.current !== null) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    onFocus?.(event);
  };

  const handleBlur = (event: React.FocusEvent<HTMLTextAreaElement>) => {
    onBlur?.(event);
  };

  return (
    <Textarea
      {...props}
      placeholder={activePlaceholder}
      onFocus={handleFocus}
      onBlur={handleBlur}
    />
  );
}
