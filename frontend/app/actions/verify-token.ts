"use server";

import { cookies } from "next/headers";

type VerifyTokenInput = {
  token: string;
};

type VerifySuccess = {
  ok: true;
  user_id: string;
};

type VerifyFailureCode = "TOKEN_EXPIRED" | "TOKEN_INVALID";

type VerifyFailure = {
  ok: false;
  code: VerifyFailureCode;
  detail: string;
};

type VerifyResponse = {
  user_id: string;
};

type VerifyErrorResponse = {
  detail: string;
  code: string;
};

export async function verifyTokenAction({
  token,
}: VerifyTokenInput): Promise<VerifySuccess | VerifyFailure> {
  if (!token.trim()) {
    return {
      ok: false,
      code: "TOKEN_INVALID",
      detail: "Magic link token invalid",
    };
  }

  const apiUrl = process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL;
  if (!apiUrl) {
    throw new Error("API_URL is not configured");
  }

  let response: Response;
  try {
    response = await fetch(`${apiUrl}/api/v1/auth/verify`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify({ token }),
      cache: "no-store",
    });
  } catch (err) {
    // P-4: Handle network errors (timeout, DNS failure, etc.)
    return {
      ok: false,
      code: "TOKEN_INVALID",
      detail: err instanceof Error ? err.message : "Network error",
    };
  }

  if (response.ok) {
    const data = (await response.json()) as VerifyResponse;
    const cookieDomain = process.env.COOKIE_DOMAIN;
    const cookieDomainOption = cookieDomain ? { domain: cookieDomain } : {};
    const cookieStore = await cookies();
    cookieStore.set("swarmsense_verified_user", data.user_id, {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: 60 * 60,
      ...cookieDomainOption,
    });
    return {
      ok: true,
      user_id: data.user_id,
    };
  }

  // P-5: Guard against non-JSON error bodies (5xx from proxy, etc.)
  let errorData: VerifyErrorResponse;
  try {
    errorData = (await response.json()) as VerifyErrorResponse;
  } catch {
    return {
      ok: false,
      code: "TOKEN_INVALID",
      detail: "Magic link token invalid",
    };
  }

  if (errorData.code === "TOKEN_EXPIRED") {
    return {
      ok: false,
      code: "TOKEN_EXPIRED",
      detail: errorData.detail,
    };
  }

  return {
    ok: false,
    code: "TOKEN_INVALID",
    detail: errorData.detail,
  };
}
