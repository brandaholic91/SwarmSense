export const errorMessages = {
  COST_LIMIT_REACHED: "A havi ingyenes kapacitás elérte a határát.",
  TOKEN_EXPIRED: "A bejelentkezési link lejárt. Kérj újat.",
  TOKEN_INVALID: "A bejelentkezési link érvénytelen. Kérj újat.",
  NO_TOKEN: "Nem érkezett bejelentkezési link. Kérj újat.",
  WAITLIST_SIGNUP_FAILED: "Most nem sikerült feliratkozni az értesítőre. Kérjük, próbáld újra.",
} as const;

export type AppErrorCode = keyof typeof errorMessages;

export function getErrorMessageByCode(code: string): string {
  if (code in errorMessages) {
    return errorMessages[code as AppErrorCode];
  }
  return "Váratlan hiba történt. Kérjük, próbáld újra.";
}
