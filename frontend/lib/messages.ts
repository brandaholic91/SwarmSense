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
        "Töltsd fel a kérdésed, és perceken belül látod, hogyan reagál rá a célközönséged — ügynökség és várakozás nélkül.",
      cta: "Ingyen kipróbálom",
    },
    painBridge: {
      heading: "A piackutatás még sosem volt ilyen egyszerű",
      closing:
        "A SwarmSense szintetikus piackutatással ad választ — AI personák döntéshozatala alapján.",
      items: [
        { before: "Hetek, hónapok", after: "Pár perc" },
        { before: "Ügynökségi büdzsé", after: "Megfizethető ár" },
        { before: "Csak nagyvállalatoknak", after: "Bárki számára" },
      ],
    },
    preview: {
      eyebrow: "Így néz ki egy eredmény",
      heading: "Konkrét reakciók, nem általános vélemények",
      researchLabel: "Kutatási téma",
      researchValue: "Meggyőző-e ez az üzenet B2B döntéshozóknak: Csökkentsd a sales ciklust 40%-kal automatizálással?",
      audienceLabel: "Célközönség",
      audienceValue: "Közép- és kisvállalati sales és marketing vezetők",
      consensusLabel: "✓ 11/18 támogatja — gyenge konszenzus",
      supportLabel: "Támogatja (61%)",
      rejectLabel: "Ellenzi (39%)",
      supportPercent: 61,
      rejectPercent: 39,
      cardAriaTemplate: "{name} - {stanceLabel} - {role}",
      cards: ([
        {
          name: "Tóth Andrea",
          role: "Sales vezető, 45 fős IT cég",
          stance: "support",
          stanceLabel: "Támogatja",
          summary:
            "A 40% konkrét szám, és az ügyfeleim pont ezt a fájdalmat érzik. Ez bejön.",
        },
        {
          name: "Fekete Márton",
          role: "CEO, B2B SaaS startup",
          stance: "conditional",
          stanceLabel: "Feltételes",
          summary:
            "Csak akkor hiteles, ha van mögötte valódi referencia-adat. Így üres claim.",
        },
        {
          name: "Varga Katalin",
          role: "Marketing vezető, szolgáltató cég",
          stance: "reject",
          stanceLabel: "Elutasítja",
          summary:
            "Túl generikus — minden automatizáló eszköz ugyanezt mondja. Nem differenciál.",
        },
      ] satisfies PreviewCard[]),
    },
    howItWorks: {
      heading: "Eredmény három lépésben",
      steps: [
        {
          title: "Beküldöd",
          description:
            "Add meg a kérdésed és határozd meg a célközönséged.",
        },
        {
          title: "A kutatás fut",
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
        { value: "Ingyenes próba", label: "regisztráció nélkül" },
        { value: "90 másodperc", label: "átlagos várakozás" },
        { value: "Strukturált elemzés", label: "emailben, azonnal" },
        { value: "15–20 persona", label: "diverz nézőpont" },
      ],
    },
    closingCta: {
      heading: "Teszteld le a következő feltételezésed még ma.",
      cta: "Ingyen kipróbálom",
      helper: "Egy ingyenes futtatás. Nincs hitelkártya.",
    },
    footer: {
      privacy: "Adatkezelési tájékoztató",
      terms: "Felhasználási feltételek",
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
      submitCta: "Tovább",
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
        cta: "Küldés",
        privacyNote: "Adataid biztonságban vannak.",
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
      companySizeLabel: "Hány főt foglalkoztat a céged?",
      companySizePlaceholder: "Válassz cégeméretet",
      companySizeOptions: [
        { value: "1_10", label: "1–10 fő" },
        { value: "11_50", label: "11–50 fő" },
        { value: "51_200", label: "51–200 fő" },
        { value: "200_plus", label: "200+ fő" },
      ],
      marketingProblemLabel: "Mi jelenleg a legnagyobb marketing problémád?",
      marketingProblemPlaceholder: "Pl. nem tudjuk elérni a döntéshozókat, drága az ügyfélszerzés...",
      roleOptions: [
        { value: "founder_ceo", label: "Alapító / CEO" },
        { value: "owner_md", label: "Tulajdonos / Ügyvezető" },
        { value: "marketing_lead", label: "Marketing vezető" },
        { value: "product_manager", label: "Termékmenedzser" },
        { value: "sales_lead", label: "Sales vezető" },
        { value: "cfo_finance", label: "CFO / Pénzügy" },
        { value: "consultant_agency", label: "Tanácsadó / Ügynökség" },
        { value: "other", label: "Egyéb" },
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
        {
          value: "sales_enablement",
          label: "Értékesítési érvek tesztelése",
          description: "Sales pitchek és kifogáskezelés előzetes validálása.",
        },
        {
          value: "investor_pitch",
          label: "Befektetői / pitch deck validálás",
          description: "Narratíva és értékajánlat tesztelése befektetői szemmel.",
        },
        {
          value: "competitor_positioning",
          label: "Versenytárs pozicionálás megértése",
          description: "Hogyan látja a célközönség a piaci alternatívákat.",
        },
        {
          value: "churn_retention",
          label: "Churn okok és megtartás",
          description: "Miért maradnak vagy miért mennek el az ügyfelek.",
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
      synthesisTitle: "Összefoglalás",
      synthesisSummaryLabel: "Összefoglalás",
      synthesisBarriersLabel: "Fő akadályok",
      synthesisWinningConditionsLabel: "Sikerhez szükséges",
      synthesisBestTargetLabel: "Kire érdemes fókuszálni",
      synthesisRecommendationLabel: "Stratégiai ajánlás",
      sentToPrefix: "Erre a címre küldtük:",
      unsubscribeLabel: "Leiratkozás",
      reflectionQuestion: "Mit tennél másképp ennek alapján?",
      reflectionCtaLabel: "Feliratkozás a Pro várólistára",
      reflectionHelper:
        "Jelentkezz a várólistára, hogy első körben kapj értesítést a Pro tier nyitásáról.",
      reflectionCtaHref: "/blocked",
      footerNote: "Ez az e-mail automatikusan lett küldve, kérjük ne válaszolj rá.",
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
