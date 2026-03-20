type PreviewCard = {
  name: string;
  role: string;
  stance: "reject" | "support" | "conditional";
  stanceLabel: string;
  summary: string;
};

export const messages = {
  landing: {
    nav: {
      cta: "Ingyen kipróbálom",
    },
    hero: {
      headline: "Tudd meg, mit gondol a piacod —",
      highlight: "90 másodperc",
      headlineSuffix: "alatt.",
      subheadline:
        "15–20 attitudinálisan különböző AI persona elemzi a hipotézised. Nem egy ChatGPT válasz — strukturált piackutatás, toborzás és várakozás nélkül.",
      cta: "Ingyen kipróbálom",
    },
    preview: {
      eyebrow: "Így néz ki egy eredmény",
      heading: "Valós idejű szimulációs output",
      researchLabel: "Kutatási téma",
      researchValue: "Érdemes-e 15%-os áremelést végrehajtani a prémium szegmensben?",
      audienceLabel: "Célközönség",
      audienceValue: "KKV marketing döntéshozók",
      consensusLabel: "⚠ 9/18 elutasítja — megosztott eredmény",
      supportLabel: "Támogatja (50%)",
      rejectLabel: "Ellenzi (50%)",
      supportPercent: 50,
      rejectPercent: 50,
      cardAriaTemplate: "{name} - {stanceLabel} - {role}",
      cards: ([
        {
          name: "Kovács Péter",
          role: "CFO, 280 fős SaaS",
          stance: "reject",
          stanceLabel: "Elutasítja",
          summary:
            "Ebben a gazdasági környezetben a 15% már az a lélektani határ, ami miatt elkezdenénk alternatívákat keresni.",
        },
        {
          name: "Nagy Eszter",
          role: "Marketing vezető, B2B szolgáltató",
          stance: "conditional",
          stanceLabel: "Feltételes",
          summary:
            "Csak akkor fogadható el, ha a szolgáltatás minősége vagy az ügyfélszolgálat elérhetősége is arányosan javul.",
        },
        {
          name: "Horváth Gábor",
          role: "Termékvezető, prémium szegmens",
          stance: "support",
          stanceLabel: "Támogatja",
          summary:
            "A prémium szegmensben az ár minőségi jelzés is, így a pozicionálást erősíti.",
        },
      ] satisfies PreviewCard[]),
    },
    howItWorks: {
      heading: "Három lépés, 90 másodperc",
      steps: [
        {
          title: "Beküldöd",
          description:
            "Add meg a kérdésed és határozd meg a célközönséged paramétereit.",
        },
        {
          title: "A swarm fut",
          description:
            "15-20 egyedi AI persona szimulálja a döntéshozatali folyamatot valós időben.",
        },
        {
          title: "Email érkezik",
          description:
            "Az eredményeket és a részletes elemzést azonnal megkapod a fiókodba.",
        },
      ],
    },
    stats: {
      items: [
        { value: "~$0.002", label: "/ futtatás" },
        { value: "90 másodperc", label: "átlagos várakozás" },
        { value: "Nincs regisztráció", label: "azonnali hozzáférés" },
        { value: "15–20 persona", label: "diverz nézőpont" },
      ],
    },
    closingCta: {
      heading: "Teszteld le a következő kampányüzeneted még ma.",
      cta: "Ingyen kipróbálom",
      helper: "Egy ingyenes futtatás. Nincs hitelkártya.",
    },
    footer: {
      brand: "SwarmSense",
      privacy: "Privacy Policy",
    },
  },
  research: {
    form: {
      eyebrow: "Új kutatás",
      headline: "Mi a hipotézised?",
      subheadline:
        "Írd le a kutatási kérdést és a célcsoportot. 90 másodperc múlva a postaládádban van az eredmény.",
      researchLabel: "Mit vizsgálsz?",
      audienceLabel: "Kinek szól?",
      researchExamples: [
        "Érdemes-e 15%-os áremelést végrehajtani a prémium szegmensben?",
        "Milyen érvek győzik meg a középvállalati IT vezetőt egy új eszközről?",
        "Hogyan dönt egy marketing vezető egy új automatizációs platformról?",
      ],
      audienceExamples: [
        "KKV marketing döntéshozók, 30–50 év, növekedési fókuszban",
        "B2B szolgáltató cégek marketing vezetői 100-300 fős szervezetből",
        "SaaS CFO-k, akik költségcsökkentési célokat kaptak 2026-ra",
      ],
      piiWarning:
        "Kérjük, fogalmazz pontosan a releváns adathalmazok eléréséhez.",
      submitCta: "Elemzés indítása",
      helper: "Egy ingyenes elemzés email-címenként.",
      errors: {
        researchTopic: "Add meg a kutatási témát.",
        audienceDescription: "Add meg a célközönség leírását.",
      },
      email: {
        heading: "Hova küldjük az eredményt?",
        subheadline:
          "Az elemzés erre az email-címre érkezik. Nem hírlevél — csak az eredményed.",
        label: "Email-cím",
        placeholder: "pelda@email.hu",
        cta: "Eredmény küldése",
        privacyNote: "Adataid biztonságban vannak. Egy kattintással leiratkozhatsz.",
      },
    },
  },
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
