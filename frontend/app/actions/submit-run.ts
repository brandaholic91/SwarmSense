"use server";

import { redirect } from "next/navigation";

type SubmitRunInput = {
  email: string;
  hasConsent: boolean;
  consentTimestamp: string;
};

type CheckEmailResponse =
  | { status: "new" }
  | { status: "returning"; redirect_to: string };

type MagicLinkResponse = { status: "sent" };

export async function submitRunAction({
  email,
  hasConsent,
  consentTimestamp,
}: SubmitRunInput): Promise<void> {
  const apiUrl = process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL;
  if (!apiUrl) {
    throw new Error("API_URL is not configured");
  }

  const response = await fetch(`${apiUrl}/api/v1/auth/check-email`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify({
      email,
      has_consent: hasConsent,
      consent_timestamp: consentTimestamp,
    }),
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Email check failed: ${response.status}`);
  }

  const data = (await response.json()) as CheckEmailResponse;
  if (data.status === "returning") {
    redirect("/blocked");
  }

  const magicLinkResponse = await fetch(`${apiUrl}/api/v1/auth/magic-link`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify({
      email,
      has_consent: hasConsent,
      consent_timestamp: consentTimestamp,
    }),
    cache: "no-store",
  });

  if (!magicLinkResponse.ok) {
    throw new Error(`Magic link generation failed: ${magicLinkResponse.status}`);
  }

  const magicLinkData = (await magicLinkResponse.json()) as MagicLinkResponse;
  if (magicLinkData.status !== "sent") {
    throw new Error("Magic link generation failed");
  }
}
