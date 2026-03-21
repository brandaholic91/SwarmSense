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
      headline: "Tudd meg, mit gondol a piacod,",
      highlight: "pár perc",
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
        "Ne adj meg személyes adatokat a kutatási témában",
      submitCta: "Elemzés indítása",
      helper: "Egy ingyenes elemzés email-címenként.",
      errors: {
        researchTopic: "Add meg a kutatási témát.",
        audienceDescription: "Add meg a célközönség leírását.",
        email: "Adj meg érvényes email-címet.",
      },
      email: {
        heading: "Hova küldjük az eredményt?",
        subheadline: "Az eredményed erre az emailre érkezik",
        successHeading: "Kiküldtük a kutatásindító linket",
        successBodyPrefix:
          "A kutatás indításához szükséges linket elküldtük erre az email-címre:",
        successHint:
          "Nyisd meg az emailed, kattints a linkre, és indulhat az elemzés.",
        label: "Email cím",
        placeholder: "pelda@email.hu",
        cta: "Eredmény küldése",
        privacyNote: "Adataid biztonságban vannak. Egy kattintással leiratkozhatsz.",
        consentPrefix: "Elfogadom az ",
        privacyPolicyLink: "Adatkezelési tájékoztatót",
        consentConnector: " és a ",
        termsOfServiceLink: "Felhasználási feltételeket",
      },
    },
  },
  qualifier: {
    intro: "Segíts kalibrálni a personákat",
    form: {
      roleLabel: "Mi jellemzi legjobban a szerepkörét?",
      rolePlaceholder: "Válassz szerepkört",
      roleOptions: [
        { value: "founder_ceo", label: "Alapító / CEO" },
        { value: "marketing_lead", label: "Marketing vezető" },
        { value: "product_manager", label: "Termékmenedzser" },
        { value: "sales_lead", label: "Sales vezető" },
        { value: "cfo_finance", label: "CFO / Pénzügy" },
      ],
      useCaseLabel:
        "Milyen célra szeretné leginkább használni a szintetikus kutatást?",
      useCaseOptions: [
        {
          value: "message_validation",
          label: "Üzenetek és pozicionálás validálása",
          description: "Kampányüzenetek és értékajánlat gyors tesztelése.",
        },
        {
          value: "pricing_decisions",
          label: "Árazási döntések előkészítése",
          description: "Árérzékenység és várható reakciók felmérése.",
        },
        {
          value: "feature_prioritization",
          label: "Termékfeature priorizálás",
          description: "Mely fejlesztések hoznak valódi üzleti értéket.",
        },
        {
          value: "launch_feedback",
          label: "Go-to-market és launch visszajelzés",
          description: "Piaci fogadtatás és kockázatok előzetes becslése.",
        },
      ],
      submitCta: "Elemzés indítása",
      errors: {
        roleAnswer: "Válaszd ki a szerepkörödet.",
        useCaseAnswer: "Válassz egy elsődleges felhasználási célt.",
      },
    },
  },
  waiting: {
    states: {
      queued: "Sorban...",
      generating: "Personák generálása...",
      /** Interpolate {current} and {total} before rendering. */
      running: "Futtatás: {current}/{total} persona",
      composing: "Eredmény összeállítása...",
      completed: "Eredmény elkészült",
      failed: "Hiba történt a feldolgozás közben.",
    },
    /** Interpolate {email} before rendering. */
    emailDeliveryNotice: "Az eredményed erre az emailre érkezik: {email}",
    delayedNotice:
      "A feldolgozás a szokásosnál tovább tart, még dolgozunk rajta.",
    retrySuggestion: "Próbáld újra egy új elemzés indításával.",
  },
  blockingScreen: {
    heading: "Ez az email-cím már igénybe vette az ingyenes próbát",
    body: "Ehhez az email-címhez már tartozik lezárt futás, ezért új ingyenes elemzést most nem tudunk indítani.",
    cta: "Iratkozz fel az értesítőre",
    submitted: "Köszönjük! Felírtunk az értesítőre. A Pro hozzáférés indulása előtt emailben szólunk.",
    invalidEmail:
      "A várólista-feliratkozáshoz érvényes email átadása szükséges. Menj vissza a kutatási űrlapra, majd próbáld újra.",
    emailPrefix: "Értesítést erre az emailre küldünk:",
  },
  verify: {
    title: "A link nem használható",
    descriptionPrefix: "A bejelentkezési linkkel probléma történt:",
    requestNewLinkCta: "Új link kérése",
    verifying: "Link ellenőrzése…",
  },
  email: {
    magicLink: {
      subject: "SwarmSense – Bejelentkezési link",
      heading: "Folytasd a SwarmSense elemzést",
      intro: "Kattints a lenti gombra az azonosításhoz.",
      buttonLabel: "Bejelentkezés magic linkkel",
      expiry: "Ez a link 24 órán belül lejár.",
    },
    result: {
      subject: "A SwarmSense elemzésed elkészült",
      preview: "A SwarmSense eredményed megérkezett",
      title: "Itt van a SwarmSense eredményed",
      intro:
        "A személyek lefutottak, az összefoglaló kész. Alább látod a fő jelzéseket és a részleteket.",
      topicLabel: "Kutatási téma",
      audienceLabel: "Célközönség",
      personaCountLabel: "Lefutott személyek",
      aggregateScoreLabel: "Aggregált támogatási arány",
      consensusIcon: "⚠",
      consensusLabel: "Konszenzus jelzés",
      consensusPending: "Nincs megadott konszenzus jelzés",
      personasTitle: "Persona visszajelzések",
      stanceLabelPrefix: "Álláspont",
      primaryArgumentLabel: "Elsődleges érv",
      changeConditionLabel: "Mi változtatná meg a véleményét",
      coreConcernLabel: "Mélyebb aggodalom",
      buyingTriggerLabel: "Vásárlási trigger",
      synthesisTitle: "Szintézis",
      synthesisSummaryLabel: "Összefoglalás",
      synthesisBarriersLabel: "Fő akadályok",
      synthesisWinningConditionsLabel: "Sikerhez szükséges",
      synthesisBestTargetLabel: "Legreceptívebb szegmens",
      synthesisRecommendationLabel: "Stratégiai ajánlás",
      sentToPrefix: "Erre a címre küldtük:",
      unsubscribeLabel: "Leiratkozás",
      reflectionQuestion: "Mit tennél másképp ennek alapján?",
      reflectionCtaLabel: "Feliratkozás a Pro várólistára",
      reflectionHelper:
        "Jelentkezz a várólistára, hogy első körben kapj értesítést a Pro tier nyitásáról.",
      reflectionCtaHref: "/blocked",
      footerNote: "Ez egy automatikus értesítő levél, válasz helyett indíts új elemzést.",
      interpretiveDisclaimer:
        "Fontos: az itt látható eredmények AI-alapú szintetikus szimulációból származnak, nem valós emberi kutatásból.",
    },
    followup: {
      day1: {
        preview: "1 nap telt el az eredményed óta",
        title: "Mit viszel tovább az első nap után?",
        body: "Nézd át újra a legerősebb ellenérvet, és használd hipotézisként a következő iterációdban.",
      },
      day3: {
        preview: "3 napos emlékeztető a SwarmSense eredményedről",
        title: "Három nap után új perspektíva",
        body: "Válassz ki egy support és egy reject álláspontot, majd formálj belőlük tesztelhető üzenetpárokat.",
      },
      day7: {
        preview: "7 napos follow-up: mi a következő lépés?",
        title: "Eltelt egy hét - ideje döntést hozni",
        body: "Ha még nem léptél, most priorizáld a következő kísérletet az eredmény alapján.",
      },
      ctaLabel: "Feliratkozás a Pro várólistára",
      ctaHref: "/blocked",
      unsubscribeLabel: "Leiratkozás",
      footerNote: "Ez egy automatikus marketing levél. Bármikor leiratkozhatsz.",
    },
  },
  legal: {
    privacyTitle: "Adatkezelési tájékoztató",
    termsTitle: "Felhasználási feltételek",
    privacyIntro:
      "A SwarmSense szolgáltatás használata során a személyes adatokat az érvényes adatvédelmi jogszabályoknak megfelelően kezeljük.",
    controllerTitle: "1. Adatkezelő",
    controllerBody:
      "Adatkezelő: SwarmSense üzemeltetője. Kapcsolat: support@swarmsense.ai",
    processedDataTitle: "2. Kezelt adatok köre",
    processedDataItems: [
      "e-mail cím",
      "kutatási téma és célközönség leírás",
      "qualifier válaszok",
      "futási metaadatok (státusz, időpontok)",
    ],
    legalBasisTitle: "3. Jogalap és adatkezelés célja",
    legalBasisBody:
      "Az adatkezelés jogalapja a felhasználó hozzájárulása és a szolgáltatás nyújtásához fűződő jogos érdek. A cél az eredmény küldése, a szolgáltatás minőségének fenntartása és a biztonságos üzemeltetés.",
    retentionTitle: "4. Megőrzési időtartamok",
    retentionBody:
      "Az adatokat addig kezeljük, amíg az a szolgáltatás teljesítéséhez, jogi kötelezettség teljesítéséhez vagy jogos igények érvényesítéséhez szükséges.",
    deletionTitle: "5. Törlési kérelem (GDPR 17. cikk)",
    deletionContactLabel: "Törlési kapcsolattartó e-mail",
    deletionContactEmail: "privacy@swarmsense.ai",
    deletionAckSlaLabel: "Automatikus visszaigazolás",
    deletionAckSlaValue: "15 percen belül",
    deletionCompletionSlaLabel: "Törlés teljesítése",
    deletionCompletionSlaValue: "7 naptári napon belül",
    deletionMvpScope:
      "MVP-ben a törlési kérelem kizárólag e-mailben nyújtható be, önkiszolgáló portál nem áll rendelkezésre.",
    userRightsTitle: "6. Érintetti jogok",
    userRightsBody:
      "Jogod van tájékoztatást kérni, helyesbítést kérni, törlést kérni, az adatkezelés korlátozását kérni, valamint panaszt tenni a felügyeleti hatóságnál.",
    updatesTitle: "7. Tájékoztató módosítása",
    updatesBody:
      "A tájékoztatót időről időre frissíthetjük. A változásokat ezen az oldalon tesszük közzé.",
    deletionEmailTemplates: {
      acknowledgementSubject: "SwarmSense adattörlési kérelem – visszaigazolás",
      acknowledgementBody:
        "Köszönjük, hogy jelezted adattörlési igényedet. A kérelmet rögzítettük, és legkésőbb 15 percen belül visszaigazoljuk. A törlést legkésőbb 7 naptári napon belül elvégezzük, majd külön megerősítő e-mailt küldünk.",
      completionSubject: "SwarmSense adattörlési kérelem – teljesítve",
      completionBody:
        "Ezúton megerősítjük, hogy a kapcsolódó személyes adataid törlését elvégeztük a kérelem beadásától számított 7 naptári napon belül.",
    },
  },
  piiWarning: "Ne adj meg személyes adatot vagy bizalmas információt.",
  genericError: "Váratlan hiba történt. Kérjük, próbáld újra.",
};
