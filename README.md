# SwarmSense

Egy kérdésre 18 szintetikus persona válaszol, a válaszokból összefoglaló és letölthető PDF készül. A futás lépései közben élőben követhetők.

**Demó:** <https://swarmsense.growthframe.hu>

A personákat nyelvi modell állítja elő, nem valódi emberek. Az eredmény gondolatébresztő, nem piackutatás.

## Mit csinál

1. Megadsz egy témát és egy célközönséget. Regisztráció nincs.
2. A rendszer a célközönséghez 18 personát tervez, majd mindegyiktől külön LLM-hívásban véleményt kér.
3. A válaszokból összefoglaló készül: fő akadályok, a siker feltételei, a legjobb célszegmens, stratégiai javaslat.
4. Az eredmény megnézhető az oldalon, letölthető PDF-ben, és kérésre e-mailben is megérkezik.

A futás közben a képernyő personánként mutatja az állapotot, a kísérletek számát, az eltelt időt és a felhasznált tokeneket. A kész futás ugyanezen a nézeten visszajátszható, a `/minta` oldal pedig egy rögzített valódi futást játszik le.

## Felépítés

```
Böngésző → Next.js frontend → FastAPI backend → Postgres
                                 ├→ LLM-szolgáltató (opencode Go)
                                 ├→ Resend (PDF e-mailben)
                                 └→ Discord webhook (hibajelzés)
```

Egyedül a frontend nyilvános. A backend és az adatbázis csak belső hálózaton érhető el.

Egy futás 20 LLM-hívás: egy a personák megtervezéséhez, 18 a véleményekhez (egyszerre legfeljebb 5 fut, hívásonként legfeljebb 3 kísérlettel), egy az összefoglalóhoz. A backend a futást háttérfeladatként, külön szálon dolgozza fel, és minden állapotváltásról sort ír a `run_events` táblába. A PDF-et Jinja2-sablonból headless Chromium készíti.

| Mappa | Tartalom |
|---|---|
| `frontend/` | Next.js 16, React 19, TypeScript, Tailwind 4, Vitest |
| `backend/app/` | FastAPI, Python 3.12, `psycopg` 3, Playwright |
| `backend/schema.sql` | A teljes séma: `runs`, `run_events`, `email_requests` |
| `backend/seed/` | A mintafutás, amelyet üres adatbázisra a backend betölt |
| `docs/lekerdezesek.md` | Lekérdezések az üzemeltetéshez |

## Tervezési döntések

- **A böngésző soha nem hívja közvetlenül a backendet.** Az egyszeri műveletek Server Actionön, a lekérdezések és a PDF-letöltés Next route handleren mennek át. A backend minden kéréshez közös titkot vár egy fejlécben, így nincs szükség CORS-ra, és a backend címe nem jelenik meg a kliensben.
- **Polling WebSocket helyett.** A kliens másodpercenként kéri az új eseményeket (`?after=<id>`). Egy másfél-két perces futáshoz ez elég, és nem kell hozzá tartós kapcsolat.
- **Az élő nézet és a visszajátszás ugyanaz a kód.** Az állapotot egyetlen tiszta függvény, az `applyEvent(állapot, esemény)` számolja; a visszajátszás a tárolt eseményeket adja neki időzítve.
- **Nyers SQL ORM nélkül.** Három tábla van, minden lekérdezés a `backend/app/db.py`-ban. A sémát a backend induláskor alkalmazza; migrációs eszköz nincs.
- **A keretek `count` lekérdezések.** Futás IP-nként és összesen gördülő 24 órára, legfeljebb 2 egyidejű futás, levélkeretek. Az értékek környezeti változók; külön rate limiter szolgáltatás nincs.
- **Hibáról kifelé csak hibakód megy.** A szolgáltató nyers üzenete a naplóban marad; a felhasználói szövegek a `frontend/lib/messages.ts`-ben vannak.

## Hibakezelés

- Ha egy persona három kísérlet után sem ad érvényes választ, kiesik; a futás a többivel megy tovább.
- 12-nél kevesebb sikeres persona esetén a futás sikertelen.
- Ha az összefoglaló nem készül el, az eredmény részlegesként jelenik meg a personák válaszaival.
- A beragadt futásokat percenként futó takarítás zárja le.

## Adatkezelés

- A futás és a PDF megmarad, az e-mail-cím 14 nap után törlődik.
- Nyers IP-cím nem tárolódik, csak kulcsolt lenyomat (HMAC), amely a keretek számolásához kell.
- Nincs felhasználói fiók, hibakövető szolgáltatás és webanalitika.

## Korlátok

- A personák válaszai egy nyelvi modell kimenetei. Nem helyettesítenek valódi megkérdezést, és ugyanarra a kérdésre futásonként eltérhetnek.
- A kijelzett költség becslés: a tokenszám és a modell listaára alapján számolódik, nem a tényleges számlából.
- A demó közös LLM-keretet használ, ezért a napi futásszám korlátozott. Ha a keret betelt, a mintafutás akkor is megnézhető.
- A futás a backend folyamatában megy; újraindításkor a folyamatban lévő futás megszakad, és sikertelenként zárul.
- Automatikus tesztek valódi LLM-hívást nem indítanak.

## Futtatás helyben

Kell hozzá Docker, Python 3.12, Node 20+ és pnpm 9, valamint egy OpenAI-kompatibilis LLM-végpont kulcsa.

```bash
# 1. Postgres (localhost:5433)
docker compose -f docker-compose.dev.yml up -d

# 2. Backend
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
cp .env.example .env          # töltsd ki a kulcsot és a titkokat
python -m uvicorn app.main:app --port 8000 --env-file .env

# 3. Frontend (másik terminálban)
cd frontend
pnpm install --frozen-lockfile
cp .env.example .env.local    # az INTERNAL_SECRET egyezzen a backendével
pnpm dev                      # http://localhost:3000
```

A backend beállításai `SWARMSENSE_` előtagú környezeti változók, a teljes lista a `backend/app/core/config.py`-ban van. Resend-kulcs nélkül a levélküldés, Discord webhook nélkül a hibajelzés nem működik; a többi funkció igen.

## Tesztek

```bash
# Backend: valódi Postgres ellen fut, LLM-hívás nélkül
cd backend && pytest tests -q

# Frontend
cd frontend && pnpm lint && pnpm exec tsc --noEmit && pnpm test && pnpm build
```

## Licenc

A kód MIT licenc alatt érhető el, lásd a [`LICENSE`](LICENSE) fájlt. A PDF-ben használt IBM Plex Sans betűtípus licence a `backend/app/assets/fonts/OFL.txt`.
