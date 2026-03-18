**ÜZLETI TERV**

**Szintetikus Piackutatás - Csali Termék**

Email lista építés & agent-alapú marketing pozicionálás

2026 március

| **Cél**<br><br>**1 000+ email** | **MVP fejlesztési idő**<br><br>**1-2 hét** | **Tervezett launch**<br><br>**Április 2026** |
| ------------------------------- | ------------------------------------------ | -------------------------------------------- |

# **1\. Stratégiai kontextus**

Ez a dokumentum nem egy hagyományos üzleti terv - nem egy termék piacra vitelét, hanem egy közönség felépítését tervezi. A szintetikus piackutatási platform ebben a fázisban elsősorban csali termék: célja email cím gyűjtése, fájdalompontok feltérképezése, és pozicionálás egy jövőbeli agent-alapú marketing ajánlathoz.

|     | **Alapelv**<br><br>A csali terméknek nem kell tökéletesnek lennie - elég érdekesnek lennie ahhoz, hogy valaki megadja az email-jét. A valódi termék döntés az email listán szerzett piaci visszajelzés alapján születik meg. |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

### **Mi a csali termék?**

Egy egyszerű webes eszköz, ahol a felhasználó megad egy kutatási témát és egy célcsoportot, majd 10-20 AI-generált persona véleményét kapja meg. Az eredmény előtt email regisztrációt és 1-2 minősítő kérdést kér a rendszer.

### **Mi NEM a cél ebben a fázisban?**

- Tökéletes, skálázható SaaS termék építése
- Calibration DB és validációs infrastruktúra kiépítése
- Enterprise sales és tier-struktúra
- 1000 personás szimulációk ingyenesen kínálása

# **2\. Célközönség**

A csali termék célközönsége és a jövőbeli agent-alapú marketing ajánlat célközönsége szándékosan átfed - ez az egész stratégia alapja.

| **Szegmens**                  | **Miért vonzódik a csali termékhez**                                 |
| ----------------------------- | -------------------------------------------------------------------- |
| Marketing & brand managerek   | Gyors kreatív validációt keresnek hirdetések, üzenetek tesztelésére  |
| Reklámügynökségek             | Ügyfeleknek kell gyors insight, nincs idő és budget teljes kutatásra |
| Product managerek (SaaS)      | Agilis fejlesztési ciklus, folyamatosan tesztelik az üzenetet        |
| Kis- és közepes vállalkozások | Nem engedhetik meg a hagyományos piackutatást                        |
| Startuperek, alapítók         | Termékvalidáció olcsón, MVP előtt                                    |

|     | **Magyar piaci fókusz**<br><br>Az első fázisban kifejezetten magyar piac - magyar nyelvű platform, magyar célcsoportok szimulálása, és a hazai marketing szakma megszólítása. Ez csökkenti a versenyt és növeli a relevancia érzetet. |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

# **3\. MVP termék specifikáció**

Az MVP-t a lehető legegyszerűbbre kell tervezni. Minden feature amit nem az email capture-höz kell, halasztható.

### **Felhasználói folyamat**

- 1\. Landing page - értékajánlat, CTA
- 2\. Form - kutatási téma + célcsoport megadása
- 3\. Email capture + 2 minősítő kérdés
- 4\. Feldolgozás - 10-15 persona párhuzamos API hívás
- 5\. Eredmény oldal - personák véleménye vizuálisan
- 6\. Automatikus email - eredmény PDF + következő lépés CTA

### **Technikai stack**

| **Komponens** | **Megoldás**                                        |
| ------------- | --------------------------------------------------- |
| Frontend      | Next.js - landing + form + eredmény oldal           |
| Backend       | FastAPI - API routing, job queue                    |
| AI engine     | Kimi K2 API (olcsóbb) vagy Claude Sonnet            |
| Email         | Resend vagy Mailchimp - capture + automation        |
| Adatbázis     | Supabase (PostgreSQL) - userek, query-k, eredmények |
| Hosting       | Vercel (frontend) + Railway (backend)               |

### **Persona engine - hogyan működik**

A persona engine nem különálló AI modellek gyűjteménye - ugyanaz az LLM API, N különböző system prompttal meghívva. Minden system prompt egy paraméteres sablon, amely a felhasználó által megadott célcsoport alapján generálódik.

|     | **Költség kalkuláció**<br><br>10 persona × 600 input + 200 output token = ~8 000 token/futás. Kimi K2 áron: \$0.60/M input + \$2.50/M output → ~\$0.002/futás. Napi 500 futás esetén \$1/nap - kezelhetően alacsony. |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

# **4\. Email capture stratégia**

Az email-t nem az eredmény után kell kérni - hanem előtte. Az emberek kíváncsiságát kell horgonyként használni. Az eredmény látásának vágya az erős motivátor, nem az utólagos regisztráció.

### **A két minősítő kérdés**

Regisztráció után, az eredmény előtt - kötelező, de rövid:

- "Milyen területen dolgozol?" (legördülő: marketing, termékfejlesztés, értékesítés, ügynökség, egyéb)
- "Mi a legnagyobb marketing kihívásod most?" (szabad szöveges, max 150 karakter)

A szabad szöveges válaszokat az első 200 feliratkozónál egyenként kell elolvasni. Ezekből jön ki az agent-alapú marketing ajánlat iránya.

### **Email automation flow**

- Azonnal (0 perc): Eredmény emailben, PDF export, branding
- 3\. nap: "Mit tanultál a szimulációból?" - engagement check
- 7\. nap: Case study email - hogyan használta valaki a platformot
- 14\. nap: Soft pitch - "dolgozunk valamin, érdekel egy korai hozzáférés?"

|     | **Fontos**<br><br>Az első 100 feliratkozónak küldj személyes emailt - ne automation, hanem te magad. Kérdezz rá a fájdalompontjaikra. Ez a legértékesebb adat ebben a fázisban. |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

# **5\. Go-to-market terv**

### **1\. hét - Pre-launch**

- Landing page és MVP fejlesztés párhuzamosan
- Waitlist oldal publikálása fejlesztés közben
- LinkedIn personal brand aktiválás: 3 poszt a szintetikus kutatás témában
- Direkt elérés: 20-30 ismert marketing szakember személyes üzenete

### **2\. hét - Launch**

- Product Hunt launch - kategória: Marketing, AI
- LinkedIn poszt a launch napján - demo giffel, eredmény screenshottal
- Hírlevél swap ajánlat 2-3 magyar marketing newsletter-nek
- Reddit: r/marketing, r/artificial (angol nyelvű) - organikus poszt

### **3-4. hét - Growth**

- Első 50 feliratkozó személyes emailje - fájdalompontok felmérése
- LinkedIn: heti 2 poszt "mit mondott az AI" formátumban (virális potenciál)
- Webinar: "Hogyan validálj terméket 48 óra alatt AI-jal" - ingyenes, 30 perc
- Referral mechanizmus: "Oszd meg 3 ismerőssel, kapsz prioritásos hozzáférést"

| **Csatorna**        | **Várt lead / hónap** |
| ------------------- | --------------------- |
| LinkedIn organic    | 150-300               |
| Product Hunt launch | 200-500 (egyszeri)    |
| Hírlevél swap       | 100-200               |
| Referral            | 50-150                |
| SEO (hosszabb táv)  | 50-100                |
| Összesen (1. hónap) | 550-1 250             |

# **6\. Finanszírozás és unit economics**

### **MVP fejlesztési költség (egyszeri)**

| **Tétel**                        | **Becsült költség** |
| -------------------------------- | ------------------- |
| Fejlesztési idő (saját munka)    | 0 Ft (opp. cost)    |
| Hosting - Vercel + Railway       | ~\$20/hó            |
| Supabase (ingyenes tier)         | \$0                 |
| Kimi API - első 10 000 futás     | ~\$20               |
| Resend email (10k email/hó free) | \$0                 |
| Domain + SSL                     | ~\$15 egyszeri      |
| Összesen (1. hónap)              | ~\$55               |

### **Skálázási küszöbök**

Az API költség az egyetlen változó kiadás. A modell-agnosztikus swarm executor lehetővé teszi a váltást:

- Kimi K2 - \$0.002/futás → 500 napi futás = \$1/nap = ~\$30/hó
- Claude Sonnet - \$0.02/futás → 500 napi futás = \$10/nap = ~\$300/hó
- Ha nő a forgalom: Kimi K2 az alapértelmezett, Claude opcionálisan prémium módban

|     | **Döntési pont**<br><br>Ha az email lista eléri az 500 főt és a minősítő kérdések alapján van kereslet a fizetős termékre, akkor érdemes a Pro tier bevezetéséről dönteni - ezzel az API költség fedezhetővé válik. |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

# **7\. Sikermetrikák és döntési pontok**

| **Metrika**                        | **4 hetes cél** | **8 hetes cél** |
| ---------------------------------- | --------------- | --------------- |
| Email feliratkozók                 | 500             | 1 500           |
| Nyitási arány (email)              | 35%+            | 30%+            |
| Futások száma/nap                  | 50+             | 200+            |
| Minősítő kérdés kitöltési arány    | 70%+            | 60%+            |
| Fájdalompont kategóriák azonosítva | 3               | 5               |
| Potenciális fizetős érdeklődők     | 20              | 80              |

### **Döntési fa - 4 hét után**

- Ha 500+ email ÉS van ismétlődő fájdalompont → agent marketing ajánlat fejlesztése indul
- Ha 500+ email DE nincs tiszta irány → mélyebb interjúk az első 50 feliratkozóval
- Ha 200 email alatt → launch csatorna újragondolása, LinkedIn stratégia erősítése
- Ha magas a futásszám DE alacsony az email capture → form pozíciójának újratervezése

# **8\. Kockázatok és mitigáció**

| **Kockázat**                              | **Mitigáció**                                                                              |
| ----------------------------------------- | ------------------------------------------------------------------------------------------ |
| AI output minősége gyenge magyar szövegen | Prompt finomhangolás magyar kulturális kontextussal; első 50 futást manuálisan ellenőrizni |
| Alacsony konverzió email capture-re       | A/B teszt az email kérés pozíciójával; értékajánlat szövegének tesztelése                  |
| API költség hirtelen megnő                | Hard limit beállítása (\$50/hó); Kimi K2 alapértelmezett modellként                        |
| Versenytárs hasonló terméket indít        | Közönség és bizalom nem másolható; az email lista a moat ebben a fázisban                  |
| Nem jön össze az agent marketing ajánlat  | A lista más ajánlatnak is értékes; rugalmas pivot lehetséges                               |

**Összefoglaló - a következő 2 hét**

| **Hét 1**           | Landing page + MVP fejlesztés + waitlist + LinkedIn aktiválás |
| ------------------- | ------------------------------------------------------------- |
| **Hét 2**           | Launch: Product Hunt + LinkedIn + első személyes üzenetek     |
| **Hét 3-4**         | Első feliratkozók interjúja + growth csatornák erősítése      |
| **Döntés (4. hét)** | Agent marketing ajánlat iránya a lista visszajelzése alapján  |
