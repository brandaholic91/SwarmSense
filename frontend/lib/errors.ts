export const errorMessages = {
  RUN_START_FAILED: "Nem sikerült elindítani az elemzést. Kérjük, próbáld újra.",
  INVALID_INPUT: "Mindkét mezőt töltsd ki, mezőnként legfeljebb 500 karakterrel.",
} as const;

export type AppErrorCode = keyof typeof errorMessages;

export function getErrorMessageByCode(code: string): string {
  if (code in errorMessages) {
    return errorMessages[code as AppErrorCode];
  }
  return "Váratlan hiba történt. Kérjük, próbáld újra.";
}
