"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

type SubmitRunInput = {
  email: string;
  hasConsent: boolean;
  consentTimestamp: string;
  topic: string;
  audience: string;
};

type CheckEmailResponse =
  | { status: "new" }
  | { status: "returning"; redirect_to: string };

type MagicLinkResponse = { status: "sent" };

export async function submitRunAction({
  email,
  hasConsent,
  consentTimestamp,
  topic,
  audience,
}: SubmitRunInput): Promise<void> {
  const normalizedEmail = email.trim().toLowerCase();
  const normalizedTopic = topic.trim();
  const normalizedAudience = audience.trim();

  if (!normalizedTopic || !normalizedAudience) {
    throw new Error("Run context is missing");
  }

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
      email: normalizedEmail,
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
    redirect(`/blocked?email=${encodeURIComponent(normalizedEmail)}`);
  }

  const cookieStore = await cookies();
  cookieStore.set("swarmsense_result_email", normalizedEmail, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60,
  });

  cookieStore.set(
    "swarmsense_run_context",
    JSON.stringify({
      topic: normalizedTopic,
      audience: normalizedAudience,
    }),
    {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: 60 * 60,
    }
  );

  const magicLinkResponse = await fetch(`${apiUrl}/api/v1/auth/magic-link`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify({
      email: normalizedEmail,
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
