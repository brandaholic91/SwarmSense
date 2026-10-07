export const errorMessages = {
  RUN_START_FAILED: "Nem sikerült elindítani az elemzést. Kérjük, próbáld újra.",
  INVALID_INPUT: "Mindkét mezőt töltsd ki, mezőnként legfeljebb 500 karakterrel.",
  BUSY: "Most két elemzés fut egyszerre. Próbáld újra egy perc múlva.",
  IP_LIMIT_REACHED:
    "Erről a címről ma már három elemzés indult. Holnap újra próbálhatod; addig nézd meg a mintafutást.",
  DAILY_LIMIT_REACHED:
    "A demó mai kerete betelt. Holnap újra próbálhatod; addig nézd meg a mintafutást.",
  RUN_NOT_FOUND: "Nem találjuk ezt a futást.",
  TOO_FEW_PERSONAS: "Túl kevés persona válaszolt, ezért az elemzés nem készült el.",
  PERSONA_GENERATION_FAILED: "A personák generálása nem sikerült.",
  RUN_TIMED_OUT: "A futás megszakadt, mielőtt elkészült volna.",
  INTERNAL_ERROR: "Váratlan hiba történt a futás közben.",
} as const;

export type AppErrorCode = keyof typeof errorMessages;

export function getErrorMessageByCode(code: string): string {
  if (code in errorMessages) {
    return errorMessages[code as AppErrorCode];
  }
  return "Váratlan hiba történt. Kérjük, próbáld újra.";
}
