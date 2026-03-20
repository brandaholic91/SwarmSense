"use server";

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

  const response = await fetch(`${apiUrl}/api/v1/auth/verify`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify({ token }),
    cache: "no-store",
  });

  if (response.ok) {
    const data = (await response.json()) as VerifyResponse;
    return {
      ok: true,
      user_id: data.user_id,
    };
  }

  const errorData = (await response.json()) as VerifyErrorResponse;
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
