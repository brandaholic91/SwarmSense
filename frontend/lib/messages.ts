type PreviewCard = {
  name: string;
  role: string;
  stance: "reject" | "support" | "conditional";
  stanceLabel: string;
  summary: string;
};

export const messages = {
  landing: {
    hero: {
      headline: "Lásd meg egy perc alatt, mit gondolnak a vevőid",
      subheadline:
        "Szintetikus buyer personák, akik valós hangon jeleznek vissza a termékedről.",
      supporting:
        "Gyorsan látszik, kinek szól, ki kételkedik, és hol kell javítani a pozicionáláson.",
    },
    form: {
      researchLabel: "Kutatási téma",
      audienceLabel: "Célcsoport leírása",
      piiWarning: "Ne adj meg személyes adatokat a kutatási témában",
      cta: "Kutatás indítása",
      emailLabel: "Email-cím",
      emailPlaceholder: "nev@ceg.hu",
      errors: {
        researchTopic: "Add meg a kutatási témát.",
        audienceDescription: "Add meg a célcsoport leírását.",
      },
    },
    preview: {
      eyebrow: "Minta eredmény",
      title: "Első körös reakciók, egyetlen pillantásból",
      stat: "15 / 18 persona elutasítja",
      statSupporting: "A legerősebb ellenérv a pénzügyi kockázat.",
      objection:
        "Ez túl drága a csapatunknak, és nem látjuk a gyors ROI-t.",
      cardAriaTemplate: "{name} - {stanceLabel} - {role}",
      cards: ([
        {
          name: "Kovács Réka",
          role: "CFO, 280 fős SaaS",
          stance: "reject",
          stanceLabel: "Elutasítja",
          summary:
            "Túl nagy az előfizetési kockázat, és nincs elég bizonyíték a megtakarításra.",
        },
        {
          name: "Varga Dániel",
          role: "Termékvezető, fintech startup",
          stance: "support",
          stanceLabel: "Támogatja",
          summary:
            "Gyorsabb piaci validációt lát, és szerinte erős a differenciálás a versenytársakhoz képest.",
        },
        {
          name: "Tóth Eszter",
          role: "Marketing vezető, B2B szolgáltató",
          stance: "conditional",
          stanceLabel: "Feltételes",
          summary:
            "Érdekes, ha látja a pontos outputot és a bevezetés nem terheli a csapatát.",
        },
      ] satisfies PreviewCard[]),
    },
  },
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
