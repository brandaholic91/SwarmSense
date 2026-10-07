# Haladás

A cél és a teljesítési kritériumok a `CLAUDE.md`-ben, a részletek a `docs/superpowers/specs/2026-10-07-swarmsense-portfolio-design.md` specben vannak. Ez a fájl csak azt rögzíti, hol tartunk.

**Most:** 0. lépés (mérés) következik. A kódhoz még nem nyúltunk.

## Lépések

| Terv | # | Lépés | Állapot |
|---|---|---|---|
| nincs terv | 0 | Hol fut most élesben; kimérő futás az opencode Go-n | nincs elkezdve |
| A: Új alap | 1 | Törlés | nincs elkezdve |
| | 2 | Postgres, `db.py`, LLM-kliens, tesztek | nincs elkezdve |
| B: A darab | 3 | Események, trace képernyő, keretek | nincs elkezdve |
| | 4 | Eredmény tárolása, eredményoldal, PDF | nincs elkezdve |
| | 5 | E-mail, takarítás, Discord, adatkezelés, módszertan | nincs elkezdve |
| | 6 | Mintafutás, visszajátszás, seed | nincs elkezdve |
| C: Kiadás | 7 | Deploy, régi lekapcsolása | nincs elkezdve |
| | 8 | Publikálás | nincs elkezdve |

Állapotok: nincs elkezdve · folyamatban · kész.

## Implementációs tervek

| Terv | Fájl | Állapot |
|---|---|---|
| A | még nincs megírva | a 0. lépés után |
| B | még nincs megírva | az A terv után |
| C | még nincs megírva | a B terv után |

## A 0. lépés mérései

| Kérdés | Eredmény |
|---|---|
| Ad-e az opencode Go `usage` mezőt tokenszámmal? | |
| Egy futás ideje és tokenszáma | |
| Átmegy-e 5, illetve 10 párhuzamos hívás egy kulcsról? | |
| Hogyan jelzi a keret kimerülését? | |
| Támogatja-e a `response_format: json_object` beállítást? | |
| Hol fut most élesben a SwarmSense? | |

## Eltérések a spectől

Ha építés közben valami másképp alakul, mint a specben, ide kerül egy sor (dátum, mi, miért), és a spec is frissül.

| Dátum | Mi változott | Miért |
|---|---|---|
