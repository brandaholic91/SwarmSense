# Haladás

A cél és a teljesítési kritériumok a `CLAUDE.md`-ben, a részletek a `docs/superpowers/specs/2026-10-07-swarmsense-portfolio-design.md` specben vannak. Ez a fájl csak azt rögzíti, hol tartunk.

**Most:** az A terv (új alap) kész (2026-10-07). A B terv megírása következik. Az A terv végén egy valódi futás helyben: 18/18 persona, `completed`, 86,5 mp, 16 134 bemeneti és 36 335 kimeneti token.

## Lépések

| Terv | # | Lépés | Állapot |
|---|---|---|---|
| nincs terv | 0 | Hol fut most élesben; kimérő futás az opencode Go-n | kész, két nyitott ponttal |
| A: Új alap | 1 | Törlés | kész |
| | 2 | Postgres, `db.py`, LLM-kliens, tesztek | kész |
| B: A darab | 3 | Események, trace képernyő, keretek | nincs elkezdve |
| | 4 | Eredmény tárolása, eredményoldal, PDF | nincs elkezdve |
| | 5 | E-mail, takarítás, Discord, adatkezelés, módszertan, landing oldal | nincs elkezdve |
| | 6 | Mintafutás, visszajátszás, seed | nincs elkezdve |
| C: Kiadás | 7 | Deploy, régi lekapcsolása | nincs elkezdve |
| | 8 | Publikálás | nincs elkezdve |

Állapotok: nincs elkezdve · folyamatban · kész.

## Implementációs tervek

| Terv | Fájl | Állapot |
|---|---|---|
| A | `docs/superpowers/plans/2026-10-07-swarmsense-a-uj-alap.md` | kész |
| B | még nincs megírva | az A terv után |
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
| 2026-10-07 | A `swarmsense` logger minimális beállítást kapott az `app/main.py`-ban (INFO, egy `StreamHandler`), így a futásonkénti összefoglaló sor uvicorn alatt is látszik (spec 10. szakasz, frissítve) | A valódi futásnál derült ki, hogy nincs naplózási beállítás, ezért az INFO sorok elvesztek; javítva, a javítás utáni láthatóságot egy próbasorral ellenőriztük, valódi futással nem |
| 2026-10-07 | A landing oldal újraírása bekerült a B terv 5. lépésébe (spec 14. szakasz, frissítve) | Balázs döntése; a spec eddig egyik lépéshez sem rendelte, a mostani szövegben hamis állítások vannak („90 másodperc", „15-20 persona") |

## Megfigyelések a valódi futásból

- A kérdés szövege egyszer megjelent a Next fejlesztői szerver naplójában a Server Action nyomvonalán (fejlesztői mód; éles buildnél nincs ellenőrizve).
- A böngésző fülében a polling megállt, amíg a fül a háttérben volt (az ok nincs megerősítve; a B terv lecseréli a pollingot).
