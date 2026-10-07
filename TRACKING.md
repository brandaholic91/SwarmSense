# Haladás

A cél és a teljesítési kritériumok a `CLAUDE.md`-ben, a részletek a `docs/superpowers/specs/2026-10-07-swarmsense-portfolio-design.md` specben vannak. Ez a fájl csak azt rögzíti, hol tartunk.

**Most:** a B terv (a darab) kész és le van zárva: a kód helyben végig van ellenőrizve valódi futásokkal (2026-10-07), a tesztek a seed fájl mellett is zöldek. Két dolog maradt nyitva: (1) a rögzített mintafutásban nincs szintézis, Balázs dönt, hogy így jó-e, vagy új mintát rögzítünk; (2) a levél tényleges kézbesítése nincs ellenőrizve. Utána a C terv (kiadás) jön.

## Lépések

| Terv | # | Lépés | Állapot |
|---|---|---|---|
| nincs terv | 0 | Hol fut most élesben; kimérő futás az opencode Go-n | kész, két nyitott ponttal |
| A: Új alap | 1 | Törlés | kész |
| | 2 | Postgres, `db.py`, LLM-kliens, tesztek | kész |
| B: A darab | 3 | Események, trace képernyő, keretek | kész |
| | 4 | Eredmény tárolása, eredményoldal, PDF | kész |
| | 5 | E-mail, takarítás, Discord, adatkezelés, módszertan, landing oldal | kész, egy nyitott ponttal (a levél kézbesítése és a Discord-értesítés élesben nincs ellenőrizve) |
| | 6 | Mintafutás, visszajátszás, seed | kész, egy nyitott ponttal (a mintában nincs szintézis) |
| C: Kiadás | 7 | Deploy, régi lekapcsolása | nincs elkezdve |
| | 8 | Publikálás | nincs elkezdve |

Állapotok: nincs elkezdve · folyamatban · kész.

## Implementációs tervek

| Terv | Fájl | Állapot |
|---|---|---|
| A | `docs/superpowers/plans/2026-10-07-swarmsense-a-uj-alap.md` | kész |
| B | `docs/superpowers/plans/2026-10-07-swarmsense-b-a-darab.md` | kész |
| C | még nincs megírva | a B terv után |

## A 0. lépés mérései

| Kérdés | Eredmény |
|---|---|
| Ad-e az opencode Go `usage` mezőt tokenszámmal? | **Igen.** `prompt_tokens`, `completion_tokens`, `total_tokens`, részletezve `cached_tokens` és `reasoning_tokens`. Költségmező nincs. |
| Egy futás ideje és tokenszáma | **86 mp, kb. 51 000 token** (20 hívás, 5 párhuzamos). Persona-generálás 15 mp / 2 200 token; 18 persona 59 mp / 42 900 token (hívásonként 8–24 mp, medián 14); szintézis 13 mp / 5 600 token. A kimeneti tokenek nagy része gondolkodás. Az 1 mp-es polling marad. Egy mérés, egy témával. |
| Átmegy-e 5, illetve 10 párhuzamos hívás egy kulcsról? | **Igen, mindkettő**, 429 nélkül (39 hívásból 39 HTTP 200). 10 párhuzamossal a 18 persona 38 mp. A 10-es körben 2 persona válasza nem felelt meg a sémának; az ok nincs kivizsgálva, és egy mérésből nem dönthető el, hogy a párhuzamosság okozta-e. |
| Hogyan jelzi a keret kimerülését? | **Nincs kimérve**, a keretet nem merítettük ki. Nyitott; addig a kliens a 429-et újrapróbálja, a többi 4xx-et nem. |
| Támogatja-e a `response_format: json_object` beállítást? | **Elfogadja**, és 39 válaszból 39 feldolgozható JSON volt. Az nincs igazolva, hogy a szolgáltató ki is kényszeríti; a séma szerinti validálás marad. |
| Hol fut most élesben a SwarmSense? | **Részben tisztázva (2026-10-07).** A `swarmsense.hu` él (HTTP 200, Next.js, Cloudflare mögött, nem Vercel); a `swarmsense.vercel.app` 404, a `swarmsense.growthframe.hu`-nak nincs DNS-rekordja. A backend deploy (`deploy.yml`, Hetzner) utoljára 2026-04-23-án futott, hibával; az utolsó sikeres 2026-03-26. Nyitott: melyik gépen van a frontend és a backend origin (a Cloudflare eltakarja), ezt a Cloudflare DNS-ből vagy a gépekről kell megnézni. |

## Eltérések a spectől

Ha építés közben valami másképp alakul, mint a specben, ide kerül egy sor (dátum, mi, miért), és a spec is frissül.

| Dátum | Mi változott | Miért |
|---|---|---|
| 2026-10-07 | A spec 6. szakaszába bekerült a kötelező saját `User-Agent` fejléc és a `reasoning_content` | A 0. lépés mérése: az alapértelmezett Python `User-Agent`-re 403 (Cloudflare 1010) jön |
| 2026-10-07 | A spec 11. szakaszába bekerült a Plausible és a `supabase-migrations-draft.yml` törlése | Balázs döntése (Plausible); a workflow a `supabase/` mappával együtt értelmét veszti |
| 2026-10-07 | A `docker-compose.dev.yml`-nek rögzített projektneve van: `swarmsense-dev` (spec 13. szakasz, frissítve) | A mappanévtől függő név ütközött volna más projektek konténereivel |
| 2026-10-07 | Annak a persona-hívásnak a tokenjei is beleszámítanak, amely válaszolt, de a séma szerint érvénytelen volt; az érvénytelen blueprint és szintézis válaszának tokenjei nem (spec 6. szakasz, frissítve) | A persona-hívás költsége valós, a másik kettőnél a hibás válasz nem jut tovább, és nem vesz részt az összesítésben |
| 2026-10-07 | A futásnapló nem tartalmaz kivételszöveget vagy tracebacket, csak futásazonosítót, kivételtípust és hibakódot (spec 10. szakasz, frissítve) | Egy láncolt validációs hiba kiírta az LLM kimenetét a naplóba |
| 2026-10-07 | Az adatkezelési és a felhasználási feltételek szövege még a régi e-mailes folyamatot írja le, a nyitóoldali statisztika még „90 másodperc”; a B tervben íródik újra | Az A terv csak az alapot cseréli; a szövegek a B terv 5. lépéséhez tartoznak |
| 2026-10-07 | Új esemény: `synthesis_failed` (`error_code`, `duration_ms`, tokenek); a `completed` és `partial` futás is `run_completed`-del zárul (spec 5. szakasz, frissítve) | A trace-nek látnia kell, hogy a szintézis elbukott, de a futás eredménnyel ér véget |
| 2026-10-07 | A `run_failed` esemény `error_code`-ot hordoz (`PERSONA_GENERATION_FAILED`, `TOO_FEW_PERSONAS`, `INTERNAL_ERROR`) (spec 5. szakasz, frissítve) | A hibaoldal a kódból választ üzenetet; nyers szöveg nem megy kifelé |
| 2026-10-07 | A persona-leírások száma pontosan 18: a többletet levágjuk, a hiányt hibának vesszük (spec 5. szakasz, frissítve) | A trace és a keretek 18 personára épülnek; a modell néha többet ad |
| 2026-10-07 | A `swarmsense` logger minimális beállítást kapott az `app/main.py`-ban (INFO, egy `StreamHandler`), így a futásonkénti összefoglaló sor uvicorn alatt is látszik (spec 10. szakasz, frissítve) | A valódi futásnál derült ki, hogy nincs naplózási beállítás, ezért az INFO sorok elvesztek; javítva, a javítás utáni láthatóságot egy próbasorral ellenőriztük, valódi futással nem |
| 2026-10-07 | A landing oldal újraírása bekerült a B terv 5. lépésébe (spec 14. szakasz, frissítve) | Balázs döntése; a spec eddig egyik lépéshez sem rendelte, a mostani szövegben hamis állítások vannak („90 másodperc", „15-20 persona") |
| 2026-10-07 | A spec 3. szakasza: minden `/api/v1/runs…` végpont `X-Internal-Secret`-et kér, nem csak az írásiak | Az eseményvégpont a futás témáját adja vissza, ezért nem lehet nyitott; a CORS és a `frontend_origin` beállítás megszűnt |
| 2026-10-07 | A spec 5. szakasza: a polling válasz kiegészült `topic`, `created_at` és `price` mezőkkel; az ár a csúcsidős listaár (0,30 / 1,20 USD / 1M token, forrás a `pricing.py`-ban) | A kijelzőnek kell a téma és a költségbecslés; az ár idősávos, a felső érték a konzervatív becslés |
| 2026-10-07 | A spec 8. szakasza: a seed fájl nem tartalmaz PDF-et és `ip_hash`-t; a minta PDF-jét az első letöltés generálja | A fájl nyilvános repóba kerül, és egy PDF nagy, bináris tartalom lenne az SQL-ben |
| 2026-10-07 | A trace minden personasora a saját hívásának tokenjeit is mutatja („be 690 · ki 1 219 token”; futó sornál gondolatjel). A B terv `PersonaRow` típusából ez kimaradt; a spec 8. szakaszának elrendezés-leírása a sorban nem említ tokent, a 2. szakasz és a teljesítési kritérium viszont igen | A kritérium personánkénti tokent kér; az esemény (`persona_completed` / `persona_failed`) eddig is hordozta az értéket |
| 2026-10-07 | A szintézis válaszában az ismeretlen kulcsot eldobjuk, nem utasítjuk el; az öt kért kulcs és a típusuk továbbra is kötelező. A persona- és a blueprint-válasz ellenőrzése nem változott | Mért hiba: a modell időnként visszaírja a kérés `response_format` mezőjét (`"type": "json_object"`) a válasz elejére, és a szigorú séma emiatt egy egyébként teljes szintézist dobott el |
| 2026-10-07 | A futásidőről szóló állítás a nyitóoldalon, az űrlapon és a módszertani oldalon „másfél perc”-ről „másfél-két perc”-re változott (a spec nem rögzít időtartamot) | Mérés: a végigment valódi futások 86–132 mp-ig tartottak, retry nélkül is 86–126 mp-ig |
| 2026-10-07 | A seed fájl egyetlen SQL-utasítás: az események csak akkor kerülnek be, ha a futás sorát ugyanez a végrehajtás szúrta be | Ha a minta azonosítója közönséges futásként már megvolt (fejlesztői adatbázis), minden backend-indulás újra hozzáfűzte az eseményeket |
| 2026-10-07 | A beragadt futásokat a takarító percenként zárja le, a lejárt e-mail-kéréseket óránként törli (a spec 9. szakasza „óránkénti takarítás”-t mondott; frissítve) | A backend újraindulása után árván maradt futás az indulási körben még túl fiatal, a következő vizsgálat egy óra múlva jött, és a `count_active_runs` addig számolta: két árva futás ~70 percre minden látogatónak BUSY-t adott |

## Megfigyelések a valódi futásból

- A kérdés szövege egyszer megjelent a Next fejlesztői szerver naplójában a Server Action nyomvonalán (fejlesztői mód; éles buildnél nincs ellenőrizve).
- A böngésző fülében a polling megállt, amíg a fül a háttérben volt (az ok nincs megerősítve; a B terv lecseréli a pollingot).
- A PDF mérete: 40 977 bájt (kb. 40 KB), 8 oldal, 17 persona + szintézis. Ez a tesztek `make_run` adatával készült, rövid mesterséges szövegekkel, nem valódi futásból; valódi (hosszabb) personaszövegekkel nagyobb lesz. A betűtípus (IBM Plex Sans, két TTF) a PDF-be részhalmazként ágyazódik, a `runs.pdf` mérete így nem a fontfájlokkal nő. A valódi futások PDF-jének mérete lejjebb, a B terv záró ellenőrzésénél van.

## A B terv záró ellenőrzése (2026-10-07)

Helyben, éles frontend builddel (`next start`, 3001-es port), valódi headless Chromiummal (Playwright) végigvíve. Összesen nyolc valódi futás indult a megengedett nyolcból (öt az ellenőrzéshez és a mintához, három a szintézis javítása után), és hat különálló diagnosztikai szintézis-hívás (kettő az első körben, négy a hiba kivizsgálásához).

| Futás | Státusz | Idő | Bemeneti / kimeneti token | Retry | Kiesett | Szintézis | PDF |
|---|---|---|---|---|---|---|---|
| 1. `b91a8284` | `partial` | 86,3 mp | 12 870 / 37 443 | 0 | 1 | elbukott | 57 305 bájt, 11 oldal |
| 2. `19bbb63b` | `failed` (`RUN_TIMED_OUT`) | szándékosan megszakítva a persona-fázisban | 745 / 2 789 az eseményekben; a `runs` sorban 0 / 0 | 0 | 0 | nem jutott el odáig | nincs |
| 3. `97a492b0` | `partial` | 114,7 mp | 12 761 / 32 863 | 1 | 0 | elbukott | 57 434 bájt |
| 4. `8dbff746` | `partial` | 131,7 mp | 13 145 / 38 190 | 2 | 1 | elbukott | 56 182 bájt |
| 5. `8cb0819b` | `completed` | 92,2 mp | 16 816 / 38 564 | 0 | 0 | elkészült | 59 709 bájt |
| 6. `38be037d` | `completed` | 117,8 mp | 16 815 / 35 496 | 0 | 0 | elkészült | 59 604 bájt |
| 7. `21eaddf4` | `completed` | 105,7 mp | 16 606 / 37 330 | 0 | 0 | elkészült | 58 300 bájt |
| 8. `6373848b` | `completed` | 126,3 mp | 16 570 / 41 039 | 0 | 0 | elkészült | 60 245 bájt |

A 3. és a 4., illetve a 6. és a 7. futás egyszerre ment (ez a keret szerint megengedett); a többi egyedül. A 6–8. futás a szintézis javítása után indult, közvetlenül a `POST /api/v1/runs` végponton, azzal a céllal, hogy legyen olyan minta, amelyben szintézis, retry és kiesett persona is van; egyikben sem volt retry vagy kiesett persona.

**Mi igazolódott**

- A böngésző hálózati forgalmában csak a Next címe szerepel: az 1. futás teljes útján (űrlap → trace → eredmény → PDF → e-mail-űrlap → visszajátszás) 120 kérés ment, mind a `localhost:3001`-re; a 8000-es portra egy sem.
- A trace personánként állapotot, eltelt időt, kísérletszámot és a persona hívásának tokenjeit mutatja, hibánál a hibakódot; az összesített tokenek és a becsült költség az összesítő sorban vannak. A soronkénti tokenkijelzés az ellenőrzés után került be; a minta visszajátszásán, böngészőben megnéztük (pl. „kész | 0:10 | kísérlet 1/3 | be 690 · ki 1 219 token”, futó sornál gondolatjel, a kiesett sornál is ott a token). Másodpercenkénti mintavétellel a „fut” érték egyik futásban sem ment 5 fölé.
- A PDF a futás saját szálából és event loopjából indított Chromiummal elkészül: mind a négy végigment futásnál megvolt a `runs.pdf` a futás végére, a naplóban PDF-hiba nélkül. A letöltött PDF megnyílik, az ékezetek (ő, ű) helyesek.
- A futás összefoglaló sora megjelenik a backend naplójában (`run … finished: status=… elapsed=… input_tokens=… output_tokens=… dropped_personas=…`).
- **A Next naplója éles buildnél nem tartalmazza a kérdés szövegét.** A teljes ellenőrzés alatt a `next start` naplója csak az indulási sorokat tartalmazta; a backend naplójában sincs kérdésszöveg vagy titok. A C tervben ezzel nincs teendő, hacsak a deploy nem fejlesztői módban fut.
- Keretek: IP-keret és napi keret a megfelelő üzenettel és linkkel a mintára; egyidejűségi keret üzenettel, link nélkül (a spec 7. szakasza szerint). Futásonkénti levélkeretnél a mező és a gomb letiltva; napi levélkeretnél üzenet. A levélkereteket helykitöltő Resend-beállítással és SQL-lel beszúrt sorokkal néztük meg, levél nem ment ki.
- Beragadt futás: a persona-fázisban megölt backend és 11 perccel visszaállított `created_at` után az újrainduló backend takarítója `failed`-re állította a futást, a nyitva hagyott trace oldal pedig hibapanelre váltott („A futás megszakadt, mielőtt elkészült volna.”), linkkel a mintára és az űrlapra.
- Kiesett persona és elbukott szintézis valódi futásban is előfordult, és a spec 10. szakasza szerint viselkedett (trace: „kiesett” a hibakóddal; eredmény: „17/18 persona válaszolt”; az eredményoldal és a PDF jelzi, hogy a szintézis nem készült el).
- Takarítás adaton: egy SQL-lel beszúrt 15 napos `email_requests` sor a backend indulásakor törlődött, a mellette lévő 13 napos megmaradt.
- A seed üres adatbázison: egy frissen létrehozott, üres adatbázisra indított backend betöltötte a mintát (`is_sample`, `ip_hash` és PDF nélkül, 43 esemény); a `/minta` végigjátszotta (131 mp, benne két retry és egy kiesett persona), az „Ugrás az eredményre” az eredményoldalra vitt, a PDF első kérésre 0,6 mp alatt legenerálódott (56 181 bájt).

**A minta:** a 4. futás (`8dbff746`), az első és egyetlen, amelyben retry és kiesett persona is volt. Kitalált kérdés (kerékpárszerviz éves karbantartási bérlete), személyes adat és valódi cégnév nélkül. Az eseményei változtatás nélkül kerültek a `backend/seed/sample_run.sql`-be (43 esemény; a fájl az exportszkripttel újra lett generálva, amikor a seed formátuma egyetlen utasításra változott). **A mintában nincs szintézis:** a rögzítésekor még élt a szintézis hibája, és a javítás utáni három futás egyikében sem volt retry és kiesett persona, így egyik sem válthatta le.

**Megfigyelések**

- **A szintézis az első négy végigment futásból háromban elbukott** (`MALFORMED_PROVIDER_OUTPUT`). **A mért ok:** a modell időnként a kérés `response_format` mezőjét visszaírja a válasz első kulcsaként (`"type": "json_object"`), utána jön az öt kért kulcs hibátlanul; a `SynthesisResult` séma az ismeretlen kulcsot tiltotta, ezért a teljes választ eldobtuk. Ez a három bukott futás tárolt persona-válaszaival megismételt négy különálló hívásból egyben jött elő (a többi három érvényes volt); mind a négy hívás `finish_reason`-je `stop`, a válasz nem volt csonka, és nem volt kódblokkba csomagolva. A három eredeti bukás nyers válasza nincs meg, így az, hogy mindhárom pontosan ez volt-e, következtetés, nem mérés. Javítás: a szintézis ismeretlen kulcsait eldobjuk. A javítás után három futásból három szintézise elkészült.
- A válaszok nem mindig tiszták: az egyik érvényes szintézis utolsó szövegmezőjének végén fölösleges `}` jelek voltak a szövegen belül. Az opencode Go a jelek szerint több szolgáltatóhoz irányít (a `usage` blokk felépítése hívásonként kétféle volt).
- Ugyanez a visszaírt kulcs okozhatja a kiesett personákat és ritkán a persona-generálás bukását is (ott is tiltott az ismeretlen kulcs); ez nincs kimérve, és a persona- meg a blueprint-ellenőrzés nem változott.
- Az első négy végigment futás 72 persona-hívásából 2 válasz volt a séma szerint érvénytelen (kiesett persona, retry nélkül). A három retry mind `NETWORK_ERROR` volt, nagyjából 60 mp-nél, vagyis a hívás időtúllépése; mindhárom a második kísérletre sikerült. A 6–8. futás 54 persona-hívásában nem volt sem érvénytelen válasz, sem retry.
- A futásidő a hét végigment futásban 86–132 mp. Retry nélkül 86–126 mp (az 1., 5., 6., 7. és 8. futás: 86,3 / 92,2 / 117,8 / 105,7 / 126,3 mp); a két retry-os futás 114,7 és 131,7 mp volt, egy időtúllépéses retry önmagában kb. 60 mp-ig áll. Az oldalak állítása ezért „nagyjából másfél perc”-ről „nagyjából másfél-két perc”-re változott; a 132 mp-es futás ennek a felső szélén kicsit túl van.
- A PDF-ben a personák alatt a „Szervezeti szerep:” címke üresen áll (az érték nem jut el az eredménybe).
- Hibára futott futásnál a trace-en az éppen futó personák „fut” állapotban maradnak, és az összesítő is „fut: 5”-öt mutat a hibapanel alatt (már ismert, halasztott apróság).
- Az IP-keret üzenete szövegesen „három elemzést” mond, a keret értéke viszont környezeti változó.
- A megszakított futás `runs` sorában a tokenszám 0, miközben az eseményeiben 745 / 2 789 token szerepel: a takarító nem összesíti az eseményeket.

## Nyitott pontok

- **A mintában nincs szintézis** (a 4. futásban elbukott), így a minta eredményoldala és PDF-je összefoglaló nélküli. Balázs döntése, hogy ez így mehet-e. Új mintához további valódi futás kell (a nyolcas keret elfogyott): olyan futás, amelyben szintézis, retry és kiesett persona is van. A retry és a kiesés a szolgáltatón múlik; az első négy végigment futásból egyben volt mindkettő, az utolsó háromban egyik sem.
- A kiesett personák oka nincs kimérve; lehet ugyanaz a visszaírt `"type"` kulcs, mint a szintézisnél. Ha igen, a persona-válasznál is elég volna az ismeretlen kulcsot eldobni, de ez a módszertani oldal állítását („érvénytelen válasz kiejti a personát”) és a minta ritkaságát is érinti, ezért döntés kell hozzá.
- **A levél tényleges megérkezése nincs ellenőrizve:** a helyi `.env`-ben nincs `SWARMSENSE_RESEND_API_KEY` és `SWARMSENSE_EMAIL_FROM`. Az űrlap ilyenkor a „nincs beállítva” szöveget adja (ellenőrizve). A CLAUDE.md megfelelő kritériuma nyitva marad.
- A Discord-értesítés élesben nincs ellenőrizve (a webhook-változó helyben üres).
- A fejlesztői adatbázisban a minta forrásfutása közönséges futásként van meg, ezért ott a seed szándékosan semmit nem ír, és nincs `is_sample` sor: a `/minta` helyben csak üres adatbázison (vagy a futás törlése után) működik. A backend ilyenkor nem írja ki a „sample run loaded from seed” sort (a függvény azt jelzi, lett-e ettől minta).
- Az `export_sample` szkript hiányzó környezeti változónál (pl. nincs `SWARMSENSE_LLM_API_KEY`) „Nincs ilyen futás” üzenetet ad, mert a beállítási hibát is `ValueError`-ként kapja el.
