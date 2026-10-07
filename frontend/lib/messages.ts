const linkWarning =
  "A futás linkjét ne írd bele nyilvános issue-ba: nyiss bejelentést link nélkül, a linket privát csatornán kérjük el tőled.";

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
        "Írd le a kérdésed és a célközönséged: 18 szintetikus persona válaszol rá, nagyjából másfél-két perc alatt, regisztráció nélkül. A futást élőben követheted, az eredményt PDF-ben letöltheted.",
      cta: "Ingyen kipróbálom",
      sampleCta: "Minta megtekintése",
      cardLabel: "Illusztráció",
      cardAriaLabel: "Illusztráció: példaeredmény",
    },
    painBridge: {
      heading: "Mit csinál a darab",
      closing:
        "A SwarmSense portfóliódarab: a válaszokat egy nyelvi modell szimulálja, nem valódi megkérdezettek. Valódi piackutatást nem vált ki.",
      methodologyLink: "A módszertanról bővebben",
      items: [
        {
          title: "Élő trace",
          description:
            "Minden persona állapotát, kísérletszámát és idejét látod, ahogy a futás halad.",
        },
        {
          title: "18 persona, legfeljebb 5 párhuzamos hívással",
          description:
            "Egy hívás elkészíti a leírásokat, utána a personák külön hívásokban válaszolnak, egyszerre legfeljebb 5.",
        },
        {
          title: "PDF az eredményről",
          description:
            "Az összefoglaló és a personák válaszai letölthetők PDF-ben, kérésre levélben is megkapod.",
        },
      ],
    },
    preview: {
      eyebrow: "Illusztráció",
      heading: "Így nézhet ki egy eredmény",
      illustrationNote:
        "Kitalált példaadat, nem egy valódi futás eredménye. Alább egy valódi futást is megnézhetsz.",
      sampleLink: "Nézz meg egy valódi mintafutást",
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
          "Adj hozzá 1 konkrét esettanulmányt és egy kipróbálható pilotot — ez a két elem a feltételes szavazókat is átbillenti.",
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
            "Add meg a kérdésed és a célközönséged. Két mező, regisztráció nélkül.",
        },
        {
          title: "A futás élőben követhető",
          description:
            "18 szintetikus persona válaszol, egyszerre legfeljebb 5. Az élő trace-en látod, hol tart a futás.",
        },
        {
          title: "Megkapod az eredményt",
          description:
            "Az eredményoldalon elolvasod az összefoglalót és a personák válaszait, és letöltheted PDF-ben.",
        },
      ],
    },
    stats: {
      items: [
        { value: "18 persona", label: "nyelvi modell által generált" },
        { value: "Másfél-két perc", label: "egy futás nagyjából" },
        { value: "Regisztráció nélkül", label: "két mezős űrlap" },
        { value: "PDF", label: "letölthető eredmény" },
      ],
    },
    closingCta: {
      heading: "Próbáld ki a demót.",
      cta: "Ingyen kipróbálom",
      helper: "Regisztráció nélkül, napi keretekkel.",
    },
    footer: {
      privacy: "Adatkezelési tájékoztató",
      terms: "Felhasználási feltételek",
      methodology: "Módszertan",
    },
  },
  research: {
    form: {
      eyebrow: "Új kutatás",
      headline: "Mi a hipotézised?",
      subheadline:
        "Írd le a kutatási kérdést és a célcsoportot. Az elemzés nagyjából másfél-két perc alatt lefut.",
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
      submitCta: "Elemzés indítása",
      helper: "Regisztráció és e-mail-cím nélkül.",
      errors: {
        researchTopic: "Add meg a kutatási témát.",
        audienceDescription: "Add meg a célközönség leírását.",
      },
    },
  },
  trace: {
    eyebrow: "Élő futás",
    elapsedLabel: "Eltelt idő",
    topicLabel: "Kérdés",
    phasesAriaLabel: "A futás fázisai",
    phases: {
      generating: "Personák generálása",
      personas: "18 persona",
      synthesis: "Szintézis",
      pdf: "PDF",
    },
    summaryAriaLabel: "Összesítő",
    summary: {
      queued: "sorban áll",
      running: "fut",
      completed: "kész",
      failed: "kiesett",
      inputTokens: "bemeneti token",
      outputTokens: "kimeneti token",
      cost: "becsült költség",
      estimate: "becslés",
    },
    personasAriaLabel: "Personák",
    row: {
      queued: "sorban áll",
      running: "fut",
      completed: "kész",
      failed: "kiesett",
      attemptLabel: "kísérlet",
      // a sor saját tokenjei: „be 812 · ki 1 940 token"
      tokensIn: "be",
      tokensOut: "ki",
      tokensUnit: "token",
      tokensPending: "–",
    },
    synthesisFailedNotice: "A szintézis nem sikerült, a futás részleges eredménnyel zárul.",
    connectionLost: "A kapcsolat megszakadt, az élő követés leállt.",
    notFound: "Nem találjuk ezt a futást.",
    failedHeading: "A futás nem fejeződött el",
    sampleLink: "Nézd meg a mintafutást",
    formLink: "Új elemzés indítása",
  },
  replay: {
    eyebrow: "Visszajátszás",
    recorded: "Rögzített futás",
    jumpToResult: "Ugrás az eredményre",
    again: "Újra",
    error: "A visszajátszás most nem tölthető be.",
    sampleUnavailable: "A mintafutás most nem érhető el.",
  },
  result: {
    eyebrow: "Eredmény",
    audienceLabel: "Célközönség",
    summaryHeading: "Összefoglaló",
    synthesisMissing:
      "A szintézis nem készült el; a personák válaszai a PDF-ben vannak.",
    stanceHeading: "Állásfoglalások megoszlása",
    stance: {
      support: "Támogatja",
      reject: "Elutasítja",
      conditional: "Feltételes",
    },
    runDataHeading: "Futásadatok",
    duration: "Futásidő",
    seconds: "mp",
    inputTokens: "Bemeneti token",
    outputTokens: "Kimeneti token",
    cost: "Becsült költség",
    estimate: "becslés",
    retries: "Újrapróbálkozások",
    personasAnswered: "persona válaszolt",
    replayLink: "Futás visszajátszása",
    pdfLink: "PDF letöltése",
    limitsHeading: "Mire nem jó",
    limitsText:
      "Az eredmény szintetikus personák válasza, nem valódi megkérdezés. Hipotézisek gyors előszűrésére való; döntést megalapozó piackutatást nem vált ki.",
    methodologyLink: "Módszertan",
    failedHeading: "A futás nem fejeződött el",
    failedFallback: "Ehhez a futáshoz nincs eredmény.",
    email: {
      heading: "PDF e-mailben",
      label: "E-mail-cím",
      submit: "Küldés",
      sending: "Küldés...",
      sent: "A levelet elküldtük. Pár percen belül meg kell érkeznie.",
      retentionNote: "A címet a levél elküldéséhez használjuk, és 14 nap után töröljük.",
      privacyLink: "Adatkezelés",
    },
  },
  legal: {
    privacyTitle: "Adatkezelési tájékoztató",
    termsTitle: "Felhasználási feltételek",
    effectiveDate: "Hatálybalépés: 2026. október 7. · Verzió: 2.0",
    contactFallback: `Kapcsolat: a repo issue-követőjén. ${linkWarning}`,
    linkWarning,
    contactLabel: "Kapcsolat",
    termsIntroParagraphs: [
      "A jelen Felhasználási feltételek (a továbbiakban: Feltételek) a SwarmSense nevű webes demó használatát szabályozzák.",
    ],
    termsSections: [
      {
        title: "1. Hatály és szolgáltató",
        paragraphs: [
          "A Feltételek mindenkire vonatkoznak, aki a SwarmSense webes felületét használja.",
          "Szolgáltató: a SwarmSense demó üzemeltetője.",
        ],
        contact: true,
      },
      {
        title: "2. A szolgáltatás jellege",
        paragraphs: [
          "A SwarmSense egy bemutató célú, ingyenes demó. A megadott kérdés és célközönség alapján egy nyelvi modell fiktív personák (szintetikus döntéshozói profilok) válaszait és egy összefoglalót állít elő. Az eredményt az oldalon mutatjuk meg, és PDF-ben le lehet tölteni.",
          "A demó napi keretekkel működik: korlátozott az egyidejű futások, az IP-címenkénti és az összes futás száma. Rendelkezésre állást nem vállalunk, és a demó tartalma vagy működése előzetes értesítés nélkül változhat vagy megszűnhet.",
        ],
      },
      {
        title: "3. Felhasználói magatartás és tiltott tartalom",
        paragraphs: [
          "Kötelezed magad, hogy a szolgáltatást jogszerűen, mások jogait és a vonatkozó szabályokat nem sértve használod. Különösen tilos:",
        ],
        list: [
          "a kérdés vagy a célközönség mezőjébe valós személyek azonosítására alkalmas adatot, különleges kategóriájú személyes adatot, illetve jogellenes vagy mások jogát sértő tartalmat írni;",
          "a szolgáltatással visszaélni (például túlzott terhelést okozó automatizált kérések küldése, mások zaklatása, rosszindulatú tartalom terjesztése);",
          "megkísérelni a szolgáltatás vagy a háttérrendszerek jogosulatlan elérését.",
        ],
      },
      {
        title: "4. Szellemi alkotások és a megadott szövegek",
        paragraphs: [
          "A SwarmSense megjelenése, szövegei és szoftverkomponensei a szolgáltató vagy partnerei tulajdonában vannak. A jogszabály által megengedett szűk kör kivételével nem másolhatod, nem terjesztheted és nem módosíthatod őket.",
          "A kérdésért és a célközönség leírásáért te felelsz. A szolgáltatónak nem kizárólagos felhasználási jogot adsz arra, hogy ezeket a demó működtetéséhez feldolgozza, tárolja, és az eredményt előállítsa és megjelenítse.",
        ],
      },
      {
        title: "5. Szintetikus eredmény: nem tanácsadás, nem reprezentatív felmérés",
        paragraphs: [
          "Az előállított elemzés, a personák és az összefoglalók tájékoztató jellegűek, piaci vagy termékhipotézisek gyors előszűrésére valók. Nem minősülnek szakmai, pénzügyi, jogi vagy egyéb szakértői tanácsadásnak, és nem helyettesítik a valós piaci vagy fogyasztói kutatást.",
          "A szolgáltató nem vállal felelősséget azért, hogy az eredmény bármely üzleti vagy jogi döntéshez megfelelő vagy teljes lenne; a döntéseket saját felelősségre hozod.",
        ],
        methodologyLink: true,
      },
      {
        title: "6. Elérhetőség",
        paragraphs: [
          "A demó nem garantál megszakításmentes működést. Karbantartás, hiba, a napi keretek betelése vagy külső szolgáltatók kiesése miatt bármikor elérhetetlenné válhat.",
        ],
      },
      {
        title: "7. Felelősség korlátozása",
        paragraphs: [
          "A szolgáltatást „ahogy van” (as-is) biztosítjuk, a jogszabályok által megkövetelt kötelező szavatossági szabályok alkalmazásával. A szolgáltató a jogszabály által kizárni nem engedett mértékig nem felel a közvetett kárért, az elmaradt haszonért, illetve a szolgáltatáson kívüli körülményből fakadó kárért.",
        ],
      },
      {
        title: "8. Adatvédelem",
        paragraphs: [
          "A személyes adatok kezelését az Adatkezelési tájékoztató részletezi; azt külön olvasd el.",
        ],
        linkPrivacy: true,
      },
      {
        title: "9. Panasz, vitarendezés",
        paragraphs: [
          "Panaszodat a kapcsolattartási elérhetőségen jelezheted. Fogyasztói jogvita esetén élni lehet a lakóhely szerinti békéltető testület eljárásának kezdeményezésével, valamint az online vitarendezési platform (ODR) lehetőségével, ha alkalmazható.",
        ],
        contact: true,
      },
      {
        title: "10. Alkalmazandó jog",
        paragraphs: [
          "A Feltételekre a magyar jog irányadó; az Európai Unió fogyasztóvédelmi előírásai a fogyasztóval szemben alkalmazandó szabályok szerint érvényesülhetnek.",
        ],
      },
      {
        title: "11. A Feltételek módosítása",
        paragraphs: [
          "A Feltételeket időről időre módosíthatjuk. A hatályos szöveg mindig ezen az oldalon érhető el. A módosítás közzététele után a demó további használata a módosítás elfogadásának minősül, kivéve, ha a jogszabály másként rendelkezik.",
        ],
      },
    ],
    methodologyLinkLabel: "Módszertan",
    privacyIntroParagraphs: [
      "A SwarmSense egy bemutató célú demó: a megadott kérdésre és célközönségre egy nyelvi modell szintetikus personák (fiktív döntéshozói profilok) válaszait és egy összefoglalót állítja elő. Regisztráció és fiók nincs.",
      "Személyes adataidat az Európai Parlament és a Tanács (EU) 2016/679 rendelete (GDPR), valamint az információs önrendelkezési jogról és az információszabadságról szóló 2011. évi CXII. törvény (Infotv.) előírásai szerint kezeljük.",
    ],
    controllerTitle: "1. Adatkezelő és elérhetőség",
    controllerBody: "Adatkezelő: a SwarmSense demó üzemeltetője.",
    processedDataTitle: "2. Kezelt adatok",
    processedDataItems: [
      "a kérdés és a célközönség szövege, valamint a futás eredménye (a personák válaszai, az összefoglaló és a PDF);",
      "a futás állapota, időbélyegei, tokenszámai és hibakódja;",
      "az IP-címed kulcsolt lenyomata (HMAC), a visszaélések korlátozásához. Az IP-cím nyersen nem tárolódik;",
      "az e-mail-cím, de csak akkor, ha a PDF-et levélben kéred.",
    ],
    cookiesTitle: "3. Sütik és webanalitika",
    cookiesBody: "Az oldal nem használ sütit és webanalitikát, és regisztrációt sem kér.",
    visibilityTitle: "4. A futás szövege és láthatósága",
    visibilityBody:
      "A kérdés és a célközönség szövege, valamint a futás eredménye korlátlan ideig megmarad. A futás linkjének birtokában bárki láthatja őket, ezért a linket kezeld úgy, mintha nyilvános lenne. Ne írj a mezőkbe személyes adatot vagy üzleti titkot.",
    processorsTitle: "5. Külső szolgáltatók",
    processorsItems: [
      "A kérdés és a célközönség szövege az opencode szolgáltatáson keresztül a DeepSeek nyelvi modelljéhez kerül feldolgozásra. A feldolgozás az Európai Gazdasági Térségen kívül is történhet.",
      "Ha a PDF-et levélben kéred, a levelet a Resend küldi. Egyetlen levél megy, a címet 14 nap után töröljük az adatbázisunkból. A Resend saját naplója ettől független, arra a törlésünk nem terjed ki.",
      "Ha egy futás hibával leáll, egy Discord-csatornára értesítés megy a futás azonosítójával és a hibakóddal. A kérdés szövege és az e-mail-cím nem kerül bele.",
    ],
    legalBasisTitle: "6. Jogalap",
    legalBasisBody:
      "A futás adatainak és az IP-cím lenyomatának kezelése a GDPR 6. cikk (1) bekezdés f) pontja szerinti jogos érdeken alapul: ez a demó működtetése és a visszaélések korlátozása. Az e-mail-cím kezelésének jogalapja a b) pont: a kért levél elküldése.",
    retentionTitle: "7. Megőrzési idő",
    retentionItems: [
      "A kérdés, a célközönség és az eredmény korlátlan ideig megmarad, amíg törlést nem kérsz.",
      "Az IP-cím lenyomata a futás mellett marad.",
      "Az e-mail-cím 14 nap után törlődik az adatbázisból.",
    ],
    userRightsTitle: "8. Érintetti jogok és felügyeleti hatóság",
    userRightsBody:
      "Tájékoztatást kérhetsz az általunk kezelt adataidról, kérheted azok helyesbítését, törlését és az adatkezelés korlátozását, illetve tiltakozhatsz az adatkezelés ellen. A kérelmeket a kapcsolattartási elérhetőségen fogadjuk.",
    userRightsSupervisoryBody:
      "Panaszoddal a Nemzeti Adatvédelmi és Információszabadság Hatósághoz (NAIH) fordulhatsz:",
    userRightsSupervisoryLinkLabel: "www.naih.hu",
    userRightsSupervisoryHref: "https://www.naih.hu/",
    deletionTitle: "9. Törlési kérelem (GDPR 17. cikk)",
    deletionBodyNoAddress: `Egy futás törléséhez nyiss bejelentést a repo issue-követőjén. ${linkWarning} A futás szövegét és eredményét töröljük az adatbázisból. Az e-mail-cím 14 nap után magától törlődik; korábbi törlését ugyanitt kérheted.`,
    deletionBody:
      "Egy futás törléséhez küldd el a futás linkjét a kapcsolattartási címre. A futás szövegét és eredményét töröljük az adatbázisból. Az e-mail-cím 14 nap után magától törlődik; korábbi törlését ugyanitt kérheted.",
    updatesTitle: "10. A tájékoztató módosítása",
    updatesBody:
      "A tájékoztatót a demó vagy a jogszabályi környezet változásakor frissíthetjük. A hatályos verzió mindig ezen az oldalon érhető el.",
  },
  methodology: {
    title: "Módszertan",
    intro:
      "Ez az oldal leírja, mit csinál a SwarmSense egy futás alatt, és mire nem használható az eredmény. A SwarmSense portfóliódarab, nem kutatási szolgáltatás.",
    sections: [
      {
        title: "Mi történik egy futásban",
        paragraphs: [],
        list: [
          "Egy LLM-hívás 18 persona-leírást készít a megadott célközönségre.",
          "Mind a 18 persona külön hívásban válaszol a kérdésre, egyszerre legfeljebb 5.",
          "Egy utolsó hívás szintézist ír a válaszokból.",
        ],
        after:
          "Ez összesen 20 hívás. A DeepSeek flash modelljét használjuk, az opencode szolgáltatáson keresztül. Egy futás nagyjából másfél-két percig tart, de ez a modell terhelésétől függ.",
      },
      {
        title: "Mi történik, ha valami nem sikerül",
        paragraphs: [],
        list: [
          "Sikertelen hívásnál legfeljebb 3 kísérlet történik.",
          "Ha egy persona válasza a megadott séma szerint érvénytelen, a persona kiesik az eredményből.",
          "Ha 12-nél kevesebb persona válaszol érvényesen, a futás sikertelen.",
          "Ha a szintézis hívása nem sikerül, az eredmény szintézis nélkül készül el. A personák válaszai ilyenkor is megvannak.",
        ],
      },
      {
        title: "Mit jelentenek a számok",
        paragraphs: [
          "A tokenszám a szolgáltató által jelentett érték. A költség listaárból számolt becslés: a demó előfizetéses kereten fut, ezért futásonkénti tényleges költség nincs.",
        ],
      },
      {
        title: "Mire nem jó",
        paragraphs: [],
        list: [
          "A personák nem valódi emberek, a válaszok egy nyelvi modell kimenetei.",
          "Az eredmény nem reprezentatív, és ugyanarra a kérdésre futásonként más jöhet ki.",
          "Hipotézisek előszűrésére való. Döntést megalapozó piackutatást nem vált ki.",
        ],
      },
    ],
    sampleHeading: "Mintafutás",
    sampleText: "A mintafutás egy valódi futás: végigkövethető és visszajátszható.",
    sampleLink: "Nézd meg a mintafutást",
  },
  piiWarning: "Ne adj meg személyes adatot vagy bizalmas információt.",
  genericError: "Váratlan hiba történt. Kérjük, próbáld újra.",
};
