type PreviewCard = {
  name: string;
  role: string;
  stance: "reject" | "support" | "conditional";
  stanceLabel: string;
  summary: string;
  primaryArgument: string;
  changeCondition: string;
  coreConcern: string;
  buyingTrigger: string;
  riskAppetite: string;
  decisionStyle: string;
  priceSensitivity: string;
  techAdoption: string;
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
      heading: "Konkrét reakciók, különböző attitűdök",
      researchLabel: "Kutatási téma",
      researchValue: "Meggyőző-e ez az üzenet B2B döntéshozóknak: Csökkentsd a sales ciklust 40%-kal automatizálással?",
      audienceLabel: "Célközönség",
      audienceValue: "Közép- és kisvállalati sales és marketing vezetők",
      consensusLabel: "✓ 11/18 támogatja — gyenge konszenzus",
      supportLabel: "Támogatja (61%)",
      rejectLabel: "Ellenzi (39%)",
      supportPercent: 61,
      rejectPercent: 39,
      primaryArgumentLabel: "Fő érv",
      changeConditionLabel: "Mikor változtatna",
      coreConcernLabel: "Fő aggodalom",
      buyingTriggerLabel: "Vásárlási trigger",
      synthesis: {
        label: "Szintézis",
        summary:
          "Az üzenet erős rezonanciát kelt a kkv-s sales vezetők körében, de az adathiány és az általánosság megosztja a döntéshozókat. A támogatók a fájdalomfelismerést értékelik, a kételkedők bizonyítékokat hiányolnak.",
        barriersLabel: "Fő akadályok",
        barriers: [
          "A 40%-os ígéret mögül hiányzik az auditált módszertan",
          "Általános megfogalmazás — nincs szegmensspecifikus relevancia",
        ],
        winningConditionsLabel: "Mikor vennék meg",
        winningConditions:
          "Konkrét esettanulmányok és ingyenes pilot ajánlat esetén a szegmens 70%+ elérése reális.",
        bestTargetLabel: "Legjobb célszegmens",
        bestTarget:
          "45–150 fős tech-barát B2B cégek sales és marketing vezetői, ahol már van CRM-rendszer.",
        recommendationLabel: "Stratégiai javaslat",
        recommendation:
          "Adj hozzá 1 konkrét esettanulmányt és egy ingyenes próbalehetőséget — ez a két elem a feltételes szavazókat is átbillenti.",
      },
      cards: ([
        {
          name: "Tóth Andrea",
          role: "Sales vezető, 45 fős IT cég",
          stance: "support",
          stanceLabel: "Támogatja",
          summary: "A 40% konkrét szám, és az ügyfeleim pont ezt a fájdalmat érzik. Ez bejön.",
          primaryArgument:
            "A konkrét 40%-os szám és a sales ciklus fájdalma teljesen reális — az én csapatom is szenved ettől. Ez hiteles ígéret.",
          changeCondition: "Ha látok legalább 2 hasonló méretű cégnél működő esettanulmányt.",
          coreConcern: "Az integráció a meglévő CRM-ünkkel és a bevezetési idő.",
          buyingTrigger: "Ingyenes pilot program, ahol saját adatainkon tesztelhetek.",
          riskAppetite: "Közepes",
          decisionStyle: "Adatvezérelt",
          priceSensitivity: "Árérzékeny",
          techAdoption: "Korai többség",
        },
        {
          name: "Fekete Márton",
          role: "CEO, B2B SaaS startup",
          stance: "conditional",
          stanceLabel: "Feltételes",
          summary: "Csak akkor hiteles, ha van mögötte valódi referencia-adat. Így üres állítás.",
          primaryArgument:
            "Az üzenet célba ér, de a 40%-os ígéret módszertan nélkül üres marketing szöveg — ilyen számhoz auditált adat kell.",
          changeCondition: "Auditált adatok és átlátható számítási módszertan a 40%-hoz.",
          coreConcern:
            "Ha nem hozza az ígért számot, elveszítjük a hitelességünket az ügyfelek felé.",
          buyingTrigger: "Részletes ROI kalkulátor és referencia ügyfelek közvetlen elérése.",
          riskAppetite: "Alacsony",
          decisionStyle: "Konszenzuskereső",
          priceSensitivity: "Magas",
          techAdoption: "Korai többség",
        },
        {
          name: "Varga Katalin",
          role: "Marketing vezető, szolgáltató cég",
          stance: "reject",
          stanceLabel: "Elutasítja",
          summary: "Túl általános. Minden automatizáló eszköz ugyanezt mondja. Nem differenciál.",
          primaryArgument:
            "Minden automatizáló eszköz pontosan ugyanezt mondja — az üzenet nem differenciál, és nem szól specifikusan az én szegmensemhez.",
          changeCondition: "Szegmensspecifikus megfogalmazás és konkrét iparági benchmark adatok.",
          coreConcern:
            "A 40% teljesen kontextusfüggő — az én iparágamban ez nem reális szám.",
          buyingTrigger: "Dedikált pilot az én iparágamra szabva, valódi ROI garanciával.",
          riskAppetite: "Nagyon alacsony",
          decisionStyle: "Szabálykövető",
          priceSensitivity: "Alacsony",
          techAdoption: "Késői többség",
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
          title: "E-mail érkezik",
          description:
            "Az eredményeket és a részletes elemzést azonnal megkapod a fiókodba.",
        },
      ],
    },
    stats: {
      items: [
        { value: "Ingyenes próba", label: "regisztráció nélkül" },
        { value: "90 másodperc", label: "átlagos várakozás" },
        { value: "Strukturált elemzés", label: "e-mailben, azonnal" },
        { value: "15–20 persona", label: "különböző nézőpont" },
      ],
    },
    closingCta: {
      heading: "Teszteld le a következő feltételezésed még ma.",
      cta: "Ingyen kipróbálom",
      helper: "Egy ingyenes futtatás. Regisztráció nélkül.",
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
        "Írd le a kutatási kérdést és a célcsoportot. Pár perc múlva a postaládádban van az eredmény.",
      researchLabel: "Mit vizsgálsz?",
      audienceLabel: "Kinek szól?",
      researchExamples: [
        "Meggyőző-e ez az árazás: 19 900 Ft/hó az alap, 49 900 Ft/hó a pro — vagy túl közel van egymáshoz a két tier?",
        "Melyik launch üzenet rezonál jobban: 'Spórolj 10 órát hetente' vagy 'Soha többé manuális riportolás'?",
        "Komoly akadályt jelent-e a 3 hónapos szerződéskötési kötelezettség egy új SaaS eszköznél?",
      ],
      audienceExamples: [
        "Alapítók és growth leadek 10-50 fős B2B SaaS startupokban, akik első fizetős ügyfeleiket szerzik",
        "E-commerce marketing vezetők, akik szezonális kampányokat terveznek kisebb büdzsével",
        "HR vezetők 100-500 fős cégeknél, akik új onboarding eszközt keresnek",
      ],
      piiWarning:
        "Ne adj meg személyes adatokat a kutatási témában",
      submitCta: "Tovább",
      helper: "Egy ingyenes elemzés e-mail címenként.",
      errors: {
        researchTopic: "Add meg a kutatási témát.",
        audienceDescription: "Add meg a célközönség leírását.",
        email: "Adj meg érvényes e-mail címet.",
      },
      email: {
        heading: "Hova küldjük az eredményt?",
        subheadline: "Az eredményed erre az e-mailre érkezik",
        successHeading: "Link elküldve",
        successEyebrow: "Következő lépés",
        successBodyPrefix:
          "Elküldtük a kutatás indításához szükséges linket erre az e-mail címre:",
        successHint:
          "Nyisd meg az e-mailed, kattints a linkre, és a kutatás elindul.",
        label: "E-mail cím",
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
    intro: "Mesélj egy kicsit magadról",
    form: {
      roleLabel: "Mi jellemzi legjobban a munkakörödet?",
      rolePlaceholder: "Válassz szerepkört",
      companySizeLabel: "Hány fős cégnél dolgozol?",
      companySizePlaceholder: "Válassz cégméretet",
      companySizeOptions: [
        { value: "1_10", label: "1–10 fő" },
        { value: "11_50", label: "11–50 fő" },
        { value: "51_200", label: "51–200 fő" },
        { value: "200_plus", label: "200+ fő" },
      ],
      marketingProblemLabel: "Mi jelenleg a legnagyobb marketing problémád?",
      marketingProblemPlaceholder: "Pl. nem konvertálnak a landing page-eim, drága az ügyfélszerzés, nem érem el a döntéshozókat, nem tudom, mi tartja vissza az érdeklődőket a vásárlástól...",
      roleOptions: [
        { value: "founder_ceo", label: "Alapító / Ügyvezető" },
        { value: "marketing_lead", label: "Marketing vezető" },
        { value: "product_manager", label: "Termékmenedzser" },
        { value: "sales_lead", label: "Sales vezető" },
        { value: "cfo_finance", label: "CFO / Pénzügy" },
        { value: "consultant_agency", label: "Tanácsadó / Ügynökség" },
        { value: "other", label: "Egyéb" },
      ],
      useCaseLabel:
        "Milyen célra szeretnéd leginkább használni a szintetikus kutatást?",
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
          label: "Lemorzsolódás okok és megtartás",
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
    eyebrow: "Futó elemzés",
    subheadline:
      "A szintetikus personák a háttérben futnak. A kész összefoglalót a megadott e-mailre küldjük.",
    personaSectionLabel: "Persona",
    progressAriaLabel: "Elemzés folyamata",
    completedStatusHint: "Minden persona lefutott",
    partialStatusHint: "Részleges lefutás — részletek az e-mailben",
    states: {
      queued: "Sorban...",
      generating: "Personák generálása...",
      /** Interpolate {current} and {total} before rendering. */
      running: "Futtatás: {current}/{total} persona",
      composing: "Az eredmény összeállítása...",
      completed: "Az eredmény elkészült",
      partial: "Részleges eredmény elkészült",
      failed: "Hiba történt a feldolgozás közben.",
    },
    canCloseNotice: "Nem kell itt várnod, bezárhatod ezt az ablakot. Az eredmény e-mailben érkezik.",
    /** Interpolate {email} before rendering. */
    emailDeliveryNotice: "Az eredményed erre az e-mailre érkezik: {email}",
    delayedNotice:
      "A feldolgozás a szokásosnál tovább tart, még dolgozunk rajta.",
    retrySuggestion: "Próbáld újra egy új elemzés indításával.",
  },
  blockingScreen: {
    heading: "Ez az e-mail cím már igénybe vette az ingyenes próbát",
    body: "Ehhez az e-mail címhez már tartozik lezárt futás, ezért új ingyenes elemzést most nem tudunk indítani.",
    cta: "Iratkozz fel az értesítőre",
    submitted: "Köszönjük! Felírtunk az értesítőre. A Pro hozzáférés indulása előtt e-mailben szólunk.",
    invalidEmail:
      "A várólista-feliratkozáshoz érvényes e-mail átadása szükséges. Menj vissza a kutatási űrlapra, majd próbáld újra.",
    emailPrefix: "Értesítést erre az e-mailre küldünk:",
  },
  verify: {
    title: "A link nem használható",
    descriptionPrefix: "A bejelentkezési linkkel probléma történt:",
    requestNewLinkCta: "Új link kérése",
    verifying: "Link ellenőrzése…",
  },
  email: {
    magicLink: {
      subject: "SwarmSense – indítsd el a kutatást",
      heading: "Egy kattintás, és indul a kutatás",
      intro: "Kattints a gombra, és a kutatás azonnal elindul.",
      buttonLabel: "Kutatás indítása",
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
        preview: "Tetszett az eredmény? Tudunk többet is mutatni.",
        title: "Egy futtatás csak a kezdet.",
        body: "Képzeld el, hogy minden kampányüzeneted, árazási döntésed és go-to-market hipotézised előtt lefuttatod ezt. A Pro hozzáférés hamarosan nyílik — iratkozz fel, hogy ne maradj le róla.",
      },
      day3: {
        preview: "A többiek már várják a Pro hozzáférést.",
        title: "Feliratkoztál már a várólistára?",
        body: "Az ingyenes próba megmutatta, mire képes a szintetikus kutatás. A Pro verzióval teljes hozzáférést kaphatsz — kampányonként, termékenként, piaconként. Iratkozz fel a várólistára, és első körben értesítünk.",
      },
      day7: {
        preview: "Utolsó emlékeztető a Pro várólistáról.",
        title: "Egy hete gondolkodsz — itt az ideje dönteni.",
        body: "A Pro hozzáférés korlátozott létszámmal indul. Ha szeretnél az elsők között lenni, most érdemes feliratkozni — utána már csak a sorban állás marad.",
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
    termsEffectiveDate: "Hatálybalépés: 2026. március 23. · Verzió: 1.0",
    termsIntroParagraphs: [
      "A jelen Felhasználási feltételek (a továbbiakban: Feltételek) szabályozzák a SwarmSense elérhető online szolgáltatás igénybevételét.",
      "A szolgáltatás használatával — különösen a kutatási folyamat megkezdésével, az e-mail cím megadásával és az adatkezeléshez szükséges jelölőnégyzet elfogadásával — a Feltételeket elfogadod, és tudomásul veszed az Adatkezelési tájékoztató tartalmát.",
    ],
    termsSections: [
      {
        title: "1. Hatály és szerződő felek",
        paragraphs: [
          "A Feltételek vonatkoznak minden olyan természetes személyre (a továbbiakban: felhasználó), aki a SwarmSense webes felületét vagy kapcsolódó szolgáltatásait igénybe veszi.",
          "Szolgáltató: a SwarmSense szolgáltatást üzemeltető. A kapcsolattartási elérhetőségeket — amint azok közzétételre kerülnek — az Adatkezelési tájékoztató és ezen az oldalon tesszük közzé.",
        ],
      },
      {
        title: "2. A szolgáltatás jellege",
        paragraphs: [
          "A SwarmSense szintetikus piackutatást nyújt: a megadott kutatási kérdés és célközönség-leírás alapján a rendszer AI által generált, fiktív personák (szintetikus döntéshozói profilok) reakcióit és összefoglaló elemzését állítja elő, és az eredményt e-mailben kézbesíti.",
          "A szolgáltatás tartalma, elérhetősége és funkciói változhatnak (beleértve a próba- vagy ingyenes futtatások korlátait); a lényeges változásokról ésszerűen tájékoztatunk (például ezen az oldalon vagy a szolgáltatás felületén).",
        ],
      },
      {
        title: "3. Regisztráció, e-mail, hitelesítés",
        paragraphs: [
          "A szolgáltatás egyes lépéseihez érvényes e-mail cím megadása és — ahol kérjük — a Felhasználási feltételek és az Adatkezelési tájékoztató elfogadása szükséges. A megadott e-mail címért felelsz: azt csak jogosultságodban álló címre add meg.",
          "Ahol a folyamat mágikus linkes vagy hasonló hitelesítést használ, a linket tartsd bizalmasan; a linken keresztül történő hozzáférésért te felelsz.",
        ],
      },
      {
        title: "4. Felhasználói magatartás és tiltott tartalom",
        paragraphs: [
          "Kötelezed magad, hogy a szolgáltatást jogszerűen, mások jogait és a vonatkozó szabályokat nem sértve veszed igénybe. Különösen tilos:",
        ],
        list: [
          "a kutatási témába vagy bármely mezőbe valós személyek azonosítására alkalmas adat, különleges kategóriájú személyes adat, illetve jogellenes vagy mások jogát sértő tartalom megadása;",
          "a szolgáltatás visszaélésszerű használata (pl. automatizált visszaélésszerű terhelés, mások zaklatása, rosszindulatú tartalom terjesztése);",
          "megkísérelni a szolgáltatás, más felhasználók adatainak vagy háttérrendszerek jogosulatlan elérését.",
        ],
      },
      {
        title: "5. Szellemi alkotások és licence a bemenetekre",
        paragraphs: [
          "A SwarmSense megjelenése, logói, szövegei és szoftverkomponensei a szolgáltató vagy partnerei jogosultságát képezik; ezeket a felhasználó nem másolhatja, nem terjesztheti és nem módosíthatja a jogszabály által megengedett szűk kör kivételével.",
          "A kutatási témaként, célközönség-leírásként és egyéb mezőkben általad megadott tartalomért te felelsz; a szolgáltató részére nem kizárólagos, a szolgáltatás nyújtásához szükséges felhasználási jogot adsz (feldolgozás, tárolás, elemzés előállítása és kézbesítés).",
        ],
      },
      {
        title: "6. Szintetikus eredmény — nem tanácsadás, nem reprezentatív felmérés",
        paragraphs: [
          "Az előállított elemzés, personák és összefoglalók tájékoztató jellegűek, piaci vagy termékhipotézisek gyors előtesztelésére; nem minősülnek szakmai, pénzügyi, jogi vagy egyéb szakértői tanácsadásnak, és nem helyettesítik a valós piaci vagy fogyasztói kutatást.",
          "A szolgáltató nem vállal felelősséget azért, hogy az eredmény bármely üzleti vagy jogi döntéshez megfelelő vagy teljes lenne; a döntéseket saját felelősségre hozod.",
        ],
      },
      {
        title: "7. Elérhetőség, változtatás, szünet",
        paragraphs: [
          "A szolgáltatást igyekszünk folyamatosan rendelkezésre bocsátani, de nem garantáljuk a megszakításmentes működést. Karbantartás, frissítés, harmadik felek hibái vagy vis maior esetén szünet előfordulhat; erről ésszerűen törekszünk tájékoztatni, ha az indokolt.",
        ],
      },
      {
        title: "8. Díjazás",
        paragraphs: [
          "A szolgáltatás egyes funkciói — a felületen feltüntetett módon — ingyenes próba vagy korlátozott futtatás keretében érhetők el. Későbbi fizetős csomagok vagy előfizetés bevezetése esetén a díjakat és feltételeket külön, előzetesen közöljük.",
        ],
      },
      {
        title: "9. Felelősség korlátozása",
        paragraphs: [
          "A szolgáltatást „ahogy van” (as-is) biztosítjuk, a jogszabályok által megkövetelt kötelező szavatossági és kellékszavatossági szabályok alkalmazásával. A szolgáltató — a jogszabály által kizárni nem engedett mértékig — nem felel a közvetett kárért, elmaradt haszonért vagy olyan kárért, amely a szolgáltatáson kívüli körülményből fakad.",
          "Ha a felelősség valamilyen formában fennáll, a szolgáltató díjazás esetén — a jogszabály által megengedett keretek között — általában a vonatkozó szolgáltatásért az adott ügyben ténylegesen megfizetett összeggel arányosított mértékben felel.",
        ],
      },
      {
        title: "10. Adatvédelem",
        paragraphs: [
          "A személyes adatok kezelését az Adatkezelési tájékoztató részletezi; kérjük, azt külön olvasd el.",
        ],
        linkPrivacy: true,
      },
      {
        title: "11. Panasz, vitarendezés",
        paragraphs: [
          "Panaszodat először a szolgáltató felé — a közzétett kapcsolattartási csatornán — jelezheted, amint az elérhető. Fogyasztói jogvita esetén élni lehet a lakóhely szerinti békéltető testület vagy a szolgáltató székhelye szerinti testület eljárása iránti igénnyel, valamint az online vitarendezési platform (ODR) lehetőségével, ha alkalmazható.",
        ],
      },
      {
        title: "12. Alkalmazandó jog",
        paragraphs: [
          "A Feltételekre a magyar jog irányadó; az Európai Unió fogyasztóvédelmi előírásai a fogyasztóval szemben alkalmazandó szabályok szerint érvényesülhetnek.",
        ],
      },
      {
        title: "13. A Feltételek módosítása",
        paragraphs: [
          "A Feltételeket időről időre módosíthatjuk. A hatályos szöveg mindig ezen az oldalon érhető el; lényeges változásnál — ha indokolt — külön is felhívjuk a figyelmet (például a szolgáltatás felületén vagy e-mailben). A módosítás közzététele után a szolgáltatás további használata a módosítás elfogadásának minősül, kivéve, ha a jogszabály másként rendelkezik.",
        ],
      },
    ],
    privacyEffectiveDate: "Hatálybalépés: 2026. március 23. · Verzió: 1.0",
    privacyIntroParagraphs: [
      "A SwarmSense egy szintetikus piackutatási szolgáltatás: a feltöltött kutatási kérdésre és célközönség-leírásra a rendszer szintetikus personák (AI által generált, fiktív döntéshozói profilok) reakcióit és összefoglaló elemzését állítja elő, majd az eredményt e-mailben eljuttatja a megadott címre.",
      "Személyes adataidat az Európai Parlament és a Tanács (EU) 2016/679 rendelete (GDPR) szerint, valamint az információs önrendelkezési jogról és az információszabadságról szóló 2011. évi CXII. törvény (Infotv.) előírásai szerint kezeljük.",
    ],
    controllerTitle: "1. Adatkezelő és elérhetőség",
    controllerBody:
      "Adatkezelő: a SwarmSense szolgáltatást üzemeltető. Dedikált általános és adatvédelmi e-mail címek egyelőre nem állnak rendelkezésre; a pontos elérhetőséget ezen a tájékoztató oldalon tesszük közzé, amint elérhetővé válik.",
    processedDataTitle: "2. Kezelt személyes adatok köre",
    processedDataItems: [
      "e-mail cím (azonosítás, eredmény és értesítések kézbesítése)",
      "a GDPR-hozzájárulás ténye és időbélyege (consent_timestamp)",
      "kutatási téma és célközönség szöveges leírása (futáshoz kötve)",
      "qualifier kérdőív válaszok: szerepkör, use case, valamint — ha megadod — cégméret és marketing probléma",
      "futáshoz kapcsolódó elemzési eredmények és szintézis mezők (összefoglalók, támogató / elutasító / feltételes arányok, stratégiai javaslat szövegek)",
      "futás státusza, technikai és költség jellegű metaadatok, időbélyegek",
      "marketing / follow-up e-mailek küldésének státusza (pl. nap 1 / 3 / 7 jelölések), valamint leiratkozás időpontja (unsubscribed_at), ha leiratkoztál",
      "Pro várólistára felvett e-mail cím, ha a szolgáltatás ezt igénybe veszed",
      "mágikus linkes hitelesítéshez kapcsolódó technikai token metaadatok (érvényesség szerint kezelve)",
    ],
    legalBasisTitle: "3. Az adatkezelés jogalapja és célja",
    legalBasisBody:
      "Az e-mail cím és a szolgáltatás nyújtásához szükséges tartalom kezelésének jogalapja a GDPR 6. cikk (1) bekezdés b) pontja (szerződés vagy az arra való előkészület — szolgáltatás nyújtása). A külön megadott, egyértelmű hozzájárulás (a tájékoztató és a felhasználási feltételek elfogadása az e-mail beküldésekor) a GDPR 6. cikk (1) bekezdés a) pontja szerinti jogalapot teremti a hozzájáruláshoz kötött elemekre. A szolgáltatás biztonságos működtetése, visszaélések megelőzése és minőségbiztosítás céljából szükséges, mértékű adatkezelés jogalapja a GDPR 6. cikk (1) bekezdés f) pontja szerinti jogos érdek; ilyenkor figyelembe vesszük az érdekmérlegelést. Marketing jellegű (nem tranzakciós) e-mailek küldéséhez — ha alkalmazunk ilyet — a hozzájárulásod vagy jogos érdekünk és a leiratkozási jog biztosítása a mérvadó.",
    aiProcessingTitle: "4. Szintetikus kutatás és automatizált feldolgozás",
    aiProcessingBody:
      "A SwarmSense nem valós személyeket kérdez meg; a válaszokat és összefoglalókat nagy nyelvi modellek és kapcsolódó automatizmusok állítják elő a megadott bemenetek alapján. Az eredmény tájékoztató jellegű, piaci hipotézisek gyors tesztelésére szolgál — nem minősül valós fogyasztói vagy iparági reprezentatív felmérésnek, és nem helyettesíti a szakmai vagy jogi tanácsadást. Kérjük, a kutatási témában ne adj meg különleges kategóriájú személyes adatot vagy bizalmas vállalati titkot.",
    cookiesTitle: "5. Cookie-k és látogatás-statisztika",
    cookiesBody:
      "A webes felületen elsősorban a működéshez szükséges (pl. munkamenet / bejelentkezéshez kötött) technikai jellegű tárolást használhatunk. Látogatás-statisztikára — ha beépítésre kerül — olyan megoldást részesítünk előnyben, amely személyazonosításra nem alkalmas, és lehetőség szerint nem igényel külön sütihozzájáruló bannert (pl. cookie-mentes, aggregált analitika). Konkrét eszközök listáját e tájékoztató frissítésekor tesszük közzé.",
    processorsTitle: "6. Adatfeldolgozók, tárolás, harmadik felek",
    processorsBody:
      "Az adatokat elsősorban az Európai Gazdasági Térségben (EGT) elhelyezett vagy ahhoz megfelelőségi döntés / megfelelő garanciák (pl. szerződéses záradékok) mellett kezelt felhőszolgáltatásokban tároljuk (adatbázis, alkalmazás-hosztolás). E-mail kézbesítéshez megbízott levelezési szolgáltatót veszünk igénybe. A pontos alvállalkozók és szolgáltatók neve, valamint az adattovábbítás részletei változáskor ezen az oldalon frissülnek. Harmadik országba csak megfelelő garanciák mellett továbbítunk adatot.",
    retentionTitle: "7. Megőrzési időtartamok",
    retentionBody:
      "A személyes adatokat csak addig őrizzük meg, ameddig a szolgáltatás nyújtásához, jogi kötelezettség teljesítéséhez (pl. számviteli, vitarendezési igény) vagy jogos érdek érvényesítéséhez szükséges — ezután töröljük vagy anonimizáljuk. Technikai naplók és biztonsági másolatok megőrzése rövidebb, szigorúan szükséges ideig történhet.",
    marketingCommsTitle: "8. Tájékoztató és marketing jellegű e-mailek, leiratkozás",
    marketingCommsBody:
      "A szolgáltatáshoz kapcsolódó tranzakciós üzenetek (pl. eredmény, hitelesítő link) a szolgáltatás részeként kerülnek kiküldésre. Ettől elkülönülő, tájékoztató vagy promóciós jellegű e-maileket csak akkor küldünk, ha azt a jogszabályoknak megfelelően megtehetjük; ilyenkor minden levélben biztosítjuk a leiratkozás lehetőségét (pl. link). A leiratkozás után marketing célú üzenetet nem küldünk a megadott címre.",
    userRightsTitle: "9. Érintetti jogok és felügyeleti hatóság",
    userRightsBody:
      "Jogosult vagy tájékoztatást kérni az általunk kezelt adataidról, kérheted azok helyesbítését, törlését, az adatkezelés korlátozását, valamint — a jogalaptól függően — tiltakozhatsz az adatkezelés ellen, és kérheted az adathordozhatóságot, ha az alkalmazható. Az érintetti kérelmek benyújtására szolgáló dedikált kapcsolattartási cím bevezetés alatt áll; a pontos elérhetőséget ezen a tájékoztató oldalon frissítjük.",
    userRightsSupervisoryBody:
      "Panaszoddal a Nemzeti Adatvédelmi és Információszabadság Hatósághoz (NAIH) fordulhatsz:",
    userRightsSupervisoryLinkLabel: "www.naih.hu",
    userRightsSupervisoryHref: "https://www.naih.hu/",
    deletionTitle: "10. Törlési kérelem (GDPR 17. cikk)",
    deletionContactLabel: "Kérelem benyújtása",
    deletionContactEmail:
      "Dedikált e-mail cím a törlési kérelmekhez: bevezetés alatt — a pontos címet ezen a tájékoztató oldalon tesszük közzé.",
    deletionAckSlaLabel: "Tervezett visszaigazolás (a kérelemfogadó csatorna elindításától)",
    deletionAckSlaValue: "15 percen belül",
    deletionCompletionSlaLabel: "Tervezett törlés teljesítése (a kérelemfogadó csatorna elindításától)",
    deletionCompletionSlaValue: "7 naptári napon belül",
    deletionMvpScope:
      "Önkiszolgáló törlőportál nem áll rendelkezésre. Amint a törlési és adatvédelmi kérelmek fogadására dedikált e-mail elérhető, a kérelmet onnan lehet benyújtani; a kérelemben egyértelműen jelöld meg az érintett e-mail címet. A törlés a vonatkozó adatbázis-rekordokra és a szolgáltatás keretében tárolt tartalmakra terjed ki, a jogszabály által megengedett kivételekkel (pl. számviteli bizonylat).",
    updatesTitle: "11. A tájékoztató módosítása",
    updatesBody:
      "A tájékoztatót a szolgáltatás vagy a jogszabályi környezet változásakor frissíthetjük. A hatályos verzió mindig ezen az oldalon érhető el; jelentős változásnál — ha szükséges — külön is felhívjuk a figyelmet (pl. e-mailben vagy a szolgáltatás felületén).",
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
