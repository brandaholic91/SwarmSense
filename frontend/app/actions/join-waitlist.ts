"use server";

import { getErrorMessageByCode } from "@/lib/errors";
import { messages } from "@/lib/messages";

type JoinWaitlistInput = {
  email: string;
};

type JoinWaitlistSuccessResponse = {
  status: "joined" | "already_joined";
};

type JoinWaitlistErrorResponse = {
  detail?: string;
  code?: string;
};

type JoinWaitlistSuccess = {
  ok: true;
  status: "joined" | "already_joined";
};

type JoinWaitlistFailure = {
  ok: false;
  message: string;
};

export async function joinWaitlistAction({
  email,
}: JoinWaitlistInput): Promise<JoinWaitlistSuccess | JoinWaitlistFailure> {
  const apiUrl = process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL;
  if (!apiUrl) {
    throw new Error("API_URL is not configured");
  }

  try {
    const response = await fetch(`${apiUrl}/api/v1/waitlist`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify({ email }),
      cache: "no-store",
    });

    if (response.ok) {
      const data = (await response.json()) as JoinWaitlistSuccessResponse;
      return {
        ok: true,
        status: data.status,
      };
    }

    let errorData: JoinWaitlistErrorResponse | null = null;
    try {
      errorData = (await response.json()) as JoinWaitlistErrorResponse;
    } catch {
      return {
        ok: false,
        message: messages.genericError,
      };
    }

    if (errorData?.code) {
      return {
        ok: false,
        message: getErrorMessageByCode(errorData.code),
      };
    }

    return {
      ok: false,
      message: messages.genericError,
    };
  } catch {
    return {
      ok: false,
      message: messages.genericError,
    };
  }
}
