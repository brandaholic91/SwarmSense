# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Hol tart a projekt

A repo átalakítás alatt áll: a freemium funnelből portfóliódarab lesz. **A kód még a régi állapotot tükrözi** (Supabase, OpenRouter, magic link, qualifier, Sentry); ez a fájl a célállapotot rögzíti.

- **Részletes design:** `docs/superpowers/specs/2026-10-07-swarmsense-portfolio-design.md`. Ha ez a fájl és a spec eltér, a spec az irányadó.
- **Aktuális állás:** `TRACKING.md`. Munka előtt olvasd el, lépés lezárásakor frissítsd.
- A `README.md`, a `_bmad*` mappák és a `docs/` régi fájljai a régi terméket írják le; ne ezekből dolgozz.

## Célállapot

Egyetlen flow, regisztráció nélkül: két mező (téma, célközönség) → 18 szintetikus persona → szintézis → letölthető PDF. A néző a futást élő trace-en követi.

```
Böngésző → Next.js frontend (egyedül ez nyilvános) → FastAPI backend → Postgres
                                                        ├→ opencode Go (LLM)
                                                        ├→ Resend (PDF e-mailben)
                                                        └→ Discord webhook
```

**Kötött döntések** (ne térj el tőlük egyeztetés nélkül)

- **A böngésző soha nem hívja közvetlenül a backendet.** Egyszeri művelet Server Actionön megy, a polling és a PDF-letöltés Next route handleren.
- **Adatbázis:** `psycopg` 3 nyers SQL-lel, minden lekérdezés a `backend/app/db.py`-ban. ORM és migrációs eszköz nincs; a séma a `backend/schema.sql`. Három tábla: `runs`, `run_events`, `email_requests`.
- **Trace:** az engine minden állapotváltásnál sort ír a `run_events`-be; a kliens 1 mp-enként kéri az újakat (`?after=<id>`), és egy tiszta `applyEvent(állapot, esemény)` függvénnyel dolgozza fel. Az élő futás és a visszajátszás ugyanazt a kódot használja.
- **A futás** a backend folyamatában, háttérfeladatként megy, külön szálon és saját event loopban. Emiatt a Playwright-böngésző PDF-enként indul, nem az app indulásakor.
- **LLM:** opencode Go, `deepseek-v4.1-flash`, kötelező `x-opencode-session` fejléccel. Költségkövetés nincs; a kijelző tokenszámot és listaárból becsült költséget mutat.
- **Keretek:** IP-nkénti és összesített futásszám gördülő 24 órára, legfeljebb 2 egyidejű futás, levélkeretek. Mind `count` lekérdezés, az értékek környezeti változók.
- **Hibáról kifelé csak hibakód megy,** a szolgáltató nyers üzenete nem. A felhasználói szövegek a `frontend/lib/messages.ts`-ben vannak, magyarul.
- **Megőrzés:** a futás és a PDF megmarad, az e-mail-cím 14 nap után törlődik. Nyers IP nem tárolódik, csak HMAC.
- **Nincs:** auth, Sentry, operator endpoint, Supabase.

## Teljesítési kritériumok

**A terv: Új alap** (1–2. lépés)

- [ ] A spec 11. szakaszában felsorolt kód, oldalak és tesztek törölve.
- [ ] A backend kódjában nincs `supabase`, `sentry`, `openrouter` hivatkozás.
- [ ] `POST /api/v1/runs` futást indít Postgresen és opencode Go-n, a státusz lekérdezhető.
- [ ] A backend tesztek valódi Postgres ellen futnak, és zöldek; valódi LLM-hívás nincs bennük.
- [ ] A frontend lint, típusellenőrzés, teszt és build zöld.

**B terv: A darab** (3–6. lépés)

- [ ] Helyben egy futás végigvihető az űrlaptól a PDF-letöltésig úgy, hogy a böngésző hálózati forgalmában csak a Next címe szerepel.
- [ ] A trace personánként mutatja az állapotot, a kísérletszámot, az időt és a tokeneket; egyszerre legfeljebb 5 persona „fut”.
- [ ] Minden keret betelése a megfelelő üzenetet adja, és a mintafutásra mutat.
- [ ] Kiesett persona, elbukott szintézis és beragadt futás a spec 10. szakasza szerint viselkedik.
- [ ] Az e-mail megérkezik a PDF-fel; a 14 napnál régebbi cím a takarítás után nincs az adatbázisban.
- [ ] A `/minta` valódi futást játszik vissza, amelyben van retry és kiesett persona; üres adatbázisra a seed betölti.
- [ ] Az eredményoldalról a futás visszajátszható.
- [ ] Az adatkezelési és a módszertani oldal a spec szerinti tartalommal él.

**C terv: Kiadás** (7–8. lépés)

- [ ] A `swarmsense.growthframe.hu` él; a backend és a Postgres kívülről nem érhető el.
- [ ] A kézi ellenőrzőlista az éles oldalon végigment, a levélig.
- [ ] A régi deploy lekapcsolva, minden régi kulcs cserélve vagy törölve.
- [ ] A nyilvános repo tiszta történettel indul, a `gitleaks` nem talál semmit, a régi történet bundle-ben megvan.
- [ ] A README leírja, mit mutat a demó, hogyan működik és mik a korlátai.

## Parancsok

A `psycopg`-re és a valódi Postgres-tesztekre való átállás után a backend parancsai változnak; akkor ezt a szakaszt frissíteni kell.

```bash
# Frontend (frontend/ mappából, pnpm 9, Node 20+)
pnpm install --frozen-lockfile
pnpm dev                      # http://localhost:3000
pnpm lint
pnpm exec tsc --noEmit
pnpm test                     # vitest, egyszeri futás
pnpm exec vitest run components/waiting-screen.test.tsx   # egy tesztfájl
pnpm build

# Backend (backend/ mappából, Python 3.12)
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests -q
pytest tests/services/test_persona_engine.py -q           # egy tesztfájl
pytest tests/services/test_persona_engine.py -k "név" -q  # egy teszt
python -m uvicorn app.main:app --port 8000
```

A backend beállításai `SWARMSENSE_` előtagú környezeti változók (`backend/app/core/config.py`).

## Munkamód

- Balázs Pythont alapszinten ismer, a TypeScriptet nem; a változtatásokhoz magyarázat kell, hogy mit és miért.
- A repo nyilvános lesz: titok, valódi e-mail-cím és belső gépnév ne kerüljön a kódba vagy a dokumentációba.
- Commit üzenet: Conventional Commits, angolul (`feat(backend): ...`), ahogy a meglévő történetben.
