export const messages = {
  emailCaptureNotice: "Az eredményed erre az emailre érkezik",
  qualifierIntro: "Segíts kalibrálni a personákat",
  waiting: {
    states: {
      queued: "Sorban áll",
      generating: "Personák generálása",
      /** Interpolate {current} and {total} before rendering. */
      running: "Futtatás: {current}/{total} persona",
      composing: "Eredmény összeállítása",
      completed: "Eredmény elkészült",
    },
    /** Interpolate {email} before rendering. */
    emailDeliveryNotice: "Az eredményed erre az emailre érkezik: {email}",
    delayedNotice:
      "A feldolgozás a szokásosnál tovább tart, még dolgozunk rajta.",
  },
  blockingHeadline: "Ez az emailcím már igénybe vette az ingyenes próbát",
  piiWarning: "Ne adj meg személyes adatot vagy bizalmas információt.",
  reflectionQuestion: "Mit tennél másképp ennek alapján?",
  genericError: "Váratlan hiba történt. Kérjük, próbáld újra.",
};
