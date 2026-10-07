import { connection } from "next/server";

import { messages } from "@/lib/messages";

// The address comes from an environment variable that is read at request
// time, so one build can be deployed with different values.
export async function getContact(): Promise<{ line: string; hasAddress: boolean }> {
  await connection();
  const email = process.env.CONTACT_EMAIL?.trim();

  return email
    ? { line: `${messages.legal.contactLabel}: ${email}`, hasAddress: true }
    : { line: messages.legal.contactFallback, hasAddress: false };
}
