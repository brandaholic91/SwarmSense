# SwarmSense B terv: A darab – Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A futás élő trace-en követhető, az eredmény megnézhető, PDF-ben letölthető és e-mailben elkérhető, a keretek védik az LLM-kvótát, és van visszajátszható mintafutás; a böngésző közben csak a Nexttel beszél.

**Architecture:** Az engine minden állapotváltásnál sort ír a `run_events` táblába; a böngésző egy Next route handleren át 1 mp-enként kéri az újakat, és egy tiszta `applyEvent` függvénnyel építi az állapotot. Ugyanez a függvény és ugyanaz a megjelenítő komponens játssza vissza a rögzített futást. Az eredmény a `runs.result` oszlopból jön, a PDF Jinja2 → Chromium úton készül a `runs.pdf` oszlopba. A backend minden `/api/v1/runs` végpontja `X-Internal-Secret`-et kér, a CORS megszűnik.

**Tech Stack:** Python 3.12, FastAPI, `psycopg` 3, Jinja2, Playwright (Chromium), pytest, Postgres 17, Next.js 16 (App Router), React 19, vitest, pnpm 9. Külső szolgáltatás: opencode Go, Resend, Discord webhook.

**Spec:** `docs/superpowers/specs/2026-10-07-swarmsense-portfolio-design.md` (ez a terv a 14. szakasz 3–6. lépését valósítja meg). Az A tervből áthozott tételek: `.superpowers/sdd/2026-10-07-swarmsense-a-uj-alap/progress.md`.

**Előfeltétel:** a munka új ágon megy (`portfolio-plan-b`), a `portfolio-redesign-spec` ágról indítva. A dev Postgres fut (`docker compose -f docker-compose.dev.yml up -d`).

## Mi nincs ebben a tervben

- Deploy, a végleges compose fájl, a régi lekapcsolása, kulcscsere, tiszta git-történet, README, LICENSE (C terv). A backend `Dockerfile` viszont itt áll át a Playwright image-re, mert a PDF-hez kell.
- Az útvonalak átnevezése magyarra (`/research`, `/waiting`). Az új útvonalak a spec szerint magyarok (`/minta`, `/eredmeny`, `/modszertan`); a két régi marad.
- A keretkimerülés jelzésének kimérése az opencode Go-n. A szabály marad: a 429-et a kliens újrapróbálja, a többi 4xx-et nem.

**Átmeneti törés:** a 3. feladat megszünteti a CORS-t és a régi státuszvégpontot, a frontend a 4. feladatban áll át. A kettő között a tesztek zöldek, de a böngészőből indított futás várakozó képernyője nem működik.

## Eltérések a spectől, amelyeket ez a terv bevezet

Mindegyik bekerül a `TRACKING.md` „Eltérések” táblájába és a specbe abban a feladatban, amelyik megvalósítja.

| Mi | Miért | Feladat |
|---|---|---|
| Új eseménytípus: `synthesis_failed` (`error_code`, `duration_ms`) | A spec 5. szakaszában nincs esemény arra, hogy a szintézis elbukott; a trace-nek ezt mutatnia kell | 1 |
| A `run_failed` esemény kitölti az `error_code` mezőt | A hibaoldalnak és a Discord-értesítésnek kell az ok | 1 |
| A polling válaszban `topic`, `created_at` és `price` is van | A trace fejléce a kérdést mutatja, a költségbecslés ára egy helyen (a backendben) él | 3 |
| A backend minden `/api/v1/runs…` végpontja titkot kér, nem csak az írók | A böngésző már nem hívja a backendet, így nincs ok nyitva hagyni | 3 |
| A persona-leírások száma pontosan 18: a többlet levágódik, a hiány a futás bukása | A kliens 18 sort rajzol; a spec nem mondja meg, mi legyen eltérő darabszámnál | 1 |
| A seed fájl nem tartalmazza a PDF-et | A letöltő végpont első kérésre legenerálja (spec 9. szakasz), a repo nem hízik bináris adattal | 10 |

## Global Constraints

- Adatbázis-hozzáférés kizárólag a `backend/app/db.py`-ban, nyers SQL-lel; ORM, migrációs eszköz és pool nincs. A séma a `backend/schema.sql`; ebben a tervben nem változik.
- A böngésző soha nem hívja a backendet. Egyszeri művelet Server Action, ismételt lekérés és fájlletöltés Next route handler. A kliensoldali kódban nem szerepelhet `NEXT_PUBLIC_API_URL`.
- Hibáról kifelé csak hibakód megy. A szolgáltató nyers üzenete, kivételszöveg és traceback nem kerül sem válaszba, sem `run_events` sorba, sem naplóba. A napló: futásazonosító, kivételtípus, hibakód.
- E-mail-cím és a kérdés szövege nem kerül naplóba és Discord-üzenetbe.
- Tesztben nincs valódi hálózati hívás: LLM, Resend és Discord autouse fixture-rel tiltva. Egyetlen kivétel a PDF-füstteszt, amely valódi Chromiumot indít.
- A tesztek csak `_test` végű nevű adatbázist üríthetnek.
- Keretértékek (spec 7. szakasz): mezőnként 500 karakter; 2 egyidejű futás; IP-nként 3 és összesen 20 futás gördülő 24 órára; futásonként 3 és összesen 30 levél 24 órára. Mind környezeti változó, ezekkel az alapértékekkel.
- `MIN_SUCCESSFUL_PERSONAS = 12`, párhuzamossági keret 5, kísérletek száma hívásonként legfeljebb 3, persona-darabszám 18.
- A takarítás: `email_requests` 14 nap után törlődik; a 10 percnél régebben nem végállapotú futás `failed`.
- Felhasználói szöveg magyarul, a `frontend/lib/messages.ts`-ben és a `frontend/lib/errors.ts`-ben. A PDF és a levél szövege a backend sablonjaiban van, magyarul.
- Titok, valódi e-mail-cím és belső gépnév nem kerül a repóba. A `.env` fájlok értékeit parancs nem írhatja ki, csak a neveket.
- A frontend kódja előtt olvasd el a `frontend/AGENTS.md`-t: ez Next.js 16, a `node_modules/next/dist/docs/` az irányadó (pl. a route handler `params`-a `Promise`, a `headers()` aszinkron).
- Commit: Conventional Commits, angolul.

## Review Focus

Amit a spec nem mond ki, de egy felhasználó belefut. Mindegyikhez teszt tartozik a megjelölt feladatban.

1. **A kérdésben HTML van** (`<script>alert(1)</script>`, `&`, idézőjel): a PDF-ben és a levélben szövegként jelenik meg, nem kódként. → 6. és 7. feladat.
2. **A néző újratölti a várakozó oldalt, vagy kész futás linkjét nyitja meg:** a teljes eseménysor egyben érkezik, az állapot helyes, és az oldal az eredményre visz; kétszer megkapott esemény nem számolódik kétszer. → 4. feladat.
3. **A fül a háttérbe kerül, majd visszajön:** a lekérdezés azonnal újraindul, és a kimaradt eseményeket egyben feldolgozza. → 4. feladat.
4. **A takarító `failed`-re állít egy lassú futást, amely utána mégis végez:** a futás `failed` marad, `run_completed` esemény nem íródik. → 8. feladat.
5. **Hibás vagy rosszindulatú e-mail-cím** (sortörés a címben, 320 karakter fölött, két cím vesszővel): `422` `INVALID_EMAIL`, sor nem jön létre, levél nem megy. → 7. feladat.

---

### Task 1: Események az engine-ben és a futásfeldolgozóban

**Files:**
- Modify: `backend/app/db.py`, `backend/app/services/llm_client.py`, `backend/app/services/persona_engine.py`, `backend/app/services/blueprint_generator.py`, `backend/app/services/run_processor.py`, `backend/app/models/persona.py`
- Create: `backend/app/services/events.py`
- Test: `backend/tests/test_db.py`, `backend/tests/services/test_llm_client.py`, `backend/tests/services/test_persona_engine.py`, `backend/tests/services/test_run_processor.py`
- Modify: `TRACKING.md`, a spec 5. szakasza

**Interfaces:**
- Produces (`db.py`):
  - `EVENT_COLUMNS = frozenset({"persona_index", "persona_name", "attempt", "error_code", "duration_ms", "input_tokens", "output_tokens"})`
  - `insert_event(run_id: str, type: str, **fields: Any) -> int` – ismeretlen mezőre `ValueError`; a visszaadott érték az új sor `id`-ja.
  - `list_events(run_id: str, *, after: int = 0) -> list[dict[str, Any]]` – `id > after`, `id` szerint növekvő; nem UUID azonosítóra üres lista.
- Produces (`events.py`):
  - `EventSink = Callable[..., None]` – hívása: `sink(type, **fields)`.
  - `async def safe_emit(sink: EventSink | None, type: str, **fields: Any) -> None` – `asyncio.to_thread`-del hív; a kivételt elnyeli, és `swarmsense.run` loggerre csak a kivétel típusnevét írja. Egy esemény elvesztése nem állítja meg a futást.
- Produces (`llm_client.py`): `generate_json(..., on_retry: Callable[[int, str], Awaitable[None]] | None = None)`. A visszahívás az alvás előtt fut, argumentumai: a **következő** kísérlet sorszáma (2 vagy 3) és az elbukott kísérlet hibakódja (`_classify_error_code`).
- Produces (`blueprint_generator.py`): `class BlueprintGenerationError(Exception)` `usage: TokenUsage` attribútummal. A `generate_persona_blueprints` minden `LLMProviderError`-t és `ValueError`-t ebbe csomagol (`from None`, hogy a lánc ne vigye tovább az LLM kimenetét); a `usage` a szolgáltatói hiba `usage`-a, különben nulla.
- Produces (`persona_engine.py`): `execute_persona_engine(..., on_event: EventSink | None = None)`; az `on_persona_completed` paraméter megszűnik.
- Produces (`models/persona.py`): `PersonaFailure` mezői: `persona_name`, `error_code`. Az `error_message` mező megszűnik.
- Produces (`run_processor.py`): `process_run(...) -> PersonaRunResult | None`; hibakód-konstansok: `PERSONA_GENERATION_FAILED`, `TOO_FEW_PERSONAS`, `INTERNAL_ERROR`.

**Eseménysorrend egy hibátlan futásban** (a tesztek ezt rögzítik):
`run_started` → `personas_generated` → személyenként `persona_started` → (`persona_retry`)* → `persona_completed` | `persona_failed` → `synthesis_started` → `synthesis_completed` | `synthesis_failed` → `run_completed` | `run_failed`.

**Mezők:**
- `persona_index`: a persona helye a leírások listájában, 0-tól.
- `attempt`: `persona_retry`-nál a következő kísérlet sorszáma; `persona_completed` és `persona_failed` esetén az utolsó kísérleté (retry nélkül 1).
- `duration_ms`: `time.monotonic()` különbség; personánál a `persona_started`-től a végéig.
- Tokenek: `personas_generated`, `persona_completed`, `persona_failed` (lehet 0), `synthesis_completed`. Az eseményekben szereplő tokenek összege egyenlő a `runs.input_tokens` és `runs.output_tokens` értékével.
- `error_code` a personánál: a `LLMProviderError.error_code`, sémahibánál `MALFORMED_PROVIDER_OUTPUT`, egyébként `UNEXPECTED_ENGINE_ERROR`.

- [x] **Step 1: Írd meg a bukó `db` teszteket** (`tests/test_db.py`)

```python
def test_insert_and_list_events_in_order(clean_db):
    run = db.create_run(topic="t", audience="a")
    first = db.insert_event(run["id"], "run_started")
    second = db.insert_event(
        run["id"], "persona_retry", persona_index=7, persona_name="Kovács Anna",
        attempt=2, error_code="RATE_LIMITED",
    )
    events = db.list_events(run["id"])
    assert [e["id"] for e in events] == [first, second]
    assert events[1]["attempt"] == 2 and events[1]["persona_name"] == "Kovács Anna"
    assert [e["id"] for e in db.list_events(run["id"], after=first)] == [second]

def test_insert_event_rejects_unknown_field(clean_db):
    run = db.create_run(topic="t", audience="a")
    with pytest.raises(ValueError):
        db.insert_event(run["id"], "run_started", error_message="nyers szöveg")

def test_list_events_invalid_run_id_is_empty(clean_db):
    assert db.list_events("nem-uuid") == []
```

Ugyanitt: a `test_update_run_rejects_invalid_status` `pytest.raises(Exception)`-je szűküljön `psycopg.errors.CheckViolation`-re.

- [x] **Step 2: Írd meg a bukó `llm_client` teszteket**

- `test_on_retry_called_with_next_attempt_and_code`: a hamis transport kétszer 429-et dob, harmadszorra válaszol; az `on_retry` hívásai pontosan `[(2, "RATE_LIMITED"), (3, "RATE_LIMITED")]`.
- `test_on_retry_not_called_on_terminal_error`: 400 után nincs hívás.
- `test_url_error_body_has_no_reason_text`: a `urlopen` `URLError("titkos-gepnev.belso")`-t dob; a `TransportError.body` nem tartalmazza a `titkos-gepnev` szöveget, a `status_code` `None`.
- A meglévő `test_real_transport_maps_low_level_failures_to_network_error` paraméterlistája bővül: `UnicodeDecodeError` (nem UTF-8 törzs 200-as válaszban), és az az eset, amikor a `HTTPError.read()` `TimeoutError`-t dob.

- [x] **Step 3: Írd meg a bukó engine-teszteket** (`test_persona_engine.py`)

A hamis kliens a `generate_json`-t valósítja meg, és elfogadja az `on_retry`-t. Egy `events: list[tuple[str, dict]]` listába gyűjtő sinkkel:

- `test_events_respect_concurrency_limit`: 18 előre megadott blueprint; az eseménylista minden előtagjában `persona_started` darabszám − (`persona_completed` + `persona_failed`) ≤ 5, és egyszer eléri az 5-öt.
- `test_persona_events_carry_index_name_attempt_tokens`: a 3. persona hívása egyszer meghívja az `on_retry(2, "RATE_LIMITED")`-et, majd sikeres; az eseményei sorrendben `persona_started`, `persona_retry` (`attempt == 2`, `error_code == "RATE_LIMITED"`), `persona_completed` (`attempt == 2`, `input_tokens == 10`, `output_tokens == 5`, `duration_ms >= 0`), mind `persona_index == 2`.
- `test_failed_persona_event_has_code_only`: a szolgáltatói hiba üzenete `"NYERS-SZOLGALTATOI-UZENET-42"`; a `persona_failed` esemény `error_code`-ja `"UPSTREAM_ERROR"`, és sem az esemény mezőiben, sem a `result.failures` elemeinek `model_dump()`-jában nem szerepel a jelölő.
- `test_personas_generated_event_only_when_generated`: előre megadott blueprintekkel nincs `personas_generated`; generálással van, tokenekkel.
- `test_sink_failure_does_not_stop_engine`: a sink minden hívásra kivételt dob; a futás 18 választ ad.

A blueprint-generátorhoz (ugyanebben a fájlban vagy `test_blueprint_generator.py`-ban):

- `test_extra_blueprints_are_truncated_to_count`: a válaszban 20 persona, `count=18` → 18 jön vissza.
- `test_too_few_blueprints_raise`: 17 persona → `BlueprintGenerationError`.
- `test_provider_error_is_wrapped_with_usage`: `LLMProviderError(usage=TokenUsage(7, 3))` → `BlueprintGenerationError`, `usage == TokenUsage(7, 3)`, `__cause__ is None`.

- [x] **Step 4: Írd meg a bukó futásfeldolgozó-teszteket** (`test_run_processor.py`, a meglévő `make_fake_llm`-mel)

- `test_event_sequence_of_completed_run`: az eseménytípusok listája `run_started`, `personas_generated`, majd 18 `persona_started` és 18 `persona_completed` (tetszőleges összefésülésben), `synthesis_started`, `synthesis_completed`, `run_completed`. Az események tokenösszege egyenlő a `runs` sor `input_tokens`, `output_tokens` értékével (200 és 100).
- `test_synthesis_failure_emits_synthesis_failed`: `synthesis_fails=True` → van `synthesis_failed` `error_code`-dal, a futás `partial`, az utolsó esemény `run_completed`.
- `test_too_few_personas_emits_run_failed_code`: 7 kieső persona → utolsó esemény `run_failed`, `error_code == "TOO_FEW_PERSONAS"`, nincs `synthesis_started`.
- `test_blueprint_failure_emits_run_failed_code_and_returns_none`: `blueprint_fails=True` → `process_run` `None`-t ad és **nem dob**; a futás `failed`; események: `run_started`, `run_failed` (`PERSONA_GENERATION_FAILED`).
- `test_unexpected_error_emits_internal_error`: az `execute_persona_engine` `RuntimeError`-t dob (monkeypatch) → `run_failed` `INTERNAL_ERROR` kóddal, a kivétel továbbmegy.
- A meglévő tesztek igazítása: az `on_persona_completed` és a `PersonaFailure.error_message` minden használata kikerül; a `test_failed_when_persona_generation_fails` az új viselkedést várja. A `test_unexpected_failure_logs_summary_and_provider_usage` kapja meg az állítást, amit a neve ígér (a `runs` sor tokenjei egyenlők a kivétel `usage`-ával).
- Pótlandó állítások (az A terv naplójából): `completed_at` ki van töltve `partial` futásnál; a `failed` futás tokenjei megmaradnak.

- [x] **Step 5: Futtasd, hogy elbukjon**

Run: `pytest tests -q`
Expected: FAIL (`AttributeError: module 'app.db' has no attribute 'insert_event'`, `TypeError ... on_event`)

- [x] **Step 6: Valósítsd meg a `db.py` két függvényét és az `events.py`-t** az Interfaces szerint. Az `insert_event` az oszlopneveket `psycopg.sql.Identifier`-rel illeszti be, ahogy az `update_run`.

- [x] **Step 7: `llm_client.py`**

- `on_retry` a `generate_json`-ból a `_request_with_retry`-ba megy tovább.
- `_post_json_sync`: az `URLError` ág `body={"detail": type(exc.reason).__name__}`-t ad; a `HTTPError` ágban az `exc.read()` saját `try`-ban van, hibánál a törzs `None`; az általános ág kivétellistája `UnicodeDecodeError`-ral bővül (a `ValueError` alosztálya, a `json.JSONDecodeError` mellé).

- [x] **Step 8: `blueprint_generator.py` és `persona_engine.py`**

- A generátor a listát `count` elemre vágja; ha `count`-nál kevesebb, hibát dob. Minden hibaág `BlueprintGenerationError`.
- Az engine a `safe_emit`-tel ír. A `persona_started` a szemafor megszerzése után megy ki. A kísérletszámot egy helyi változó követi, amelyet az `on_retry`-nak átadott aszinkron lezárás állít (és ugyanez küldi a `persona_retry`-t). A `PersonaFailure` építésénél nincs `str(exc)`.
- A haladás `runs.persona_count`-ba írása megszűnik (az eseményekből látszik); a végső érték a futás lezárásakor íródik, ahogy eddig.

- [x] **Step 9: `run_processor.py`**

- A sink: `lambda type, **f: db.insert_event(run_id, type, **f)`; a saját eseményeit is `safe_emit`-tel írja.
- Közös lezáró a három bukási úthoz: `_fail_run(*, run_id, error_code, usage, started, dropped)` → `status="failed"`, `completed_at`, tokenek, `run_failed` esemény az `error_code`-dal, összefoglaló naplósor.
- `BlueprintGenerationError` → `_fail_run(PERSONA_GENERATION_FAILED)`, visszatérés `None`. Egyéb kivétel a külső őrben → `_fail_run(INTERNAL_ERROR)`, majd `raise`.
- A szintézis köré `synthesis_started`, utána `synthesis_completed` (idő, tokenek) vagy `synthesis_failed` (`error_code`: a `LLMProviderError.error_code`, különben `MALFORMED_PROVIDER_OUTPUT`).
- `_format_persona_count_header_display`: `"valaszolt"` → `"válaszolt"`.

- [x] **Step 10: Futtasd, hogy átmenjen**

Run: `pytest tests -q`
Expected: PASS, 0 hiba.

- [x] **Step 11: Dokumentáld az eltéréseket.** A spec 5. szakaszának táblájába: `synthesis_failed` sor; a `run_failed` sorba `error_code`; egy mondat a 18-as darabszám szabályáról. `TRACKING.md`: három sor az „Eltérések” táblába.

- [x] **Step 12: Commit**

```bash
git add backend docs/superpowers/specs TRACKING.md
git commit -m "feat(backend): write run events from the engine and run processor"
```

---

### Task 2: Keretek és IP-hash a futás indításánál

**Files:**
- Create: `backend/app/services/limits.py`, `backend/tests/services/test_limits.py`
- Modify: `backend/app/core/config.py`, `backend/app/core/errors.py`, `backend/app/db.py`, `backend/app/routers/runs.py`, `backend/tests/conftest.py`, `backend/tests/routers/test_runs.py`, `backend/tests/test_db.py`, `backend/.env.example`

**Interfaces:**
- Produces (`config.py`): `ip_hash_secret: str` (kötelező), `max_concurrent_runs: int = 2`, `runs_per_ip_per_day: int = 3`, `runs_per_day: int = 20`.
- Produces (`errors.py`): `ErrorCode.BUSY`, `IP_LIMIT_REACHED`, `DAILY_LIMIT_REACHED`.
- Produces (`db.py`):
  - `create_run(*, topic: str, audience: str, ip_hash: str | None = None) -> dict[str, Any]`
  - `count_active_runs() -> int` – `status in ('queued','running','composing')`.
  - `count_runs_since(*, hours: int = 24, ip_hash: str | None = None) -> int` – `created_at > now() - make_interval(hours => %s)`; `ip_hash` megadásakor arra szűr. Mindkét számláló kihagyja az `is_sample = true` sorokat.
- Produces (`limits.py`):
  - `hash_ip(ip: str) -> str` – HMAC-SHA256 az `ip_hash_secret` kulccsal, hexa.
  - `check_run_limits(ip_hash: str | None) -> ErrorCode | None` – sorrend: egyidejű → IP → napi. `ip_hash is None` esetén az IP-ellenőrzés kimarad.
- A `POST /api/v1/runs` az `X-Client-IP` fejlécből számol hasht (üres vagy hiányzó fejléc → `None`). Betelt keret: `429`, törzs `{"detail": ..., "code": <kód>}`; sor nem jön létre, háttérfeladat nem indul.

- [x] **Step 1: Írd meg a bukó teszteket**

`test_limits.py` (valódi Postgres, `clean_db`):

```python
def test_hash_ip_is_stable_and_not_the_ip():
    assert limits.hash_ip("203.0.113.7") == limits.hash_ip("203.0.113.7")
    assert limits.hash_ip("203.0.113.7") != limits.hash_ip("203.0.113.8")
    assert "203.0.113.7" not in limits.hash_ip("203.0.113.7")

def test_order_concurrent_before_ip_before_daily(clean_db, monkeypatch):
    # 2 futó, ugyanattól az IP-től 3, összesen 20 fölött: az első betelt keret kódja jön
    ...
```

Esetek, egy-egy teszt: 2 `running` futás → `BUSY`; 2 `completed` → `None`; azonos hash-sel 3 futás 24 órán belül → `IP_LIMIT_REACHED`, más hash-sel `None`; 20 futás összesen → `DAILY_LIMIT_REACHED`; 25 órás futás nem számít (a `created_at`-ot a teszt SQL-lel állítja vissza); `failed` futás számít; `is_sample` futás nem számít; `ip_hash=None` mellett 5 hash nélküli futás után sincs `IP_LIMIT_REACHED`; a keretértékek környezeti változóból jönnek (`SWARMSENSE_RUNS_PER_DAY=1`).

`test_runs.py`: `X-Client-IP: 203.0.113.7` mellett a sor `ip_hash`-e egyenlő a `hash_ip` értékével, és a nyers cím a sor egyetlen oszlopában sem szerepel; fejléc nélkül `ip_hash is None`; betelt keretnél `429` a megfelelő kóddal, `_run_count()` nem nő, `dispatched == []` (paraméterezve a három kódra).

`conftest.py`: a `settings_env` beállítja a `SWARMSENSE_IP_HASH_SECRET=test-ip-secret` változót.

- [x] **Step 2: Futtasd, hogy elbukjon**

Run: `pytest tests/services/test_limits.py tests/routers/test_runs.py -q`
Expected: FAIL (`ModuleNotFoundError: app.services.limits`)

- [x] **Step 3: Valósítsd meg** a `config.py`, `errors.py`, `db.py`, `limits.py` és `routers/runs.py` változásait az Interfaces szerint. A router a keretet a `db.create_run` előtt ellenőrzi; ha az ellenőrzés adatbázishibára fut, a válasz a meglévő `500 RUN_START_FAILED`.

- [x] **Step 4: A helyi `.env` bővítése** (érték kiírása nélkül) és az `.env.example` frissítése a négy új névvel:

```bash
printf 'SWARMSENSE_IP_HASH_SECRET=%s\n' "$(openssl rand -hex 32)" >> backend/.env
grep -c '^SWARMSENSE_IP_HASH_SECRET=' backend/.env
```

Expected: `1`

- [x] **Step 5: Futtasd, hogy átmenjen**

Run: `pytest tests -q`
Expected: PASS

- [x] **Step 6: Commit**

```bash
git add backend
git commit -m "feat(backend): enforce run limits and store hashed client ip"
```

---

### Task 3: Eseményvégpont, zárt backend, CORS nélkül

**Files:**
- Create: `backend/app/core/pricing.py`
- Modify: `backend/app/routers/runs.py`, `backend/app/models/run.py`, `backend/app/core/internal_auth.py`, `backend/app/core/errors.py`, `backend/app/core/config.py`, `backend/app/main.py`, `backend/tests/routers/test_runs.py`, `backend/tests/conftest.py`, `backend/.env.example`
- Modify: `TRACKING.md`, a spec 3. és 5. szakasza

**Interfaces:**
- Produces: `GET /api/v1/runs/{run_id}/events?after=<int ≥ 0, alapérték 0>` →

```json
{
  "status": "running",
  "is_sample": false,
  "topic": "…",
  "created_at": "2026-10-07T12:00:00Z",
  "price": {"input_per_million_usd": 0.0, "output_per_million_usd": 0.0},
  "events": [
    {"id": 41, "type": "persona_retry", "persona_index": 7, "persona_name": "Kovács Anna",
     "attempt": 2, "error_code": "RATE_LIMITED", "at": "2026-10-07T12:00:03Z"}
  ]
}
```

  Az eseményből a `None` értékű mezők kimaradnak; az `at` a `created_at` ISO-alakja. Ismeretlen vagy nem UUID azonosító: `404 RUN_NOT_FOUND`. Adatbázishiba: `503 SERVICE_UNAVAILABLE` (naplóban csak a kivétel típusa). Negatív vagy nem szám `after`: `422`.
- Produces (`pricing.py`): `INPUT_PRICE_PER_MILLION_USD: float`, `OUTPUT_PRICE_PER_MILLION_USD: float`, `PRICE_SOURCE: str` (URL és dátum), `price_payload() -> dict[str, float]`.
- Produces (`internal_auth.py`): `is_internal_endpoint(request)` igaz minden útvonalra, amely `/api/v1/runs` vagy azzal kezdődik (`/api/v1/runs/…`), metódustól függetlenül. A `/` és a `/api/v1/status` nyitva marad. Az `INTERNAL_ONLY_ENDPOINTS` halmaz megszűnik.
- Megszűnik: `GET /api/v1/runs/{run_id}/status`, `RunStatusResponse`, a `CORSMiddleware`, a `frontend_origin` beállítás.

- [x] **Step 1: Állapítsd meg az árakat.** Nyisd meg a DeepSeek nyilvános árlistáját, és vedd ki a `deepseek-v4.1-flash` (vagy az ezzel azonos árazású flash modell) bemeneti (cache nélküli) és kimeneti listaárát USD / 1M token egységben. A két szám és a forrás (URL, a lekérdezés dátuma) a `pricing.py` konstansaiba és egy megjegyzésébe kerül. Ha az ár nem állapítható meg egyértelműen, állj meg `NEEDS_CONTEXT` státusszal; ne becsülj.

- [x] **Step 2: Írd meg a bukó teszteket** (`test_runs.py`)

- `test_events_returns_status_topic_price_and_events`: két beszúrt esemény; a válasz kulcsai pontosan a fenti hat; a `price` egyenlő a `pricing.price_payload()`-dal; az első eseményben nincs `persona_index` kulcs.
- `test_events_after_cursor_returns_only_newer`.
- `test_events_unknown_or_malformed_id_is_404` (paraméterezve: véletlen UUID, `"abc"`).
- `test_events_invalid_after_is_422` (`-1`, `"x"`).
- `test_events_db_failure_is_503_with_code`: a `db.get_run` kivételt dob; a törzs `code`-ja `SERVICE_UNAVAILABLE`, a naplóban nincs a kivétel szövege.
- `test_every_runs_endpoint_requires_secret`: titok nélkül `401` a `POST /api/v1/runs`, a `GET /api/v1/runs/<id>/events` és a `GET /api/v1/runs/<id>/events/` útvonalon.
- `test_status_and_root_are_open`.
- `test_no_cors_headers`: `Origin: http://localhost:3000` fejléccel a válaszban nincs `access-control-allow-origin`.
- Törlendő: a két CORS-teszt és a `test_get_status_*` tesztek. A `client` fixture alapból küldje a titkot.

- [x] **Step 3: Futtasd, hogy elbukjon**

Run: `pytest tests/routers/test_runs.py -q`
Expected: FAIL (404 az `/events` útvonalra)

- [x] **Step 4: Valósítsd meg.** A válaszmodell `response_model_exclude_none=True`-val megy ki. A `main.py`-ból kikerül a CORS és az „átmeneti” megjegyzés; a `config.py`-ból és a `conftest.py`-ból a `frontend_origin`; az `.env.example`-ből és a helyi `.env`-ből a `SWARMSENSE_FRONTEND_ORIGIN` sor (`sed -i '/^SWARMSENSE_FRONTEND_ORIGIN=/d' backend/.env`).

- [x] **Step 5: Futtasd, hogy átmenjen**

Run: `pytest tests -q && grep -rn "CORS\|frontend_origin" backend/app`
Expected: PASS, a `grep` nem talál semmit.

- [x] **Step 6: Dokumentáld az eltéréseket** (spec 3. szakasz: minden `/api/v1/runs…` végpont titkot kér; 5. szakasz: a polling válasz új mezői; `TRACKING.md` két sor).

- [x] **Step 7: Commit**

```bash
git add backend docs/superpowers/specs TRACKING.md
git commit -m "feat(backend): add events endpoint, lock run endpoints, drop cors"
```

---

### Task 4: Trace képernyő és a böngésző leválasztása a backendről

**Files:**
- Create: `frontend/lib/backend.ts`, `frontend/lib/trace.ts`, `frontend/lib/cost.ts`, `frontend/app/api/runs/[id]/events/route.ts`, `frontend/components/trace-view.tsx`, `frontend/components/live-trace.tsx`
- Test: `frontend/lib/trace.test.ts`, `frontend/lib/cost.test.ts`, `frontend/app/api/runs/[id]/events/route.test.ts`, `frontend/components/trace-view.test.tsx`, `frontend/components/live-trace.test.tsx`
- Modify: `frontend/app/actions/start-run.ts` (+ teszt), `frontend/app/research/page.tsx` (+ teszt), `frontend/app/waiting/[run_id]/page.tsx`, `frontend/lib/errors.ts`, `frontend/lib/messages.ts`, `frontend/.env.example`, `frontend/package.json`
- Delete: `frontend/components/waiting-screen.tsx`, `frontend/components/waiting-screen.test.tsx`

**Interfaces:**
- Consumes: a 3. feladat eseményvégpontja; a 2. feladat hibakódjai és az `X-Client-IP` fejléc.
- Produces (`lib/backend.ts`, csak szerveroldalon importálható):
  - `backendFetch(path: string, init?: RequestInit & { timeoutMs?: number }): Promise<Response>` – az `API_URL`-hez fűz, hozzáadja az `X-Internal-Secret`-et, `cache: "no-store"`, alapértelmezett időkorlát 10 000 ms (`AbortSignal.timeout`). Hiányzó `API_URL` vagy `INTERNAL_SECRET` esetén dob.
  - `isRunId(value: string): boolean` – UUID-alak ellenőrzése.
  - `clientIp(headers: Headers): string | null` – az `x-forwarded-for` első eleme, szóközök nélkül; ha nincs, `null`.
- Produces (`lib/trace.ts`):

```ts
export const TOTAL_PERSONAS = 18;
export const MAX_ATTEMPTS = 3;

export type TraceEvent = {
  id: number; type: string; at: string;
  persona_index?: number; persona_name?: string; attempt?: number;
  error_code?: string; duration_ms?: number; input_tokens?: number; output_tokens?: number;
};
export type PersonaRow = {
  index: number; name: string; status: "running" | "completed" | "failed";
  attempt: number; startedAt: string; durationMs: number | null; errorCode: string | null;
};
export type TracePhase = "waiting" | "generating" | "personas" | "synthesis" | "pdf" | "done" | "failed";
export type TraceState = {
  lastEventId: number; phase: TracePhase; startedAt: string | null; endedAt: string | null;
  personas: PersonaRow[];            // persona_index szerint rendezve
  inputTokens: number; outputTokens: number; retryCount: number;
  synthesisFailed: boolean; failureCode: string | null;
};
export function initialTraceState(): TraceState;
export function applyEvent(state: TraceState, event: TraceEvent): TraceState;   // tiszta, nem módosítja a bemenetet
export function countByStatus(state: TraceState): { queued: number; running: number; completed: number; failed: number };
```

- Produces (`lib/cost.ts`): `type Price = { input_per_million_usd: number; output_per_million_usd: number }`; `estimateCostUsd(inputTokens: number, outputTokens: number, price: Price): number`; `formatCostUsd(value: number): string` (pl. `"~$0.012"`, három tizedes).
- Produces (`components/trace-view.tsx`): `TraceView({ topic, state, now, price, banner? })` – csak kirajzol, lekérdezést nem tartalmaz. A `now` ezredmásodperc; a futó sorok és a fejléc órája ebből számol.
- Produces (`components/live-trace.tsx`): `LiveTrace({ runId })`.
- Produces: `GET /api/runs/[id]/events?after=<n>` (Next route handler).
- Megszűnik: `NEXT_PUBLIC_API_URL`, a `@tanstack/react-query` függőség.

**Az `applyEvent` szabályai:**

| Esemény | Hatás |
|---|---|
| bármi, `id <= lastEventId` | az állapot változatlan (ugyanaz az objektum) |
| `run_started` | `phase = "generating"`, `startedAt = at` |
| `personas_generated` | `phase = "personas"`, tokenek hozzáadva |
| `persona_started` | új sor `running`, `attempt = 1`, `startedAt = at` |
| `persona_retry` | a sor `attempt` és `errorCode` mezője frissül, `retryCount + 1` |
| `persona_completed` | a sor `completed`, `durationMs`, `attempt`, `errorCode = null`; tokenek hozzáadva |
| `persona_failed` | a sor `failed`, `durationMs`, `attempt`, `errorCode`; tokenek hozzáadva |
| `synthesis_started` | `phase = "synthesis"` |
| `synthesis_completed` | `phase = "pdf"`, tokenek hozzáadva |
| `synthesis_failed` | `phase = "pdf"`, `synthesisFailed = true` |
| `run_completed` | `phase = "done"`, `endedAt = at` |
| `run_failed` | `phase = "failed"`, `endedAt = at`, `failureCode = error_code ?? null` |
| ismeretlen típus | csak a `lastEventId` nő |

`countByStatus`: `queued = TOTAL_PERSONAS − personas.length`, de csak `personas` fázisban; más fázisban 0.

**A `LiveTrace` viselkedése:**
- Indulástól 1000 ms-onként kéri a `/api/runs/<id>/events?after=<lastEventId>` címet; a következő kérés csak az előző válasza után indul (nincs átfedés). A kapott eseményeket sorban adja az `applyEvent`-nek.
- `document.visibilitychange` → ha a fül láthatóvá válik, azonnal lekér.
- Három egymás utáni sikertelen kérés (hálózati hiba vagy nem 2xx, a 404 kivételével): hibaüzenet és link a `/minta` oldalra; az utolsó állapot kint marad, a lekérdezés megáll.
- `404`: „nem találjuk ezt a futást” üzenet, link az űrlapra; a lekérdezés megáll.
- `phase === "done"`: `router.replace("/eredmeny/<id>")`. `phase === "failed"`: hibapanel a `failureCode`-hoz tartozó szöveggel, link a `/minta` oldalra és az űrlapra; a lekérdezés megáll.
- A `now`-t egy 1000 ms-os időzítő frissíti, amíg a fázis nem végállapot.

**Elrendezés (spec 8. szakasz):** fejléc a kérdéssel, a futó órával és a négy fázissal (personák generálása → 18 persona → szintézis → PDF; az aktuális kiemelve, a kész pipálva); összesítő sor (sorban áll / fut / kész / kiesett darabszám, bemeneti és kimeneti token, becsült költség „becslés” jelöléssel); alatta 18 sor (név, állapot, eltelt idő, kísérlet `n/3`, hibánál a hibakód). A még el nem indult personák sora név nélkül, „sorban áll” felirattal jelenik meg. Mobilon egy oszlop. A színek a `lib/tokens.ts`-ből jönnek.

- [x] **Step 1: Írd meg a bukó `trace` és `cost` teszteket**

`trace.test.ts`, egy `ev(id, type, extra?)` segéddel:

- a táblázat minden sorára egy teszt a pontos várt mezőkkel;
- `applyEvent` nem módosítja a bemenő állapotot (`Object.freeze`-elt állapottal sem dob);
- **Review Focus 2:** ugyanaz az eseménysor kétszer lejátszva ugyanazt az állapotot adja, mint egyszer (`inputTokens`, `retryCount`, `personas.length` nem duplázódik); a duplikált eseményre visszakapott objektum `toBe` az eredeti;
- egy teljes rögzített sor (run_started, personas_generated 120/900 tokennel, 18 persona, közülük egy retry-jal és egy kiesővel, synthesis_completed, run_completed) után: `phase === "done"`, `countByStatus` `{queued: 0, running: 0, completed: 17, failed: 1}`, `retryCount === 1`, a tokenek a sor összege;
- `personas` fázisban 5 elindított personánál `queued === 13`;
- a `personas` tömb `index` szerint rendezett akkor is, ha a `persona_started` események nem sorrendben jönnek.

`cost.test.ts`: `estimateCostUsd(1_000_000, 2_000_000, {input_per_million_usd: 0.5, output_per_million_usd: 1.5}) === 3.5`; 0 tokenre 0; `formatCostUsd(0.0123) === "~$0.012"`.

- [x] **Step 2: Írd meg a bukó route handler és `start-run` teszteket**

`route.test.ts` (a `fetch` mockolva, `API_URL` és `INTERNAL_SECRET` beállítva):

- a hívás a `http://backend.test/api/v1/runs/<id>/events?after=41` címre megy `X-Internal-Secret` fejléccel, és a backend törzse és státusza változatlanul megy tovább (200 és 404);
- nem UUID azonosító: `404`, `{code: "RUN_NOT_FOUND"}`, a `fetch` nem hívódik;
- `after` hiányzik → `0`; `after=abc` vagy `after=-3` → `400`, `{code: "INVALID_INPUT"}`, a `fetch` nem hívódik;
- a `fetch` dob → `502`, `{code: "BACKEND_UNAVAILABLE"}`;
- a válasz `Cache-Control` fejléce `no-store`.

`start-run.test.ts` új esetei: az action a kérés `x-forwarded-for: 203.0.113.7, 10.0.0.1` fejlécéből `X-Client-IP: 203.0.113.7`-et küld (a `next/headers` mockolva); fejléc nélkül nincs `X-Client-IP`; a backend `429 {code: "DAILY_LIMIT_REACHED"}` válaszára `{ok: false, code: "DAILY_LIMIT_REACHED"}`; `500`-as, nem JSON törzsű válaszra `RUN_START_FAILED`; időtúllépésre (`AbortError`) `RUN_START_FAILED`.

- [x] **Step 3: Írd meg a bukó komponensteszteket**

`trace-view.test.tsx`: a fenti teljes sor állapotával a 18 sorból 17 „kész”, 1 „kiesett” a hibakódjával; a retry-os sor `2/3`-at mutat; az összesítőben megjelenik a `formatCostUsd` értéke és a „becslés” szó; `personas` fázisban 13 „sorban áll” sor van; `jest-axe` nem talál kritikus hibát.

`live-trace.test.tsx` (hamis időzítőkkel, mockolt `fetch`-csel és `next/navigation`-nel):

- az első kérés `after=0`, a második a legnagyobb kapott `id`-val megy;
- **Review Focus 2:** ha az első válasz a teljes kész futást hozza, a komponens `router.replace("/eredmeny/<id>")`-t hív, és nem kér többet;
- **Review Focus 3:** egy `visibilitychange` esemény (`document.visibilityState === "visible"`) után azonnal megy kérés, az 1000 ms kivárása nélkül;
- három egymás utáni hibás válasz után megjelenik a hibaüzenet és a `/minta` link, negyedik kérés nincs; egy közbeeső sikeres válasz nullázza a számlálót;
- `404` után egyetlen kérés történt, és a „nem találjuk” szöveg látszik;
- `run_failed` `TOO_FEW_PERSONAS` kóddal: a hibapanel a kódhoz tartozó szöveget mutatja, `router.replace` nem hívódik.

`research/page.test.tsx` új esetei: `IP_LIMIT_REACHED` és `DAILY_LIMIT_REACHED` kódnál a hibaüzenet mellett link jelenik meg a `/minta` oldalra, `BUSY`-nál nem; sikeres indítás után a gomb letiltva marad, és egy második beküldés nem hívja újra az actiont.

- [x] **Step 4: Futtasd, hogy elbukjon**

Run: `pnpm test`
Expected: FAIL (a `lib/trace` modul nem található)

- [x] **Step 5: Valósítsd meg a `lib` modulokat és a route handlert.** A route handler fájlban `export const dynamic = "force-dynamic"`.

- [x] **Step 6: Valósítsd meg a `TraceView`-t és a `LiveTrace`-t**, majd a `waiting/[run_id]/page.tsx`-et: nem UUID azonosítóra `notFound()`, különben `<LiveTrace runId={run_id} />`. Töröld a `waiting-screen` két fájlját és a `@tanstack/react-query` függőséget (`pnpm remove @tanstack/react-query`).

- [x] **Step 7: Igazítsd az indítást.** A `start-run.ts` a `backendFetch`-et és a `clientIp`-t használja. A `research/page.tsx` egy `submitted` állapottal tartja letiltva a gombot a sikeres indítás után, és a két keretkódnál linket mutat a mintára.

- [x] **Step 8: Szövegek.** `lib/errors.ts` új kódjai:

| Kód | Szöveg |
|---|---|
| `BUSY` | „Most két elemzés fut egyszerre. Próbáld újra egy perc múlva.” |
| `IP_LIMIT_REACHED` | „Erről a címről ma már három elemzés indult. Holnap újra próbálhatod; addig nézd meg a mintafutást.” |
| `DAILY_LIMIT_REACHED` | „A demó mai kerete betelt. Holnap újra próbálhatod; addig nézd meg a mintafutást.” |
| `RUN_NOT_FOUND` | „Nem találjuk ezt a futást.” |
| `TOO_FEW_PERSONAS` | „Túl kevés persona válaszolt, ezért az elemzés nem készült el.” |
| `PERSONA_GENERATION_FAILED` | „A personák generálása nem sikerült.” |
| `RUN_TIMED_OUT` | „A futás megszakadt, mielőtt elkészült volna.” |
| `INTERNAL_ERROR` | „Váratlan hiba történt a futás közben.” |

A `messages.waiting` blokk helyére `messages.trace` kerül (fázisnevek, állapotnevek, összesítő címkék, a „kapcsolat megszakadt” üzenet, linkszövegek). A régi `waiting` kulcsok törlődnek.

- [x] **Step 9: Környezet.** A `frontend/.env.example`-ből és a helyi `.env.local`-ból kikerül a `NEXT_PUBLIC_API_URL` (`sed -i '/^NEXT_PUBLIC_API_URL=/d' frontend/.env.local`).

- [x] **Step 10: Futtasd, hogy átmenjen**

Run: `pnpm lint && pnpm exec tsc --noEmit && pnpm test && pnpm build && grep -rn "NEXT_PUBLIC_API_URL\|react-query" app components lib`
Expected: mind zöld, a `grep` nem talál semmit.

- [x] **Step 11: Commit**

```bash
git add frontend
git commit -m "feat(frontend): live trace over a next route handler"
```

---

### Task 5: Eredmény tárolása és eredményoldal

**Files:**
- Modify: `backend/app/db.py`, `backend/app/services/run_processor.py`, `backend/app/routers/runs.py`, `backend/app/models/run.py`, `backend/app/core/errors.py`, a hozzájuk tartozó tesztek
- Create: `frontend/app/eredmeny/[id]/page.tsx`, `frontend/components/result-view.tsx`, `frontend/components/result-view.test.tsx`, `frontend/lib/run.ts`, `frontend/lib/run.test.ts`
- Modify: `frontend/lib/messages.ts`

**Interfaces:**
- Produces (`db.py`):
  - `UPDATABLE_RUN_COLUMNS` bővül a `result` oszloppal; az `update_run` a `result` értékét `psycopg.types.json.Jsonb`-be csomagolja.
  - `count_events(run_id: str, type: str) -> int`
- Produces (`run_processor.py`): a `_build_result_payload` kimenete új kulcsot kap: `"failed_personas": [{"name": str, "error_code": str}]`. Sikeres vagy részleges futásnál a kimenet a `runs.result`-ba íródik; `failed` futásnál a `result` `NULL` marad.
- Produces: `GET /api/v1/runs/{run_id}` →

```json
{
  "run_id": "…", "status": "partial", "is_sample": false,
  "topic": "…", "audience": "…",
  "created_at": "…", "completed_at": "…", "duration_ms": 86500,
  "input_tokens": 16134, "output_tokens": 36335, "retry_count": 2,
  "price": {"input_per_million_usd": 0.0, "output_per_million_usd": 0.0},
  "result": { … a _build_result_payload kimenete … }
}
```

  `duration_ms`: `completed_at − created_at`, futó futásnál `null`. `retry_count`: a `persona_retry` események száma. `result`: `null`, ha a futás nem `completed` vagy `partial`. Hibák: `404 RUN_NOT_FOUND`, `503 SERVICE_UNAVAILABLE`.
- Produces (`frontend/lib/run.ts`, szerveroldali): `type RunDetail` (a fenti alak); `fetchRun(id: string): Promise<RunDetail | null>` – `null` a 404-re és a nem UUID azonosítóra; más hibánál dob.
- Produces (`components/result-view.tsx`): `ResultView({ run, children? })` – a `children` helyére kerül a 7. feladat e-mail-űrlapja.

**Az eredményoldal (spec 9. szakasz), fentről lefelé:** fejléc (kérdés, célközönség) → összefoglaló (`result.synthesis.summary`) és az állásfoglalások megoszlása (`result.stance_counts`, darabszámmal és sávval) → futásadatok (idő másodpercben, bemeneti és kimeneti token, becsült költség „becslés” jelöléssel, `n/18 persona válaszolt`, retry-k száma) és „Futás visszajátszása” link (`/eredmeny/<id>/visszajatszas`) → „PDF letöltése” (`/api/runs/<id>/pdf`) → az e-mail-kérés helye → „Mire nem jó” bekezdés és link a `/modszertan` oldalra. A personák részletes válaszai nincsenek az oldalon.

**Állapotok:** nincs ilyen futás → `notFound()`; `queued`, `running`, `composing` → `redirect("/waiting/<id>")`; `failed` → hibapanel, link a `/minta` oldalra és az űrlapra, PDF-link nélkül; `partial` szintézis nélkül (`result.synthesis === null`) → az összefoglaló helyén „A szintézis nem készült el; a personák válaszai a PDF-ben vannak.”; ha `result.failed_personas` nem üres → „16/18 persona válaszolt” alakú sor.

- [x] **Step 1: Írd meg a bukó backend teszteket**

`test_run_processor.py`:

- `test_completed_run_stores_result_payload`: a `runs.result` nem `None`; `result["stance_counts"] == {"support": 10, "reject": 5, "conditional": 3}`; `len(result["personas"]) == 18`; `result["synthesis"]["summary"]` egyezik a hamis LLM válaszával; `result["failed_personas"] == []`.
- `test_partial_run_result_lists_failed_personas`: két kieső persona → `failed_personas` két eleme `{"name", "error_code"}` kulcsokkal, és a teljes `result` JSON-ban nincs a `MARKER`.
- `test_synthesis_failure_result_has_null_synthesis`.
- `test_failed_run_has_no_result`.

`test_db.py`: a `result` oda-vissza egyezik (`update_run(..., result={"á": [1, 2]})` → `get_run`).

`test_runs.py`:

- `test_get_run_returns_detail`: kész futás két `persona_retry` eseménnyel → `retry_count == 2`, `duration_ms` a két időbélyeg különbsége, a `result` egyezik, a válaszban nincs `ip_hash` és nincs `pdf` kulcs.
- `test_get_run_running_has_null_result_and_duration`.
- `test_get_run_unknown_is_404`, `test_get_run_requires_secret`.

- [x] **Step 2: Futtasd, hogy elbukjon**

Run: `pytest tests -q`
Expected: FAIL

- [x] **Step 3: Valósítsd meg a backend részt.** A futás lezárása két lépés lesz: (1) `update_run` az eredménnyel, a számlálókkal, a szintézis-oszlopokkal és a tokenekkel, a státusz közben `composing` marad; (2) a végső státusz és a `completed_at`, majd a `run_completed` esemény. A két lépés közé a 6. feladat teszi a PDF-et.

- [x] **Step 4: Futtasd, hogy átmenjen**

Run: `pytest tests -q`
Expected: PASS

- [x] **Step 5: Írd meg a bukó frontend teszteket**

`run.test.ts`: nem UUID → `null`, `fetch` nélkül; 404 → `null`; 503 → dob; 200 → a törzs.

`result-view.test.tsx` egy `makeRun(overrides)` segéddel:

- teljes futás: megjelenik az összefoglaló, a három állásfoglalás darabszáma, „18/18 persona válaszolt”, a retry-k száma, a `formatCostUsd` értéke a „becslés” szóval; a PDF-link `href`-je `/api/runs/<id>/pdf`, a visszajátszásé `/eredmeny/<id>/visszajatszas`, a módszertané `/modszertan`;
- részleges futás két kiesővel: „16/18 persona válaszolt”;
- szintézis nélkül: a pótló mondat látszik, az összefoglaló címe nem;
- a personák érvei (`primary_argument`) nem jelennek meg az oldalon;
- `jest-axe` nem talál kritikus hibát.

- [x] **Step 6: Valósítsd meg a frontend részt** a fenti szerkezet és állapotok szerint. A szövegek a `messages.result` blokkba kerülnek. A „Mire nem jó” bekezdés állítása: az eredmény szintetikus personák válasza, nem valódi megkérdezés; hipotézisek gyors előszűrésére való, döntést megalapozó piackutatást nem vált ki.

- [x] **Step 7: Futtasd, hogy átmenjen**

Run: `pnpm lint && pnpm exec tsc --noEmit && pnpm test && pnpm build`
Expected: mind zöld.

- [x] **Step 8: Commit**

```bash
git add backend frontend
git commit -m "feat: store run result and add the result page"
```

---

### Task 6: PDF

**Files:**
- Create: `backend/app/services/pdf_service.py`, `backend/app/templates/report.html.j2`, `backend/app/assets/fonts/` (egy OFL-licencű, magyar ékezeteket tartalmazó fontcsalád normál és félkövér TTF-je a licencfájljával), `backend/tests/services/test_pdf_service.py`, `frontend/app/api/runs/[id]/pdf/route.ts`, `frontend/app/api/runs/[id]/pdf/route.test.ts`
- Modify: `backend/requirements.txt`, `backend/Dockerfile`, `backend/app/db.py`, `backend/app/services/run_processor.py`, `backend/app/routers/runs.py`, `backend/app/core/errors.py`, a hozzájuk tartozó tesztek, `.github/workflows/ci.yml`, `CLAUDE.md` (Parancsok)

**Interfaces:**
- Consumes: `runs.result` (5. feladat), `pricing.price_payload()` (3. feladat).
- Produces (`db.py`): `save_pdf(run_id: str, pdf: bytes) -> None`; `get_pdf(run_id: str) -> bytes | None`.
- Produces (`pdf_service.py`):
  - `render_report_html(run: dict[str, Any]) -> str` – tiszta függvény; a `run` a `db.get_run` sora. Jinja2 `Environment(autoescape=True)`.
  - `async def html_to_pdf(html: str) -> bytes` – hívásonként indít és zár le egy Chromiumot (`async_playwright`), A4, háttérnyomtatással.
  - `async def generate_pdf(run: dict[str, Any]) -> bytes` – a kettő együtt, `asyncio.wait_for(..., timeout=60)` alatt.
- Produces: `GET /api/v1/runs/{run_id}/pdf` → `200`, `Content-Type: application/pdf`, `Content-Disposition: attachment; filename="swarmsense-<az azonosító első 8 karaktere>.pdf"`. Ha a futás `completed` vagy `partial` és nincs tárolt PDF, a végpont legenerálja, elmenti, és azt adja vissza. Hibák: `404 RUN_NOT_FOUND`; `409 RUN_NOT_FINISHED` (nem végállapot vagy `failed`); `503 PDF_UNAVAILABLE` (a generálás nem sikerült).
- Produces: `GET /api/runs/[id]/pdf` (Next route handler) – a backend törzsét, státuszát, `Content-Type` és `Content-Disposition` fejlécét adja tovább; időkorlát 90 000 ms.

**A PDF tartalma (spec 9. szakasz), ebben a sorrendben:** címlap (kérdés, célközönség, dátum, „szintetikus elemzés” megjelölés) → konszenzus és top érvek → szintézis (ha nincs: „A szintézis nem készült el.”) → personák egyenként (név, szerep, állásfoglalás, a négy szöveges mező, a négy jellemző) → hogyan futott (idő, tokenek, becsült költség becslésként jelölve, `n/18`, a kiesett personák neve hibakóddal) → módszertan és korlátok (ugyanaz az állítás, mint az eredményoldal „Mire nem jó” bekezdésében).

**A futásban:** az eredmény mentése és a végső státusz közé kerül. A PDF hibája nem buktatja a futást: a kivétel típusa a naplóba megy, a futás `completed` vagy `partial` lesz PDF nélkül.

- [x] **Step 1: Rögzítsd a verziókat.** A `requirements.txt`-be `jinja2==3.1.*` és a `playwright` PyPI-n elérhető legfrissebb kiadása pontos verzióval. A `Dockerfile` alapképe `mcr.microsoft.com/playwright/python:v<ugyanez a verzió>-noble`; a meglévő rendszerfelhasználó-létrehozás helyett az image `pwuser` felhasználója fut; a `COPY` sorok kiegészülnek az `app/templates`, `app/assets` mappákkal (az `app` másolása már viszi őket) és a `seed` mappával (`COPY --chown=pwuser:pwuser seed ./seed`; a mappát a 10. feladat tölti meg, itt egy `.gitkeep` kerül bele). Helyben: `pip install -r requirements.txt && python -m playwright install chromium`.

- [x] **Step 2: Írd meg a bukó teszteket**

`test_pdf_service.py`, egy `make_run(**overrides)` segéddel, amely a `_build_result_payload` alakját követi:

```python
def test_html_contains_sections_and_hungarian_text():
    html = pdf_service.render_report_html(make_run(topic="Őszi árazás"))
    for needle in ["Őszi árazás", "Szintézis", "Hogyan futott", "Módszertan és korlátok"]:
        assert needle in html

def test_html_escapes_user_text():          # Review Focus 1
    html = pdf_service.render_report_html(make_run(topic='<script>alert(1)</script> & "idézet"'))
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html

def test_html_without_synthesis_says_so():
    html = pdf_service.render_report_html(make_run(synthesis=None))
    assert "A szintézis nem készült el." in html

def test_html_lists_failed_personas_with_code_only(): ...
def test_html_embeds_bundled_font():        # @font-face a csomagolt TTF-re mutat

def test_generate_pdf_smoke():              # valódi Chromium
    pdf = asyncio.run(pdf_service.generate_pdf(make_run(topic="Árvíztűrő tükörfúrógép")))
    assert pdf.startswith(b"%PDF-") and len(pdf) > 10_000
```

`test_run_processor.py`: `test_completed_run_stores_pdf` (a `pdf_service.generate_pdf` monkeypatch-elve `b"%PDF-fake"`-re → `db.get_pdf` ezt adja; a `run_completed` esemény a PDF mentése után íródik); `test_pdf_failure_keeps_run_completed` (a generálás `RuntimeError("NYERS")`-t dob → a státusz `completed`, `db.get_pdf` `None`, a naplóban nincs `NYERS`); `test_failed_run_generates_no_pdf`. A fájl többi tesztjéhez egy autouse fixture hamisítja a `generate_pdf`-et, hogy ne induljon Chromium.

`test_runs.py`: tárolt PDF → `200`, a törzs bájtra egyezik, a két fejléc a megadott; hiányzó PDF kész futásnál → a (monkeypatch-elt) generálás egyszer fut, a második kérés már nem generál; a generálás hibája → `503 PDF_UNAVAILABLE`; futó vagy `failed` futás → `409 RUN_NOT_FINISHED`; ismeretlen azonosító → `404`; titok nélkül → `401`.

`route.test.ts` (frontend): a bináris törzs és a két fejléc változatlanul megy tovább; nem UUID → `404` `fetch` nélkül; a backend `503`-a kóddal együtt megy tovább; a `fetch` dob → `502 BACKEND_UNAVAILABLE`.

- [x] **Step 3: Futtasd, hogy elbukjon**

Run: `pytest tests/services/test_pdf_service.py -q`
Expected: FAIL (`ModuleNotFoundError: app.services.pdf_service`)

- [x] **Step 4: Valósítsd meg a sablont és a `pdf_service.py`-t.** A sablon önálló HTML: beágyazott CSS, a font `@font-face` szabálya `file://` útvonallal a csomagolt TTF-re mutat (az útvonalat a `render_report_html` adja át), külső hálózati hivatkozás nincs benne. A PDF-végpont `async def`, és közvetlenül `await`-eli a `generate_pdf`-et.

- [x] **Step 5: Kösd be a futásba és a végpontba**, majd írd meg a Next route handlert.

- [x] **Step 6: CI.** A `ci.yml` backend feladatába a függőségek telepítése után: `python -m playwright install --with-deps chromium`. A `CLAUDE.md` „Parancsok” blokkjába a `pip install` sor után: `python -m playwright install chromium`.

- [x] **Step 7: Futtasd, hogy átmenjen**

Run: `pytest tests -q` (backend), `pnpm lint && pnpm exec tsc --noEmit && pnpm test && pnpm build` (frontend), `docker build -t swarmsense-backend-test backend`
Expected: mind zöld; az image felépül.

- [x] **Step 8: Nézd meg a PDF-et.** Generálj egyet a teszt `make_run` adatával egy fájlba a scratchpad mappába, és nyisd meg: az ő és az ű helyesen jelenik meg, a szakaszok nem törnek ketté értelmetlenül. A jelentésbe írd le, mit láttál, és a fájl méretét (a spec 16. szakasza szerint a PDF mérete eddig ismeretlen; az érték a `TRACKING.md` „Megfigyelések” részébe kerül).

- [x] **Step 9: Commit**

```bash
git add backend frontend .github CLAUDE.md TRACKING.md
git commit -m "feat: generate the report pdf and serve it through next"
```

---

### Task 7: E-mail a PDF-fel

**Files:**
- Create: `backend/app/services/email_service.py`, `backend/tests/services/test_email_service.py`, `frontend/app/actions/request-email.ts`, `frontend/app/actions/request-email.test.ts`, `frontend/components/email-request-form.tsx`, `frontend/components/email-request-form.test.tsx`
- Modify: `backend/app/core/config.py`, `backend/app/core/errors.py`, `backend/app/db.py`, `backend/app/routers/runs.py`, `backend/app/models/run.py`, `backend/tests/conftest.py`, `backend/tests/routers/test_runs.py`, `backend/tests/test_db.py`, `backend/.env.example`, `frontend/app/eredmeny/[id]/page.tsx`, `frontend/lib/run.ts` (a `RunDetail` új mezője: `emails_remaining: number`), `frontend/lib/errors.ts`, `frontend/lib/messages.ts`

**Interfaces:**
- Produces (`config.py`): `resend_api_key: str = ""`, `email_from: str = ""`, `public_base_url: AnyHttpUrl = "http://localhost:3000"`, `emails_per_run: int = 3`, `emails_per_day: int = 30`.
- Produces (`db.py`):
  - `create_email_request(run_id: str, email: str) -> int`
  - `mark_email_sent(request_id: int) -> None`
  - `count_email_requests(*, run_id: str | None = None, hours: int | None = None) -> int`
- Produces (`email_service.py`):
  - `class EmailSendError(Exception)` – üzenete csak a HTTP-státusz vagy a kivétel típusneve.
  - `build_email(*, topic: str, run_id: str) -> tuple[str, str]` – tárgy és HTML törzs. A törzs: a kérdés (`html.escape`-pel), az eredmény linkje (`<public_base_url>/eredmeny/<run_id>`), és egy mondat arról, hogy a levelet az oldalon kérték, és más levél nem jön.
  - `send_report_email(*, to: str, topic: str, run_id: str, pdf: bytes) -> None` – `POST https://api.resend.com/emails`, `Authorization: Bearer <kulcs>`, `User-Agent: swarmsense/0.1`, JSON törzs: `from`, `to: [cím]`, `subject`, `html`, `attachments: [{"filename": "swarmsense-<id8>.pdf", "content": <base64>}]`. Időkorlát 30 mp. A tényleges HTTP-hívás egy modulszintű `_post_resend(payload: dict) -> None` függvényben van, hogy a tesztek azt cserélhessék.
- Produces: `POST /api/v1/runs/{run_id}/email`, törzs `{"email": "…"}` (`extra="forbid"`) → `200 {"status": "sent", "emails_remaining": <int>}`.

  Ellenőrzések sorrendben: cím érvényessége → `422 INVALID_EMAIL`; a futás létezik → `404 RUN_NOT_FOUND`; `completed` vagy `partial` → különben `409 RUN_NOT_FINISHED`; a kulcs és a feladó be van állítva → különben `503 EMAIL_NOT_CONFIGURED`; futásonkénti keret → `429 EMAIL_RUN_LIMIT_REACHED`; napi keret → `429 EMAIL_DAILY_LIMIT_REACHED`; PDF megvan vagy legenerálható → különben `503 PDF_UNAVAILABLE`. Ezután sor az `email_requests`-be, küldés, `sent_at`. A küldés hibája: `502 EMAIL_SEND_FAILED`; a sor `sent_at` nélkül megmarad, és beleszámít a keretbe.
- A `GET /api/v1/runs/{run_id}` válasza új mezőt kap: `"emails_remaining": int` (`emails_per_run` mínusz a futás eddigi kérései, legalább 0).
- Produces (frontend): `requestEmailAction(input: { runId: string; email: string }): Promise<{ ok: true; emailsRemaining: number } | { ok: false; code: string }>` – soha nem dob; `EmailRequestForm({ runId, emailsRemaining })`.

**Cím érvényessége:** a `pydantic` `EmailStr` típusa, legfeljebb 254 karakter. A FastAPI alapértelmezett 422-es válasza helyett a végpont `INVALID_EMAIL` kódot ad (a kérésmodell validálása a végponton belül történik, vagy a modell saját kivételkezelőt kap; az e-mail-cím a hibaválaszban és a naplóban nem jelenik meg).

- [x] **Step 1: Nézd meg a Resend küldő API aktuális dokumentációját** (Context7), és vesd össze a fenti kérésalakkal. Eltérésnél a dokumentáció az irányadó; az eltérést írd a jelentésbe.

- [x] **Step 2: Írd meg a bukó backend teszteket**

`conftest.py`: új autouse fixture `no_real_email`, amely az `app.services.email_service._post_resend`-et `AssertionError`-t dobó függvényre cseréli; a `settings_env` beállítja a `SWARMSENSE_RESEND_API_KEY=test-resend-key` és a `SWARMSENSE_EMAIL_FROM=demo@example.test` változót.

`test_email_service.py`:

- `test_build_email_escapes_topic` (**Review Focus 1**): `topic='<b>x</b> & y'` → a törzsben `&lt;b&gt;x&lt;/b&gt; &amp; y`, és a link `http://localhost:3000/eredmeny/<id>`.
- `test_send_posts_expected_payload`: a `_post_resend` rögzítő hamisítvány; a `to` egyelemű lista, a csatolmány `content`-je base64-ből visszafejtve egyenlő a PDF bájtjaival, a `from` a beállított feladó.
- `test_send_error_message_has_no_provider_text`: a hamisítvány `EmailSendError`-t dob; a hívó felé menő kivétel szövegében nincs a cím.

`test_runs.py` (a `send_report_email` monkeypatch-elve rögzítő hamisítványra, a futás kész, tárolt PDF-fel):

- siker: `200`, `emails_remaining == 2`, az `email_requests` sor `sent_at`-ja ki van töltve, a hamisítvány egyszer hívódott;
- **Review Focus 5**, paraméterezve: `"a@b.hu\nBcc: x@y.hu"`, `"a@b.hu, c@d.hu"`, `"nem-cím"`, 255 karakteres cím → `422 INVALID_EMAIL`, nincs sor, nincs küldés, a válasz törzsében nincs benne a beküldött szöveg;
- a negyedik kérés ugyanarra a futásra → `429 EMAIL_RUN_LIMIT_REACHED`, nincs negyedik sor;
- 30 kérés 24 órán belül más futásokra → `429 EMAIL_DAILY_LIMIT_REACHED`; a 25 órás kérések nem számítanak;
- futó futás → `409`; ismeretlen → `404`; üres `SWARMSENSE_RESEND_API_KEY` → `503 EMAIL_NOT_CONFIGURED`, nincs sor;
- a küldés `EmailSendError`-t dob → `502 EMAIL_SEND_FAILED`, a sor megvan `sent_at` nélkül;
- a naplóban (`caplog`) egyik esetben sem szerepel az e-mail-cím;
- a `GET /api/v1/runs/<id>` `emails_remaining` értéke két kérés után `1`.

- [x] **Step 3: Futtasd, hogy elbukjon**

Run: `pytest tests -q`
Expected: FAIL

- [x] **Step 4: Valósítsd meg a backend részt.** A `_post_resend` `urllib`-bel küld, ahogy az `llm_client._post_json_sync`; a hibaágai csak státuszkódot és típusnevet visznek tovább. Az `.env.example` öt új nevet kap; a `SWARMSENSE_EMAIL_FROM` értéke ott `swarmsense@example.com`.

- [x] **Step 5: Futtasd, hogy átmenjen**

Run: `pytest tests -q`
Expected: PASS

- [x] **Step 6: Írd meg a bukó frontend teszteket**

`request-email.test.ts`: a hívás `POST /api/v1/runs/<id>/email` a titokkal; siker → `{ok: true, emailsRemaining: 2}`; a backend kódja változatlanul jön vissza (`EMAIL_RUN_LIMIT_REACHED`); nem UUID vagy üres cím → `INVALID_EMAIL`, `fetch` nélkül; a `fetch` dob → `EMAIL_SEND_FAILED`.

`email-request-form.test.tsx`: `emailsRemaining === 0` → a gomb letiltva, mellette a „Erre a futásra már nem kérhető több levél.” szöveg; siker után megerősítő üzenet és a mező kiürül; hibakódnál a `lib/errors.ts` szövege `role="alert"`-tel; küldés közben a gomb letiltva; az űrlap alatt látszik a megjegyzés a 14 napos törlésről, linkkel az adatkezelési oldalra.

- [x] **Step 7: Valósítsd meg a frontend részt**, és tedd az űrlapot az eredményoldalra a `ResultView` `children`-jeként. Új szövegek a `lib/errors.ts`-ben:

| Kód | Szöveg |
|---|---|
| `INVALID_EMAIL` | „Ez nem tűnik érvényes e-mail-címnek.” |
| `EMAIL_RUN_LIMIT_REACHED` | „Erre a futásra már nem kérhető több levél.” |
| `EMAIL_DAILY_LIMIT_REACHED` | „A mai levélkeret betelt. A PDF-et az oldalról le tudod tölteni.” |
| `EMAIL_SEND_FAILED` | „A levél küldése nem sikerült. A PDF-et az oldalról le tudod tölteni.” |
| `EMAIL_NOT_CONFIGURED` | „A levélküldés ezen a példányon nincs beállítva. A PDF-et az oldalról le tudod tölteni.” |
| `PDF_UNAVAILABLE` | „A PDF most nem készíthető el. Próbáld újra egy perc múlva.” |
| `RUN_NOT_FINISHED` | „Ez a futás még nem készült el.” |

- [x] **Step 8: Futtasd, hogy átmenjen**

Run: `pnpm lint && pnpm exec tsc --noEmit && pnpm test && pnpm build`
Expected: mind zöld.

- [x] **Step 9: Commit**

```bash
git add backend frontend
git commit -m "feat: send the report pdf by email on request"
```

---

### Task 8: Takarítás, Discord-értesítés, lekérdezések

**Files:**
- Create: `backend/app/services/notifier.py`, `backend/app/services/cleanup.py`, `backend/tests/services/test_notifier.py`, `backend/tests/services/test_cleanup.py`, `docs/lekerdezesek.md`
- Modify: `backend/app/core/config.py`, `backend/app/db.py`, `backend/app/main.py`, `backend/app/services/run_processor.py`, `backend/app/routers/runs.py`, `backend/tests/conftest.py`, a hozzájuk tartozó tesztek, `backend/.env.example`

**Interfaces:**
- Produces (`config.py`): `discord_webhook_url: str = ""`.
- Produces (`db.py`):
  - `finalize_run(run_id: str, **fields: Any) -> bool` – ugyanaz, mint az `update_run`, de csak akkor ír, ha a sor státusza `running` vagy `composing`; a visszaadott érték megmondja, írt-e.
  - `delete_old_email_requests(*, days: int = 14) -> int` – a törölt sorok száma.
  - `fail_stuck_runs(*, minutes: int = 10) -> list[str]` – `failed`-re állítja (`completed_at = now()`) a `queued`, `running`, `composing` státuszú, `minutes` percnél régebben létrehozott, nem minta futásokat; a visszaadott érték az azonosítók listája.
- Produces (`notifier.py`):
  - `notify_run_failed(run_id: str, error_code: str) -> None` – üzenet: futásazonosító, hibakód, link (`<public_base_url>/eredmeny/<run_id>`).
  - `notify_daily_limit_reached() -> None`
  - Mindkettő a modulszintű `_post_discord(content: str) -> None`-t hívja. Üres webhook-cím → nem történik semmi. Bármely hiba → egy `swarmsense.notify` naplósor a kivétel típusával; kivétel nem megy tovább.
- Produces (`cleanup.py`):
  - `run_cleanup_once() -> dict[str, int]` – `{"deleted_emails": n, "failed_runs": m}`; minden megszakított futásra `run_failed` eseményt ír `RUN_TIMED_OUT` kóddal, és értesít.
  - `async def cleanup_loop(*, interval_seconds: float = 3600) -> None` – azonnal fut egyszer, utána `interval_seconds`-enként; a `run_cleanup_once`-ot `asyncio.to_thread`-del hívja; a körön belüli kivétel a naplóba megy (típusnévvel), a ciklus megy tovább.
- A `lifespan` a sémaalkalmazás után `asyncio.create_task(cleanup_loop())`-ot indít, leálláskor `cancel()`-t hív rá, és megvárja.

**Hol megy értesítés:** a `_fail_run`-ban (minden bukási úton); a takarítóban megszakított futásonként; a futás létrehozása után, ha az elmúlt 24 óra futásszáma éppen elérte a `runs_per_day` értéket (így a keret betelése egyszer jelez, nem minden elutasított kérésnél).

- [x] **Step 1: Írd meg a bukó teszteket**

`conftest.py`: autouse `no_real_discord`, amely az `app.services.notifier._post_discord`-ot `AssertionError`-t dobóra cseréli.

`test_notifier.py`:

- üres webhook → a `_post_discord` nem hívódik (az autouse tiltás mellett sem dob);
- beállított webhook → az üzenetben benne van a futásazonosító, a hibakód és a link; nincs benne a kérdés szövege (a teszt létrehoz egy futást `topic="TITKOS-TEMA"` értékkel, és ezt keresi);
- a `_post_discord` `OSError("nyers")`-t dob → a `notify_run_failed` nem dob, a naplóban `OSError` szerepel, `nyers` nem.

`test_cleanup.py`:

- 15 napos `email_requests` sor törlődik, a 13 napos marad; a visszaadott számláló 1;
- 11 perces `running` futás `failed` lesz `completed_at`-tal, utolsó eseménye `run_failed` `RUN_TIMED_OUT` kóddal, és ment értesítés; a 9 perces `running`, a 11 perces `completed` és a 11 perces minta futás érintetlen;
- **Review Focus 4:** `test_late_finish_does_not_revive_timed_out_run` – a hamis LLM szintézishívása közben a teszt `db.fail_stuck_runs(minutes=0)`-t hív; a `process_run` végén a futás `failed`, nincs `run_completed` esemény, és a `finalize_run` `False`-t adott;
- `test_cleanup_loop_survives_a_failing_round`: a `run_cleanup_once` első hívása dob, a második fut (`interval_seconds=0`, a teszt két kör után megszakítja a feladatot).

`test_db.py`: `finalize_run` `True`-t ad `composing` sorra és ír; `False`-t ad `failed` sorra és nem ír; ismeretlen oszlopra `ValueError`.

`test_run_processor.py`: mindhárom bukási úton pontosan egy `notify_run_failed` hívás a megfelelő kóddal; sikeres futásnál nincs hívás.

`test_runs.py`: `SWARMSENSE_RUNS_PER_DAY=2` mellett a második futás létrehozása után egy `notify_daily_limit_reached` hívás; az első után nincs; a harmadik (elutasított) kérésnél nincs újabb.

`tests/test_main.py` (új) vagy a meglévő indulási teszt mellé: az alkalmazás indulásakor a takarító egyszer lefut (a `run_cleanup_once` rögzítő hamisítványra cserélve), leálláskor a feladat megszakad.

- [x] **Step 2: Futtasd, hogy elbukjon**

Run: `pytest tests -q`
Expected: FAIL

- [x] **Step 3: Valósítsd meg** az Interfaces szerint. A futásfeldolgozó végső státuszírása `finalize_run`-ra vált; ha `False`-t ad, a `run_completed` esemény és a PDF-mentés kimarad, és a naplóba egy sor kerül a futásazonosítóval.

- [x] **Step 4: Írd meg a `docs/lekerdezesek.md`-t** három lekérdezéssel (spec 10. szakasz): mai futások státusz szerint; napi tokenösszeg az elmúlt 14 napra; a leggyakoribb hibakódok a `run_events`-ből az elmúlt 7 napra. Mindegyik fölé egy mondat arról, mire való, és a futtatás módja (`docker compose … exec postgres psql -U swarmsense`).

- [x] **Step 5: Futtasd, hogy átmenjen**

Run: `pytest tests -q`
Expected: PASS

- [x] **Step 6: Commit**

```bash
git add backend docs/lekerdezesek.md
git commit -m "feat(backend): hourly cleanup and discord notifications"
```

---

### Task 9: Adatkezelés, módszertan, feltételek, landing

**Files:**
- Create: `frontend/app/modszertan/page.tsx`, `frontend/app/modszertan/page.test.tsx`, `frontend/app/privacy/page.test.tsx`
- Modify: `frontend/lib/messages.ts`, `frontend/app/privacy/page.tsx`, `frontend/app/terms/page.tsx`, `frontend/app/page.tsx`, `frontend/app/page.test.tsx`, `frontend/app/layout.tsx`, `frontend/lib/tokens.ts`, `frontend/.env.example`
- Delete: `frontend/components/ui/button.tsx`, `frontend/public/{file,globe,next,vercel,window}.svg` (előtte `grep`-pel ellenőrizve, hogy nincs hivatkozásuk), a `lib/tokens.ts` `email*` konstansai és a React Emailre utaló megjegyzése

**Interfaces:**
- Consumes: a 4., 5. és 7. feladat útvonalai (`/minta` a 10. feladatban jön létre; a link már most kikerül).
- Produces: `/modszertan` oldal; a kapcsolattartási cím a `CONTACT_EMAIL` környezeti változóból jön (szerveroldali komponens olvassa). Ha nincs beállítva, az oldalak a „Kapcsolat: a repo issue-követőjén” mondatot mutatják cím helyett.

Ebben a feladatban a pontos szöveget az implementáló írja; a terv azt rögzíti, **mit kell állítania és mit nem állíthat** az egyes oldalaknak. A kész szöveget Balázs a terv végén átolvassa.

**Adatkezelési tájékoztató – kötelező állítások (spec 9. szakasz):**

1. Regisztráció és fiók nincs; az oldal nem használ sütit és webanalitikát.
2. A kérdés és a célközönség szövege korlátlan ideig megmarad, és a futás linkjének birtokában bárki láthatja; ezért ne írj bele személyes adatot vagy üzleti titkot.
3. A kérdés szövege az opencode-on keresztül a DeepSeek modelljéhez kerül feldolgozásra.
4. IP-cím nyersen nem tárolódik; a visszaélések korlátozásához egy kulcsolt lenyomata (HMAC) kerül a futás mellé.
5. E-mail-cím csak akkor kerül hozzánk, ha a PDF-et levélben kéred; egyetlen levél megy, a cím 14 nap után törlődik az adatbázisból. A levelet a Resend küldi, amelynek saját naplója ettől független.
6. Hibaértesítés megy egy Discord-csatornára futásazonosítóval és hibakóddal; a kérdés szövege és e-mail-cím nem.
7. Érintetti jogok és a NAIH elérhetősége (a meglévő szöveg megtartható); törlési kérés a kapcsolattartási címen, a futás linkjével.

**Törlendő a régiből:** mágikus link, hozzájárulási jelölőnégyzet, follow-up és marketing levelek, leiratkozás, várólista, költségadatok, SLA-ígéretek (15 perc, 7 nap), a `deletionEmailTemplates` blokk.

**Felhasználási feltételek:** kimarad a 3. (regisztráció, e-mail, hitelesítés) és a 8. (díjazás) szakasz, a bevezető második bekezdése és minden mondat, amely e-mailes kézbesítést, próbaidőszakot vagy fizetős csomagot említ. Új mondat: ez egy bemutató célú, ingyenes demó, napi keretekkel, rendelkezésre állási vállalás nélkül. A 6. szakasz (nem tanácsadás, nem reprezentatív felmérés) marad.

**Módszertan (`/modszertan`) – kötelező tartalom:**

1. Mi történik egy futásban: egy LLM-hívás 18 persona-leírást készít a megadott célközönségre; mind a 18 persona külön hívásban válaszol (egyszerre legfeljebb 5); egy utolsó hívás szintézist ír. Összesen 20 hívás.
2. Hibakezelés: sikertelen hívásnál legfeljebb 3 kísérlet; a séma szerint érvénytelen válasz kiesik; 12 válasz alatt a futás sikertelen; a szintézis hibájánál az eredmény szintézis nélkül készül el.
3. Mit jelentenek a számok: a tokenszám a szolgáltató által jelentett érték, a költség listaárból számolt becslés (a demó előfizetéses kereten fut, tényleges futásonkénti költség nincs).
4. Mire nem jó: a personák nem valódi emberek, a válaszok egy nyelvi modell kimenetei; az eredmény nem reprezentatív, ugyanarra a kérdésre futásonként más jöhet ki; hipotézisek előszűrésére való, döntést megalapozó piackutatást nem vált ki.
5. Link a mintafutásra.

**Landing – szabályok (CLAUDE.md B terv utolsó kritériuma):**

- A hero kiemelése „pár perc” marad (Balázs korábbi döntése).
- Tilos állítás (a `page.test.tsx` mindegyikre ellenőrzi, hogy nincs az oldalon): „90 másodperc”, „15-20”, „15–20”, „Megfizethető ár”, „Ügynökségi büdzsé”, „A piackutatás még sosem volt ilyen egyszerű”, „e-mailben”, „Ingyenes próba”.
- Kötelező állítások: 18 szintetikus persona; a futás nagyjából másfél percig tart; regisztráció nélkül; az eredmény PDF-ben letölthető; a futás élőben követhető; ez egy portfóliódarab, amely nem vált ki valódi piackutatást (link a `/modszertan` oldalra).
- A „Minta megtekintése” gomb a `/minta` oldalra visz (ma `#sample` horgony).
- Az eredmény-előnézet blokk marad, de „Illusztráció” megjelölést kap, mert kitalált példaadat; a blokk alatti link a valódi mintafutásra mutat.
- A `painBridge` blokk három sora helyére: mit csinál a darab (élő trace, 18 persona 5-ös párhuzamossággal, PDF). A lábléc új linkje: Módszertan.
- A `layout.tsx` `metadata` szövegei ugyanezeket a szabályokat követik („percek alatt”, „várakozás nélkül” jellegű ígéret nélkül).

- [x] **Step 1: Írd meg a bukó teszteket**

- `page.test.tsx` (landing): a nyolc tiltott kifejezés egyike sincs a renderelt szövegben; megvan a „18” és a „portfólió” szó; van link a `/minta`, a `/modszertan`, a `/privacy` és a `/terms` oldalra; az előnézet blokkban látszik az „Illusztráció” szó; a meglévő axe-teszt marad.
- `privacy/page.test.tsx`: megvan a „14 nap”, a „DeepSeek”, a „Resend”, az „IP-cím” kifejezés; nincs benne „mágikus”, „várólista”, „leiratkoz”, „hozzájárulás”; `CONTACT_EMAIL=kapcsolat@example.test` mellett a cím megjelenik, nélküle a pótló mondat.
- `modszertan/page.test.tsx`: megvan a „18”, a „20 hívás”, a „legfeljebb 5”, a „nem reprezentatív” kifejezés és a link a `/minta` oldalra; axe.
- A feltételek oldalához egy teszt a `privacy` tesztfájl mellé: nincs benne „mágikus”, „előfizetés”, „e-mailben kézbesíti”.

- [x] **Step 2: Futtasd, hogy elbukjon**

Run: `pnpm test`
Expected: FAIL

- [x] **Step 3: Írd át a szövegeket és az oldalakat** a fenti szabályok szerint. A `privacy/page.tsx` szerkezete a megmaradó kulcsokhoz igazodik; a nem használt `messages.legal` kulcsok törlődnek. A hatálybalépés dátuma a commit napja, a verzió 2.0.

- [x] **Step 4: Takarítás.** `grep -rn "components/ui/button\|file.svg\|globe.svg\|next.svg\|vercel.svg\|window.svg\|emailCanvas\|emailSurface\|emailBorder\|emailText" frontend --include=*.ts --include=*.tsx --include=*.css` – ha nincs találat, a felsorolt fájlok és konstansok törlődnek; ha van, a találatot írd a jelentésbe, és az a fájl marad.

- [x] **Step 5: Futtasd, hogy átmenjen**

Run: `pnpm lint && pnpm exec tsc --noEmit && pnpm test && pnpm build`
Expected: mind zöld.

- [x] **Step 6: Commit**

```bash
git add frontend
git commit -m "feat(frontend): rewrite legal, methodology and landing copy"
```

---

### Task 10: Visszajátszás, minta és seed (kód)

**Files:**
- Create: `frontend/lib/replay.ts`, `frontend/lib/replay.test.ts`, `frontend/components/replay-trace.tsx`, `frontend/components/replay-trace.test.tsx`, `frontend/app/minta/page.tsx`, `frontend/app/eredmeny/[id]/visszajatszas/page.tsx`, `backend/scripts/export_sample.py`, `backend/tests/test_seed.py`, `backend/seed/.gitkeep` (ha a 6. feladat még nem hozta létre)
- Modify: `backend/app/db.py`, `backend/app/main.py`, `backend/app/routers/runs.py`, `backend/tests/routers/test_runs.py`, `frontend/lib/run.ts`, `frontend/lib/messages.ts`, a spec 8. szakasza, `TRACKING.md`

**Interfaces:**
- Produces (`db.py`):
  - `SEED_PATH = <backend>/seed/sample_run.sql`
  - `get_sample_run_id() -> str | None` – a legutóbb létrehozott `is_sample = true` futás azonosítója.
  - `seed_sample_if_missing() -> bool` – ha nincs minta és a `SEED_PATH` létezik, lefuttatja; a visszaadott érték megmondja, betöltött-e.
  - `export_sample_sql(run_id: str) -> str` – egy `runs` beszúrás (`is_sample = true`, `ip_hash = null`, `pdf` nélkül, az eredeti `id`-val és időbélyegekkel, `on conflict (id) do nothing`) és a futás eseményeinek beszúrásai `id` szerinti sorrendben, `id` oszlop nélkül, az eredeti `created_at` értékekkel. Az értékek `psycopg.sql.Literal`-lal kerülnek a szövegbe.
- Produces: `GET /api/v1/runs/sample` → `200 {"run_id": "…"}` vagy `404 SAMPLE_NOT_FOUND`. Az útvonal a routerben a `/{run_id}` útvonalak **előtt** áll.
- Produces (`scripts/export_sample.py`): `python -m scripts.export_sample <run_id>` → kiírja a `backend/seed/sample_run.sql`-t, és kiírja a futás összesítőjét (események típusonkénti darabszáma). Ha a futásban nincs `persona_retry` vagy nincs `persona_failed` esemény, hibaüzenettel és nem nulla kilépési kóddal áll meg, fájlt nem ír.
- Produces (`frontend/lib/replay.ts`):
  - `type ScheduledEvent = { event: TraceEvent; delayMs: number }` – a `delayMs` az első eseménytől mért késleltetés.
  - `buildSchedule(events: TraceEvent[]): ScheduledEvent[]` – az `at` időbélyegek különbsége szerint; az első esemény `delayMs`-e 0; azonos időbélyegű események sorrendje az `id` szerinti.
- Produces (`frontend/lib/run.ts`): `fetchSampleRunId(): Promise<string | null>`.
- Produces (`components/replay-trace.tsx`): `ReplayTrace({ runId })` – egyszer lekéri a `/api/runs/<id>/events?after=0` címet, és az ütemezés szerint adagolja az eseményeket az `applyEvent`-nek; ugyanazt a `TraceView`-t rajzolja, mint az élő futás.

**A visszajátszás viselkedése (spec 8. szakasz):**
- Felül címke: „Rögzített futás, <a futás dátuma>” és „Ugrás az eredményre” gomb (`/eredmeny/<id>`), amely végig látszik.
- A `TraceView` `now` értéke a virtuális óra: az első esemény időbélyege plusz a lejátszás kezdete óta eltelt valós idő. Így a futó sorok órája az eredeti tempóban jár.
- A végén az állapot kint marad, és megjelenik egy „Újra” gomb, amely elölről indítja.
- Ha a lekérés nem sikerül: hibaüzenet és link az űrlapra. Ha a futás még nem végállapotú: átirányítás a `/waiting/<id>` oldalra.
- `/minta`: szerveroldali komponens; `fetchSampleRunId()` → van: `<ReplayTrace runId=… />`; nincs: „A mintafutás most nem érhető el.” és link az űrlapra.
- `/eredmeny/[id]/visszajatszas`: nem UUID → `notFound()`; különben `<ReplayTrace runId=… />`.

- [x] **Step 1: Írd meg a bukó backend teszteket**

`test_seed.py`:

```python
def test_export_then_seed_roundtrip(clean_db):
    # egy futás eredménnyel, PDF-fel, ip_hash-sel és 5 eseménnyel (köztük retry és failed)
    sql_text = db.export_sample_sql(run_id)
    # truncate, majd a szöveg lefuttatása
    restored = db.get_run(run_id)
    assert restored["is_sample"] is True and restored["ip_hash"] is None
    assert restored["result"] == original["result"]
    assert db.get_pdf(run_id) is None
    assert [(e["type"], e["created_at"]) for e in db.list_events(run_id)] == original_events

def test_seed_runs_only_when_no_sample(clean_db, tmp_path, monkeypatch): ...
def test_seed_missing_file_is_noop(clean_db, monkeypatch): ...
def test_seed_is_idempotent(clean_db, tmp_path, monkeypatch): ...   # kétszer futtatva egy minta van
def test_export_text_with_quotes_and_accents_roundtrips(clean_db): ...  # topic: "O'Brien \"ő\" -- ; drop table runs"
```

`test_runs.py`: `GET /api/v1/runs/sample` minta nélkül `404 SAMPLE_NOT_FOUND`; mintával a legutóbbi azonosítót adja; titok nélkül `401`; a `GET /api/v1/runs/sample` nem a `{run_id}` útvonalra fut (a válasz nem `RUN_NOT_FOUND`). A minta `GET …/events` válaszában `is_sample` igaz. Indulási teszt: üres adatbázisnál és létező seed fájlnál az alkalmazás indulása után van minta.

A szkripthez: a retry vagy kieső nélküli futásra nem nulla kilépési kód, és nem jön létre fájl (a `SEED_PATH` a `tmp_path`-ra állítva).

- [x] **Step 2: Írd meg a bukó frontend teszteket**

`replay.test.ts`: három esemény `12:00:00.000`, `12:00:01.500`, `12:00:01.500` időbélyeggel → `delayMs` `[0, 1500, 1500]`, a sorrend az `id` szerinti; üres bemenetre üres kimenet; az időben visszafelé lépő esemény `delayMs`-e nem kisebb az előzőénél.

`replay-trace.test.tsx` (hamis időzítőkkel): pontosan egy `fetch` történik; 1499 ms-nál a második esemény még nincs feldolgozva, 1500 ms-nál igen; a címke a futás dátumát mutatja; az „Ugrás az eredményre” link `href`-je `/eredmeny/<id>` a lejátszás közben is; a végén megjelenik az „Újra” gomb, és megnyomása után az állapot a kezdeti; hibás lekérésnél a hibaüzenet látszik.

- [x] **Step 3: Futtasd, hogy elbukjon**

Run: `pytest tests -q` és `pnpm test`
Expected: FAIL mindkettő

- [x] **Step 4: Valósítsd meg a backend részt.** A `lifespan` sorrendje: `apply_schema()` → `seed_sample_if_missing()` → a takarító indítása. A seed hibája (pl. sérült fájl) nem állítja meg az indulást: a kivétel típusa a naplóba megy.

- [x] **Step 5: Valósítsd meg a frontend részt.**

- [x] **Step 6: Futtasd, hogy átmenjen**

Run: `pytest tests -q`; `pnpm lint && pnpm exec tsc --noEmit && pnpm test && pnpm build`
Expected: mind zöld.

- [x] **Step 7: Dokumentáld az eltérést** (a seed nem tartalmaz PDF-et): spec 8. szakasz egy mondat, `TRACKING.md` egy sor.

- [x] **Step 8: Commit**

```bash
git add backend frontend docs/superpowers/specs TRACKING.md
git commit -m "feat: replay recorded runs and seed the sample run"
```

---

### Task 11: A valódi mintafutás és a teljes ellenőrzés

Ez a feladat valódi LLM-hívásokat indít Balázs opencode Go keretéből. **Legfeljebb 8 futás indítható.** Ha addig nincs olyan futás, amelyben van retry és kiesett persona is, a feladat megáll, és a jelentés leírja, mi fordult elő; a folytatásról Balázs dönt. Az események hamisítása vagy kézi szerkesztése tilos (spec 8. szakasz).

**Files:**
- Create: `backend/seed/sample_run.sql`
- Modify: `TRACKING.md`, `CLAUDE.md`, a spec (ha a mérés eltérést hoz)

**Interfaces:**
- Consumes: minden korábbi feladat.

- [x] **Step 1: Indítsd el helyben a teljes rendszert.** Postgres a `docker-compose.dev.yml`-ből; a backend `python -m uvicorn app.main:app --port 8000`; a frontend `pnpm build && pnpm start` (éles build, nem `dev`). Ha a 3000-es port foglalt, a frontend a 3001-esen megy, és a backend folyamata `SWARMSENSE_PUBLIC_BASE_URL=http://localhost:3001`-et kap. A mintagyűjtés idejére a backend folyamata `SWARMSENSE_RUNS_PER_IP_PER_DAY=20`-at kap, hogy a keret ne állítsa meg.

- [x] **Step 2: Végigvitel a böngészőben** (Chrome, nyitott hálózati panellel). Űrlap → trace → eredmény → PDF letöltése → visszajátszás. Ellenőrizd és írd a jelentésbe:

- a hálózati forgalomban csak a Next címe szerepel (nincs kérés a 8000-es portra);
- a trace personánként mutat állapotot, kísérletszámot, időt; az összesítőben egyszerre legfeljebb 5 „fut”;
- a backend naplójában megjelent a futás összefoglaló sora (az A terv óta ez valódi futással nincs megerősítve);
- a Next naplójában szerepel-e a kérdés szövege éles buildnél (az A tervben fejlesztői módban szerepelt; az eredmény a `TRACKING.md` „Megfigyelések” részébe kerül, a teendő a C tervé);
- a letöltött PDF megnyílik, az ékezetek helyesek.

- [x] **Step 3: Keretek kézi ellenőrzése.** A backendet újraindítva `SWARMSENSE_RUNS_PER_IP_PER_DAY=1`, majd `SWARMSENSE_RUNS_PER_DAY=1`, majd `SWARMSENSE_MAX_CONCURRENT_RUNS=0` értékkel: az űrlap mindháromnál a megfelelő üzenetet adja, az első kettőnél linkkel a mintára. LLM-hívás ezekhez nem kell (a már meglévő futások betöltik a keretet).

- [x] **Step 4: Beragadt futás.** Indíts egy futást, és a persona-fázisban állítsd le a backendet. Írd át SQL-lel a futás `created_at`-ját 11 perccel korábbra (így nem kell 10 percet várni), indítsd újra a backendet, és nézd meg, hogy a nyitva hagyott trace oldal hibapanelre vált a `RUN_TIMED_OUT` szövegével.

- [x] **Step 5: E-mail.** Ha a helyi `.env`-ben van `SWARMSENSE_RESEND_API_KEY` és `SWARMSENSE_EMAIL_FROM`: kérj egy levelet Balázs által megadott címre, és erősítsd meg vele, hogy megérkezett a PDF-fel. Ha nincs beállítva: az űrlap az `EMAIL_NOT_CONFIGURED` szöveget adja; a levél tényleges megérkezése nyitott pontként a `TRACKING.md`-be kerül, és a CLAUDE.md megfelelő kritériuma nem pipálható ki.

- [x] **Step 6: A takarítás ellenőrzése adaton.** Szúrj be SQL-lel egy 15 napos `email_requests` sort, indítsd újra a backendet, és ellenőrizd, hogy a sor eltűnt.

- [x] **Step 7: A minta kiválasztása.** A 2–4. lépés futásai közül az, amelyikre a `python -m scripts.export_sample <run_id>` sikerrel lefut (van benne retry és kiesett persona). Ha egyik sem ilyen, indíts további futásokat különböző kérdésekkel a 8-as felső határig. A kiválasztott futás kérdése és célközönsége nem tartalmazhat személyes adatot vagy valódi cégnevet; ha tartalmaz, az nem lehet minta.

- [x] **Step 8: A seed ellenőrzése üres adatbázison.** Állítsd le a rendszert, töröld a dev adatbázis kötetét (`docker compose -f docker-compose.dev.yml down -v && … up -d`), indítsd el a backendet, és nyisd meg a `/minta` oldalt: a visszajátszás lefut, van benne retry és kiesett persona, az „Ugrás az eredményre” az eredményoldalra visz, és onnan a PDF letölthető (első kérésre generálódik).

- [x] **Step 9: Zárás a dokumentumokban.**

- `CLAUDE.md`: a B terv kritériumai közül azok pipálódnak ki, amelyekre a jelentésben van bizonyíték; a „Hol tart a projekt” bekezdés frissül.
- `TRACKING.md`: a 3–6. lépés és a B terv állapota; a „Most” sor; a megfigyelések (PDF mérete, a futások ideje és tokenszáma, hányadik futás adta a mintát, a Next napló kérdése); a nyitott pontok.
- A terv fájljában a checkboxok.

- [x] **Step 10: Teljes ellenőrzés és commit**

Run: `pytest tests -q` (backend); `pnpm lint && pnpm exec tsc --noEmit && pnpm test && pnpm build` (frontend); `grep -rn "localhost:8000\|NEXT_PUBLIC_API_URL" frontend/app frontend/components frontend/lib`
Expected: mind zöld; a `grep` legfeljebb szerveroldali fájlban vagy tesztben talál.

```bash
git add backend/seed TRACKING.md CLAUDE.md docs
git commit -m "feat: add the recorded sample run and close plan B"
```

---

## Önellenőrzés a spechez

| Spec | Hol valósul meg |
|---|---|
| 3. Architektúra (zárt backend, Server Action, route handler, kliens IP) | 2., 3., 4., 6., 7. feladat |
| 4. Adatmodell (`result`, `pdf`, `ip_hash`, `run_events`, `email_requests`) | 1., 2., 5., 6., 7. feladat; a séma már az A tervben létrejött |
| 5. Események és polling válasz | 1., 3. feladat |
| 6. Költségbecslés listaárból | 3. (ár), 4., 5., 6. feladat |
| 7. Keretek | 2. (futás), 7. (levél) feladat |
| 8. Trace és visszajátszás, minta, seed | 4., 10., 11. feladat |
| 9. Eredményoldal, PDF, e-mail, takarítás, adatkezelés | 5., 6., 7., 8., 9. feladat |
| 10. Hibakezelés, Discord, lekérdezések | 1., 4., 8. feladat; az Uptime Kuma beállítása a C tervé |
| 12. Tesztelés | minden feladat; a kézi lista a 11. feladat |
| 13. Backend image, CI Chromium | 6. feladat; a deploy compose a C tervé |
