# SwarmSense portfóliódarab: design

- **Dátum:** 2026-10-07
- **Állapot:** jóváhagyva (2026-10-07)
- **Forrás:** `2026-10-07 SwarmSense terv` (second-brain vault) és a 2026-10-07-i brainstorming
- **Ütemezés:** párhuzamosan fut a Portfólió kapujával (határnap 2026-12-01), a scope nincs vágva (Balázs döntése)

## 1. Cél

A SwarmSense freemium funnelből portfóliódarab lesz egyetlen kipróbálható flow-val: kérdés → 18 szintetikus persona → letölthető PDF. Regisztráció nincs. A darab a Homelabban fut a `swarmsense.growthframe.hu` címen, a repo nyilvános.

**Mit bizonyít**

- Főleg LLM-orchestrationt: 18 persona párhuzamos hívása 5-ös kerettel, retry, részleges hiba kezelése, validált strukturált kimenet. Ezt a néző **élő trace-en** látja, nem csak a README-ben olvassa.
- Másodsorban marketing-gondolkodást: a kérdésfeltevés, a personák és a szintézis szerkezete.

**Amit nem állít:** hogy kiváltja a valódi piackutatást. Az eredményoldal, a PDF és a módszertani oldal is kimondja.

**Siker:** a nyilvános oldalon egy idegen regisztráció nélkül végigvisz egy futást vagy megnézi a mintafutást, látja a trace-t, letölti a PDF-et; a kód nyilvános és titokmentes.

## 2. Mit lát a néző

1. Kitölt két mezőt: „Mit vizsgálsz?” és „Kinek szól?”.
2. Vagy egy kattintással megnyitja a mintafutást (`/minta`), amely egy rögzített futás trace-ét játssza vissza.
3. A várakozó képernyő élő trace: personánként állapot, kísérletszám, eltelt idő, tokenek.
4. Az eredményoldal (`/eredmeny/[id]`): összefoglaló, futásadatok, PDF letöltése, „Futás visszajátszása” link, e-mail-kérés, korlátok.
5. Ha megad egy e-mail-címet, megkapja a PDF-et levélben. Más levél nem megy.

## 3. Architektúra

```
Böngésző
   │  (csak ez nyilvános: swarmsense.growthframe.hu, Traefik)
   ▼
Next.js frontend ──────────────► FastAPI backend ──► Postgres
   Server Action: futás indítása,    (belső Dokploy-háló)     (belső háló)
                  e-mail-kérés           │
   Route handler: események, PDF         ├──► opencode Go (LLM)
                                         ├──► Resend (PDF e-mailben)
                                         └──► Discord webhook (értesítés)
```

- **A backend kívülről nem érhető el.** A böngésző csak a Nexttel beszél; emiatt a CORS megszűnik.
- **Server Action** az egyszeri műveletekre (futás indítása, e-mail-kérés). **Route handler** arra, amit a böngésző ismételten lekér vagy fájlként letölt:
  - `GET /api/runs/[id]/events?after=<id>` → a backend eseményvégpontja
  - `GET /api/runs/[id]/pdf` → a backend PDF-végpontja
- **`X-Internal-Secret`** marad a backend írási végpontjain a belső hálón is.
- **Kliens IP:** a Next a Traefiktől kapott címet fejlécben adja tovább; a backend csak érvényes `X-Internal-Secret` mellett fogadja el.
- **A futás** a backend folyamatában, háttérfeladatként megy (`BackgroundTasks`, külön szál, saját event loop). Ez nem változik.

### Egy futás útja

1. Az űrlap Server Actiont hív → backend `POST /api/v1/runs`. A backend ellenőrzi a kereteket, létrehozza a `runs` sort, elindítja a háttérfeladatot.
2. Az engine minden állapotváltásnál sort ír a `run_events` táblába.
3. A várakozó képernyő 1 mp-enként lekéri az új eseményeket.
4. Personák → szintézis → eredmény mentése (`runs.result`) → PDF mentése (`runs.pdf`) → `completed`.
5. A képernyő átirányít az eredményoldalra.

A kombinált `POST /run-sessions` végpont a qualifier kiesésével értelmét veszti; egyetlen `POST /runs` marad.

## 4. Adatmodell

Egyetlen `backend/schema.sql`, amit a backend induláskor futtat (`create table if not exists`). Migrációs eszköz és adatmigráció nincs. ORM nincs: `psycopg` 3 nyers SQL-lel, minden lekérdezés a `backend/app/db.py` modulban, függvényenként egy művelet.

| Tábla | Oszlopok | Megjegyzés |
|---|---|---|
| `runs` | `id uuid` (véletlen), `topic`, `audience`, `status`, `persona_count`, `created_at`, `completed_at`, a meglévő szintézis-oszlopok, `result jsonb`, `pdf bytea`, `is_sample bool`, `ip_hash text`, `input_tokens int`, `output_tokens int` | Kiesik: `user_id`, `cost_usd`, `day1/3/7_sent` |
| `run_events` | `id bigserial`, `run_id`, `type`, `persona_index`, `persona_name`, `attempt`, `error_code`, `duration_ms`, `input_tokens`, `output_tokens`, `created_at` | Csak beszúrás. Az `id` a polling kurzora. |
| `email_requests` | `id`, `run_id`, `email`, `created_at`, `sent_at` | 14 nap után törlődik |

- **`result`:** a `_build_result_payload` kimenete (állásfoglalások, konszenzus, top érvek, personák, szintézis). Az eredményoldal és a PDF is ebből dolgozik.
- **`ip_hash`:** az IP és egy szerveroldali titok HMAC-je. Nyers IP nem tárolódik.
- **Nincs `cost_tracking`:** a havi összesítés, a hard cap, a `cost_enforcement.py` middleware és az `increment_monthly_cost` függvény törlődik.
- **Megőrzés:** a futás, az események és a PDF korlátlan ideig megmarad; a futás linkje nem jár le. Csak az e-mail-cím törlődik.

## 5. Események

| `type` | Mikor | Kitöltött mezők |
|---|---|---|
| `run_started` | a feldolgozás elindul | – |
| `personas_generated` | megvan a 18 persona-leírás | `duration_ms`, tokenek |
| `persona_started` | a persona bejut az 5-ös keretbe | `persona_index`, `persona_name` |
| `persona_retry` | egy kísérlet elbukott, újrapróbál | + `attempt`, `error_code` |
| `persona_completed` | érvényes válasz jött | + `attempt`, `duration_ms`, tokenek |
| `persona_failed` | kiesett | + `attempt`, `error_code`, `duration_ms` |
| `synthesis_started`, `synthesis_completed` | a szintézis hívása | `duration_ms`, tokenek |
| `run_completed`, `run_failed` | vége | – |

- „Sorban áll” állapotra nincs esemény: a `personas_generated` után minden persona sorban áll, amíg nem jön róla `persona_started`. A kliens számolja.
- Hibáról csak `error_code` megy ki, a szolgáltató nyers üzenete nem.

**Polling válasz**

```json
{
  "status": "running",
  "is_sample": false,
  "events": [
    {"id": 41, "type": "persona_retry", "persona_index": 7,
     "persona_name": "Kovács Anna", "attempt": 2,
     "error_code": "RATE_LIMITED", "at": "2026-10-07T12:00:03Z"}
  ]
}
```

A kliens a legnagyobb kapott `id`-t küldi vissza `after`-ként.

**Változás a kódban**

- `persona_engine.py`: az `on_persona_completed(kész, összes)` callback helyett általános `on_event(esemény)`.
- `llm_client.py`: a `_request_with_retry` ciklus opcionális `on_retry` callbacket kap; a válasz `usage` mezőjéből tokenszámot ad vissza költség helyett.
- `run_processor.py`: az eseményeket a `db.py`-n át írja; a Supabase- és Sentry-hívások kikerülnek.

## 6. LLM-szolgáltató

- **opencode Go**, az Ajánlatkészítő mintájára: `https://opencode.ai/zen/go/v1/chat/completions`, OpenAI-kompatibilis kérés, modell `deepseek-v4.1-flash`.
- Kötelező fejléc: `x-opencode-session: swarmsense-<run_id>` (enélkül 400).
- Kötelező saját `User-Agent` fejléc is (pl. `swarmsense/<verzió>`): a Python alapértelmezett `User-Agent`-jét a szolgáltató előtti Cloudflare 403-mal (1010) elutasítja. Mérve 2026-10-07.
- A modell gondolkodó modell: a válaszban `reasoning_content` is jön, és a kimeneti tokenek nagy része gondolkodás. A kliens csak a `content`-et dolgozza fel; a tokenszám a `usage` mezőből jön.
- **Tokenszámlálás:** az a persona-hívás is beleszámít, amely válaszolt, de a válasza a séma szerint érvénytelen volt (a tokeneket a szolgáltató ettől még elszámolta). Az érvénytelen blueprint vagy szintézis válaszának tokenjei nem számítanak bele, mert az a hívás nem jut tovább.
- A `config.py` `openrouter_*` mezőiből `llm_*` lesz, az osztályból `LLMClient`. A nem használt `kimi_api_key` törlődik.
- **Költség:** a trace és az eredményoldal tokenszámot mutat, mellette a DeepSeek listaárából számolt becslést, becslésként jelölve. Az ár egy konstans a kódban.
- **Ismert függés:** a demó Balázs napi munkaeszközének keretét használja. Ezt a globális napi futáskeret korlátozza (7. szakasz).

## 7. Keretek

Futás indítása előtt, ebben a sorrendben. Az értékek környezeti változók; a véglegeseket a kimérő futás után rögzítjük.

| Keret | Kiinduló érték | Ha betelt |
|---|---|---|
| Bemenet hossza | mezőnként 500 karakter | Űrlaphiba |
| Egyszerre futó futások | 2 | „Most foglalt, próbáld újra egy perc múlva” |
| IP-nként 24 óra alatt | 3 futás | Üzenet, link a mintafutásra |
| Összesen 24 óra alatt | 20 futás | Üzenet, link a mintafutásra |
| Levél futásonként | 3 | A gomb letiltva |
| Levél összesen 24 óra alatt | 30 | Üzenet; a letöltés működik |

- Gördülő 24 óra (`created_at > now() - interval '24 hours'`), nem naptári nap.
- A sikertelen futás is beleszámít. A mintafutás megnézése nem.
- A keretek egy-egy `count` lekérdezés; zárolás nincs, két egyidejű kérésnél a keret eggyel túlléphető. Ez elfogadott.

## 8. Trace képernyő és visszajátszás

**Elrendezés:** fejléc (kérdés, futó óra, négy fázis: personák generálása → 18 persona → szintézis → PDF), összesítő sor (állapotonkénti darabszám, tokenek, becsült költség), alatta 18 sor (név, állapot, eltelt idő, kísérlet `n/3`, hibánál a hibakód). Mobilon egy oszlop.

**Állapotkezelés**

- Egy tiszta függvény: `applyEvent(állapot, esemény) → új állapot`. A komponens csak kirajzol.
- A futó óra a kliensen számol az esemény időbélyegétől.
- Ha a polling megszakad, az utolsó állapot kint marad; három egymás utáni hiba után hibaüzenet és link a mintafutásra.

**Visszajátszás**

- A mintafutás közönséges `runs` sor `is_sample = true` jelöléssel, valódi eseményekkel.
- A `/minta` oldal és az eredményoldal „Futás visszajátszása” linkje ugyanazt a komponenst használja: a kliens egyben megkapja az eseményeket, és az időbélyegek különbsége szerint, eredeti tempóban adagolja az `applyEvent`-nek.
- Felül címke („Rögzített futás, dátum”) és „Ugrás az eredményre” gomb.
- A mintának tartalmaznia kell valódi retry-t és legalább egy kiesett personát. Nem hamisítjuk; addig futtatunk, amíg előfordul.
- A minta SQL-fájlként a repóban van (`backend/seed/sample_run.sql`); a backend induláskor betölti, ha nincs megjelölt minta.

## 9. Eredményoldal, PDF, e-mail

**Eredményoldal:** fejléc → összefoglaló és az állásfoglalások megoszlása → futásadatok (idő, tokenek, becsült költség, `n/18` persona, retry-k száma) és visszajátszás-link → PDF letöltése → e-mail-kérés → „Mire nem jó” és link a módszertani oldalra. A personák részletes válaszai csak a PDF-ben vannak.

**PDF**

- Tartalom: címlap → konszenzus és top érvek → szintézis → personák egyenként → hogyan futott → módszertan és korlátok.
- Jinja2 sablon → HTML → Playwright (Chromium) → A4 PDF, a `runs.pdf` oszlopba.
- A böngésző PDF-enként indul és áll le, mert a futás saját event loopban megy, és egy Playwright-böngésző csak a saját loopjából használható.
- A konténer tartalmaz egy fontfájlt a magyar ékezetekhez.
- Ha a PDF nem készül el, a futás `completed` marad; a letöltő végpont első kérésre újrapróbálja.
- A tartalom kétszer létezik (React-oldal és Jinja-sablon). Ez vállalt duplikáció; a Next-oldal nyomtatása visszahozná a backend → frontend függést.

**E-mail**

- Server Action → `POST /runs/{id}/email` → `email_requests` sor → Resend, a PDF csatolva → `sent_at`.
- Rövid sima HTML levél: a kérdés, az eredménylink, és hogy a levelet az oldalon kérték.
- Feladó: `swarmsense@growthframe.hu`.
- A React Email sablonok és a három render-route törlődik.

**Óránkénti takarítás:** háttérfeladat a FastAPI `lifespan`-ben. Törli a 14 napnál régebbi `email_requests` sorokat, és `failed`-re állítja a 10 percnél régebben `running` futásokat.

**Adatkezelési tájékoztató:** újraírva. Kimondja, hogy a kérdés szövege megmarad (ne írjanak bele személyes adatot), az e-mail-cím 14 nap után törlődik nálunk, a Resend saját naplója ettől független, és a kérdés szövege az opencode-on át a DeepSeekhez kerül.

## 10. Hibakezelés

| Mi történik | Rendszer | Néző |
|---|---|---|
| Egy persona kiesik | A futás megy tovább | Trace: „kiesett”; eredmény: „16/18 persona válaszolt” |
| 12-nél kevesebb persona válaszol (`MIN_SUCCESSFUL_PERSONAS`) | `failed` | Hibaoldal, link a mintafutásra |
| A persona-generálás elbukik | `failed` | Ugyanaz |
| A szintézis elbukik | `partial`, az eredmény szintézis nélkül készül el | Eredmény és PDF a szintézis-rész nélkül, jelezve |
| Az opencode-keret elfogyott | A hívások hibáznak, `failed` | Hibaoldal, link a mintafutásra |
| A backend futás közben újraindul | A takarító 10 perc után `failed`-re állítja | A trace megáll, majd hibaoldal |
| Keret betelt | `429` hibakóddal | A 7. szakasz szerinti üzenet |

- A backend hibakódot ad, a szövegek a `frontend/lib/messages.ts`-ben vannak.
- **Sentry kikerül** (backend SDK, frontend config fájlok, `test_sentry.py`).
- **Napló:** szabványos kimenet, futásonként egy összefoglaló sor (azonosító, státusz, idő, tokenek, kiesettek). E-mail-cím nem kerül a naplóba. Hibánál a napló csak a futás azonosítóját, a kivétel típusát és a hibakódot tartalmazza, kivételszöveget és tracebacket soha (egy láncolt validációs hiba kiírhatná az LLM kimenetét). A `swarmsense` logger az `app/main.py`-ban kap egy minimális beállítást (INFO szint, egy `StreamHandler` a standard hibakimenetre, ismételt híváskor nem duplázódik), különben az uvicorn alatt az INFO sorok elvesznének.
- **Discord-értesítés** webhookon: ha egy futás `failed`, és ha betelt az összesített napi keret. Tartalma futásazonosító, hibakód, link; a kérdés szövege nem. Ha a webhook-változó üres, nincs értesítés; ha a Discord nem elérhető, a hiba a naplóba kerül.
- **Elérhetőség:** az Uptime Kuma figyeli a `/api/v1/status` végpontot.
- **Operator endpointok nincsenek.** Helyettük `docs/lekerdezesek.md` három SQL-lekérdezéssel (mai futások státusz szerint, napi tokenösszeg, leggyakoribb hibakódok).

## 11. Mi törlődik

- **Backend:** magic link auth, qualifier, waitlist, unsubscribe, follow-up levelek, e-mail-metrikák, operator endpointok, consent- és adattörlő service, az „egy e-mail, egy futás” korlát, `cost_enforcement.py`, `run_sessions.py`, Sentry, a Supabase-kliens.
- **Frontend:** a `blocked`, `pro`, `qualifier`, `verify`, `research/email`, `research/sent` oldalak, a három e-mail-renderelő route, a React Email sablonok, a Sentry config, a Plausible szkript (`app/layout.tsx`); webanalitika nincs.
- **Séma:** `users`, `magic_link_tokens`, `qualifier_responses`, `waitlist`, `cost_tracking`.
- **Tesztek:** a kieső kód tesztjei (13 fájl).
- **Repo:** `_bmad`, `_bmad-output`, `.cursor`, `.opencode`, `.agent`, `.agents`, `supabase/`, `skills-lock.json`, a `docs/` régi fájljai, `.github/workflows/deploy.yml`, `.github/workflows/supabase-migrations-draft.yml`, `docker-compose.swarmsense-backend.yml`.

## 12. Tesztelés

| Réteg | Mit | Hogyan |
|---|---|---|
| `db.py`, keretek, események, e-mail-kérés, takarítás | A valódi SQL | pytest valódi Postgres ellen; séma a tesztek előtt, táblák ürítése tesztenként. CI-ban service container, helyben Docker. |
| Engine, LLM-kliens | Párhuzamosság, retry, kiesés, eseménysorrend | Hamis transport (a kliens már támogatja); valódi hívás nincs |
| PDF | Elkészül, és érvényes PDF | Füstteszt valódi Chromiummal |
| Frontend | `applyEvent`, visszajátszás időzítése, route handlerek, űrlap | vitest |
| Teljes folyamat | Űrlaptól a levélig | Kézi ellenőrzőlista deploy után |

- Megmarad kis módosítással: `test_llm_client.py`, `test_persona_engine.py`.
- Újraírandó: `test_run_processor.py`, `test_runs.py` (a `FakeQuery` osztályaik a Supabase API-ját utánozzák).

## 13. Deploy és publikálás

**Deploy**

- Egy compose fájl három szolgáltatással (frontend, backend, Postgres kötettel) a Dokployon; Traefik-címet csak a frontend kap.
- A backend image a hivatalos Playwright Python image-re épül.
- A helyi fejlesztői `docker-compose.dev.yml` rögzített projektnevet kap (`swarmsense-dev`), hogy ne függjön a mappa nevétől és ne ütközzön más projektek konténereivel.
- A CI marad, kiegészül a Postgres service containerrel és a Chromium telepítésével.
- Adatbázis-mentés nincs; a mintafutást a seed fájl pótolja.
- A régi deploy lekapcsolása a végén.

**Publikálás**

1. Minden régi kulcs cseréje vagy törlése, feltétel nélkül (Supabase projekt, OpenRouter, Resend, operator kulcs, internal secret).
2. A történet átvizsgálása `gitleaks`-szel.
3. **Tiszta történet:** a régi történet git bundle-be mentve, a nyilvános repo új történettel indul.
4. LICENSE, README (mit mutat a demó, hogyan működik, miben tér el az élestől, ismert korlátok).

## 14. Építési sorrend

Nyolc lépés, három implementációs tervben. Egyszerre mindig csak a következő terv van megírva, mert a 0. lépés mérései a későbbi részleteket módosíthatják. Minden terv végén működő, megszakítható állapot van. A haladást a `TRACKING.md` követi.

| Terv | # | Lépés |
|---|---|---|
| nincs terv (mérés) | 0 | Kideríteni, hol fut most élesben; kimérő futás az opencode Go-n |
| **A: Új alap** | 1 | Törlés (backend, frontend, tesztek, Sentry) |
| | 2 | Postgres, `db.py`, LLM-kliens átállítása, tesztek valódi Postgresen |
| **B: A darab** | 3 | Események, trace képernyő, keretek |
| | 4 | Eredmény tárolása, eredményoldal, PDF |
| | 5 | E-mail, takarító feladat, Discord, adatkezelési szöveg, módszertani oldal |
| | 6 | Mintafutás, visszajátszás, seed |
| **C: Kiadás** | 7 | Deploy, régi lekapcsolása |
| | 8 | Publikálás |

## 15. Amit a 0. lépés kimér

Ezek ma feltételezések; a kimérő futás dönti el őket.

| Kérdés | Mit érint |
|---|---|
| Ad-e az opencode Go `usage` mezőt tokenszámmal? | Token- és költségkijelzés (6., 8., 9. szakasz) |
| Mennyi egy futás ideje és tokenszáma? | Polling gyakorisága (10 mp alatti futásnál 500 ms), a napi keret értéke |
| Átmegy-e 5 (és 10) párhuzamos hívás egy kulcsról? | A párhuzamossági keret és az egyidejű futások kerete |
| Hogyan jelzi a keret kimerülését (429, 402, más)? | A retry szabálya: keretkimerülést nem szabad újrapróbálni |
| Támogatja-e a `response_format: json_object` beállítást? | A strukturált kimenet validálása |
| Hol fut most élesben a SwarmSense? | Mit kell lekapcsolni a 7. lépésben |

## 16. Ismert kockázatok

- **Scope:** a Portfólió kapuja 3/4 kész · 0/4 kint. Ez a darab többnapos munka mellette. A lépésenkénti terv teszi megszakíthatóvá.
- **Közös LLM-keret:** ha a keretek rosszul vannak beállítva, a demó Balázs napi munkaeszközét állítja le.
- **Megmaradó kérdésszöveg:** korlátlan ideig tárolódik, és a link birtokában bárki látja. Az űrlap figyelmeztet, de semmi nem ellenőrzi.
- **Tárhely:** a PDF-ek az adatbázisban gyűlnek. A napi 20 futás korlátozza; a PDF mérete még nem ismert.
- **E-mail mint spam-eszköz:** a link birtokában bármilyen címre küldhető levél. A futásonkénti és a napi levélkeret korlátozza, nem szünteti meg.
- **opencode Go felhasználási feltételei:** a szolgáltatás kódoló ügynökökre készült; a nyilvános demó ettől eltérő használat. Az Ajánlatkészítőnél ez elfogadott döntés volt, itt futásonként kb. 20 hívással nagyobb a terhelés.
