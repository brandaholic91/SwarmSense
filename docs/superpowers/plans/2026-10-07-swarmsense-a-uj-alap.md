# SwarmSense A terv: Új alap – Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A régi funnel kódja törlődik, a megmaradó mag (futás indítása, 18 persona, szintézis, státusz) Supabase helyett sima Postgresen, OpenRouter helyett opencode Go-n fut, valódi Postgres ellen tesztelve.

**Architecture:** A backend minden adatbázis-műveletet a `backend/app/db.py`-n át végez `psycopg` 3 nyers SQL-lel; a sémát a `backend/schema.sql` adja, amit a backend induláskor lefuttat. Az LLM-kliens `LLMClient` néven opencode Go-t hív, és költség helyett tokenszámot ad vissza. A frontend két mezőből közvetlenül futást indít, és a meglévő várakozó képernyőre visz.

**Tech Stack:** Python 3.12, FastAPI, `psycopg` 3, pytest, Postgres 17 (Docker), Next.js 16, React 19, vitest, pnpm 9.

**Spec:** `docs/superpowers/specs/2026-10-07-swarmsense-portfolio-design.md` (ez a terv a 14. szakasz 1–2. lépését valósítja meg). A 0. lépés mérései: `TRACKING.md`.

**Előfeltétel:** a munka új ágon megy (`portfolio-plan-a`), a `portfolio-redesign-spec` ágról indítva, miután az ottani dokumentum-módosítások commitolva vannak.

## Mi nincs ebben a tervben

A B tervbe tartozik, itt szándékosan nem készül el:

- `run_events` írása, trace képernyő, `on_event` és `on_retry` callback (a táblák viszont már most létrejönnek).
- Keretek (IP, napi, egyidejű futás), `ip_hash`.
- `runs.result` és `runs.pdf` kitöltése, eredményoldal, PDF, e-mail, Discord.
- A böngésző → Next → backend proxy. **Átmeneti állapot:** a várakozó képernyő ebben a tervben még közvetlenül kérdezi a backendet, ezért a CORS és a `NEXT_PUBLIC_API_URL` marad. A B terv 3. lépése szünteti meg.
- A landing oldal és a jogi oldalak újraírása. Itt csak azok a mondatok változnak, amelyek a törlés után hamisak lennének.

A terv végén a futás végigmegy és a státusza `completed`, de eredményt megjelenítő oldal még nincs.

## Global Constraints

- Adatbázis-hozzáférés kizárólag a `backend/app/db.py`-ban; ORM, migrációs eszköz és connection pool nincs. Minden függvény saját kapcsolatot nyit és zár.
- A séma egyetlen fájl: `backend/schema.sql`, csak `create ... if not exists` utasításokkal.
- LLM: `https://opencode.ai/zen/go/v1/chat/completions`, modell `deepseek-v4.1-flash`, fejlécek: `x-opencode-session: swarmsense-<run_id>` és `User-Agent: swarmsense/0.1`.
- A backend beállításai `SWARMSENSE_` előtagú környezeti változók.
- Tesztben valódi LLM-hívás nincs. A tesztek csak `_test` végű nevű adatbázist üríthetnek.
- A backend kódjában és tesztjeiben a terv végén nem szerepelhet a `supabase`, `sentry`, `openrouter` szó.
- Hibáról kifelé csak hibakód megy, a szolgáltató nyers üzenete nem.
- Titok, valódi e-mail-cím és belső gépnév nem kerül a repóba. A `backend/.env` értékeit parancs nem írhatja ki.
- Felhasználói szöveg magyarul, a `frontend/lib/messages.ts`-ben és a `frontend/lib/errors.ts`-ben.
- Commit: Conventional Commits, angolul.
- Nem követett helyi mappákat (`_bmad`, `.cursor`, `.opencode`, `.agent`, `.agents`) a terv nem töröl; csak a gitben követett fájlok törlődnek.

## Review Focus

Amit a spec nem mond ki, de egy felhasználó belefut. Mindegyikhez teszt tartozik a megjelölt feladatban.

1. **Nem UUID alakú futásazonosító az URL-ben** (`/waiting/abc`): 404 `RUN_NOT_FOUND`, nem 500. → 2. és 4. feladat.
2. **Az LLM válaszában nincs `usage` mező:** a futás nem bukik el, a tokenszám 0. → 3. feladat.
3. **Az adatbázis nem érhető el futás indításakor:** `500` `RUN_START_FAILED` kóddal, háttérfeladat nem indul. → 4. feladat.
4. **Túl hosszú (500 karakter feletti) vagy csak szóközből álló mező:** `422`, sor nem jön létre; a frontend érthető üzenetet mutat. → 4. és 5. feladat.
5. **A backend nem érhető el a Server Actionből** (a `fetch` kivételt dob): az action `{ ok: false, code: "RUN_START_FAILED" }`-t ad vissza, nem dob. → 5. feladat.

---

### Task 1: Backend – a kieső flow-k törlése

A cél: eltűnik minden, amit a megmaradó mag nem importál. A `run_processor.py` még használja a `cost_enforcement.py` konstansait, az `email_service.py`-t, a `database.py`-t és a Sentryt; ezek a 4. feladatban mennek.

**Files:**
- Delete: `backend/app/routers/{auth,operator,qualifier,run_sessions,unsubscribe,waitlist}.py`
- Delete: `backend/app/models/{auth,operator,qualifier,run_session,unsubscribe,waitlist}.py`
- Delete: `backend/app/services/{consent_service,data_deletion_service,email_metrics}.py`
- Delete: `backend/delete_user_data.py`, `backend/scripts/` (mindkét szkript)
- Delete: `backend/tests/routers/{test_auth,test_auth_post_deletion,test_operator,test_run_sessions,test_unsubscribe,test_waitlist}.py`
- Delete: `backend/tests/services/{test_consent_service,test_data_deletion_service,test_delete_user_data_cli,test_email_metrics,test_email_service,test_followup_email_service}.py`
- Delete: `backend/tests/test_sentry.py`
- Modify: `backend/app/main.py`, `backend/app/core/internal_auth.py`, `backend/app/core/errors.py`, `backend/tests/routers/test_runs.py`

**Interfaces:**
- Produces: a FastAPI app, amelyben csak a `runs` és a `status` router él; `INTERNAL_ONLY_ENDPOINTS == {("POST", "/api/v1/runs")}`.

- [ ] **Step 1: Töröld a fenti fájlokat** `git rm`-mel.

- [ ] **Step 2: `backend/app/main.py`**

Kikerül: a `sentry_sdk` import és az `_init_sentry`, a `cost_enforcement_middleware` regisztrációja, a hat törölt router importja és `include_router` hívása. Marad: `internal_auth_middleware`, CORS, `runs.router`, `status.router`, a `/` végpont. A middleware-sorrendről szóló megjegyzést igazítsd a két megmaradó middleware-hez.

- [ ] **Step 3: `internal_auth.py` és `errors.py`**

`INTERNAL_ONLY_ENDPOINTS` egyetlen eleme `("POST", "/api/v1/runs")`. Az `ErrorCode`-ban marad: `UNAUTHORIZED`, `RUN_NOT_FOUND`, valamint a `COST_LIMIT_REACHED` és `COST_CHECK_FAILED` (ezeket a 4. feladat törli, addig a `cost_enforcement.py` importálja).

- [ ] **Step 4: `test_runs.py` kigyomlálása**

Töröld azokat a teszteket, amelyek törölt kódot vizsgálnak: `test_run_blocked_at_cap_and_no_row_created`, `test_run_allowed_when_no_month_row`, `test_qualifier_insert_success`, `test_qualifier_payload_validation_failure`, `test_cost_check_failure_returns_503`. A többi tesztből vedd ki a `cost_enforcement` és a `qualifier_router` monkeypatch-eit. A fájl a 4. feladatban teljesen újraíródik, itt csak zöldnek kell maradnia.

- [ ] **Step 5: Ellenőrzés**

Run (a `backend/` mappából): `pytest tests -q`
Expected: minden megmaradt teszt zöld (`test_runs.py`, `test_run_processor.py`, `test_llm_client.py`, `test_persona_engine.py`).

Run: `python -c "from app.main import app; print(sorted(r.path for r in app.routes if r.path.startswith('/api')))"` (betöltött `.env` mellett)
Expected: `['/api/v1/runs', '/api/v1/runs/{run_id}/status', '/api/v1/status']`

- [ ] **Step 6: Commit**

```bash
git add -A backend
git commit -m "refactor(backend): remove auth, qualifier, waitlist and operator flows"
```

---

### Task 2: Postgres – fejlesztői adatbázis, séma, `db.py`

**Files:**
- Create: `docker-compose.dev.yml`, `backend/dev/init-test-db.sql`
- Create: `backend/schema.sql`, `backend/app/db.py`
- Create: `backend/tests/conftest.py`, `backend/tests/test_db.py`
- Modify: `backend/requirements.txt`, `backend/app/core/config.py`

**Interfaces:**
- Produces (`app/db.py`):
  - `SCHEMA_PATH: Path` – a `backend/schema.sql` útvonala (`Path(__file__).resolve().parent.parent / "schema.sql"`).
  - `connect() -> psycopg.Connection` – kapcsolat a `settings.database_url`-re, `row_factory=dict_row`.
  - `apply_schema() -> None` – lefuttatja a `SCHEMA_PATH` tartalmát.
  - `create_run(*, topic: str, audience: str) -> dict[str, Any]` – beszúr egy `queued` sort; visszaad: `id` (`str`), `status` (`str`), `created_at` (`datetime`, időzónával).
  - `get_run(run_id: str) -> dict[str, Any] | None` – a sor minden oszlopa a `pdf` kivételével, az `id` `str`-ként; `None`, ha nincs ilyen sor **vagy a `run_id` nem érvényes UUID**.
  - `update_run(run_id: str, **fields: Any) -> None` – csak az `UPDATABLE_RUN_COLUMNS` oszlopait írja; ismeretlen oszlopnévre `ValueError`.
  - `UPDATABLE_RUN_COLUMNS: frozenset[str]` = `status`, `persona_count`, `support_count`, `reject_count`, `conditional_count`, `synthesis_summary`, `synthesis_main_barriers`, `synthesis_winning_conditions`, `synthesis_best_target_segment`, `synthesis_strategic_recommendation`, `input_tokens`, `output_tokens`, `completed_at`.
- Produces (`tests/conftest.py`): a `clean_db` fixture (üres táblák), az automatikus `settings_env` és `no_real_llm` fixture.
- Produces (`config.py`): `Settings.database_url: str` (kötelező).

- [ ] **Step 1: Fejlesztői Postgres**

`docker-compose.dev.yml` a repo gyökerében, egyetlen `postgres` szolgáltatással: image `postgres:17`, `POSTGRES_USER=swarmsense`, `POSTGRES_PASSWORD=swarmsense`, `POSTGRES_DB=swarmsense`, port `127.0.0.1:5433:5432` (az 5432 a gépen foglalt), named volume `swarmsense-dev-pg`, és a `backend/dev/init-test-db.sql` csatolva a `/docker-entrypoint-initdb.d/` alá. Az init fájl tartalma: `create database swarmsense_test;`. A fájl elejére megjegyzés: a jelszó csak helyi fejlesztésre való.

Run: `docker compose -f docker-compose.dev.yml up -d && sleep 5 && pg_isready -h localhost -p 5433`
Expected: `localhost:5433 - accepting connections`

- [ ] **Step 2: Függőség és beállítás**

`backend/requirements.txt`: új sor `psycopg[binary]==3.2.*`. Telepítés: `pip install -r requirements.txt`.

`config.py`: új kötelező mező `database_url: str = Field(...)`. A többi mező ebben a feladatban változatlan.

A helyi `backend/.env`-be (nem követett fájl) kerüljön be egy sor, az értékek kiírása nélkül:

```bash
grep -q '^SWARMSENSE_DATABASE_URL=' backend/.env || echo 'SWARMSENSE_DATABASE_URL=postgresql://swarmsense:swarmsense@localhost:5433/swarmsense' >> backend/.env
```

- [ ] **Step 3: `backend/schema.sql`**

```sql
create table if not exists runs (
  id uuid primary key default gen_random_uuid(),
  topic text not null check (length(trim(topic)) > 0),
  audience text not null check (length(trim(audience)) > 0),
  status text not null default 'queued'
    check (status in ('queued', 'running', 'composing', 'completed', 'partial', 'failed')),
  persona_count integer not null default 0,
  support_count integer,
  reject_count integer,
  conditional_count integer,
  synthesis_summary text,
  synthesis_main_barriers text[],
  synthesis_winning_conditions text,
  synthesis_best_target_segment text,
  synthesis_strategic_recommendation text,
  result jsonb,
  pdf bytea,
  is_sample boolean not null default false,
  ip_hash text,
  input_tokens integer not null default 0,
  output_tokens integer not null default 0,
  created_at timestamptz not null default now(),
  completed_at timestamptz
);
create index if not exists runs_created_at_idx on runs (created_at);
create index if not exists runs_ip_hash_created_at_idx on runs (ip_hash, created_at);

create table if not exists run_events (
  id bigserial primary key,
  run_id uuid not null references runs (id) on delete cascade,
  type text not null,
  persona_index integer,
  persona_name text,
  attempt integer,
  error_code text,
  duration_ms integer,
  input_tokens integer,
  output_tokens integer,
  created_at timestamptz not null default now()
);
create index if not exists run_events_run_id_id_idx on run_events (run_id, id);

create table if not exists email_requests (
  id bigserial primary key,
  run_id uuid not null references runs (id) on delete cascade,
  email text not null,
  created_at timestamptz not null default now(),
  sent_at timestamptz
);
create index if not exists email_requests_created_at_idx on email_requests (created_at);
```

A `run_events` és az `email_requests` táblát ebben a tervben semmi nem írja; azért jönnek létre most, mert a `create table if not exists` meglévő táblát később nem módosít.

- [ ] **Step 4: `backend/tests/conftest.py`**

- `TEST_DATABASE_URL`: a `SWARMSENSE_TEST_DATABASE_URL` környezeti változó, alapértéke `postgresql://swarmsense:swarmsense@localhost:5433/swarmsense_test`.
- `settings_env` (autouse, function scope): `monkeypatch.setenv`-vel beállítja `SWARMSENSE_DATABASE_URL=TEST_DATABASE_URL`, `SWARMSENSE_INTERNAL_SECRET=test-internal-secret`, `SWARMSENSE_FRONTEND_ORIGIN=http://localhost:3000`, `SWARMSENSE_ENVIRONMENT=development`, valamint egy `# átmeneti, a 4. feladat törli` megjegyzéssel jelölt blokkban a még kötelező régi mezőket (`SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `KIMI_API_KEY`, `OPENROUTER_API_KEY`, `OPERATOR_API_KEY`, `BACKEND_ORIGIN`, `RESEND_API_KEY`) teszt-értékekkel; előtte és utána `get_settings.cache_clear()`.
- `_schema` (session scope): ha a `TEST_DATABASE_URL` adatbázisneve nem `_test`-re végződik, `pytest.exit` hibaüzenettel; különben saját `psycopg.connect(TEST_DATABASE_URL)` kapcsolaton lefuttatja a `db.SCHEMA_PATH` tartalmát.
- `clean_db` (function scope, függ: `settings_env`, `_schema`): `truncate runs, run_events, email_requests restart identity cascade`.
- `no_real_llm` (autouse): az `app.services.llm_client._post_json_sync`-et olyan függvényre cseréli, amely `AssertionError("valódi hálózati hívás tesztben")`-t dob.

- [ ] **Step 5: Írd meg a bukó teszteket (`backend/tests/test_db.py`)**

```python
import uuid
from datetime import UTC, datetime

import pytest

from app import db


def test_create_run_inserts_queued_row(clean_db):
    row = db.create_run(topic="Árazás", audience="KKV vezetők")
    assert uuid.UUID(row["id"])
    assert row["status"] == "queued"
    assert row["created_at"].tzinfo is not None


def test_get_run_returns_row_without_pdf(clean_db):
    created = db.create_run(topic="Árazás", audience="KKV vezetők")
    row = db.get_run(created["id"])
    assert row["id"] == created["id"]
    assert row["topic"] == "Árazás"
    assert row["persona_count"] == 0
    assert row["input_tokens"] == 0
    assert "pdf" not in row


def test_get_run_missing_returns_none(clean_db):
    assert db.get_run(str(uuid.uuid4())) is None


@pytest.mark.parametrize("bad_id", ["abc", "", "123", "'; drop table runs; --"])
def test_get_run_invalid_uuid_returns_none(clean_db, bad_id):
    assert db.get_run(bad_id) is None


def test_update_run_writes_listed_columns(clean_db):
    created = db.create_run(topic="Árazás", audience="KKV vezetők")
    now = datetime.now(UTC)
    db.update_run(
        created["id"],
        status="completed",
        persona_count=18,
        synthesis_main_barriers=["ár", "bizalom"],
        input_tokens=100,
        output_tokens=50,
        completed_at=now,
    )
    row = db.get_run(created["id"])
    assert row["status"] == "completed"
    assert row["persona_count"] == 18
    assert row["synthesis_main_barriers"] == ["ár", "bizalom"]
    assert (row["input_tokens"], row["output_tokens"]) == (100, 50)
    assert row["completed_at"] == now


def test_update_run_rejects_unknown_column(clean_db):
    created = db.create_run(topic="Árazás", audience="KKV vezetők")
    with pytest.raises(ValueError):
        db.update_run(created["id"], topic="más")


def test_update_run_rejects_invalid_status(clean_db):
    created = db.create_run(topic="Árazás", audience="KKV vezetők")
    with pytest.raises(Exception):
        db.update_run(created["id"], status="nonsense")
    assert db.get_run(created["id"])["status"] == "queued"


def test_apply_schema_is_idempotent(clean_db):
    db.apply_schema()
    db.apply_schema()
    assert db.create_run(topic="a", audience="b")["status"] == "queued"
```

- [ ] **Step 6: Futtasd, hogy elbukjon**

Run: `pytest tests/test_db.py -q`
Expected: FAIL, `ImportError: cannot import name 'db' from 'app'`

- [ ] **Step 7: Írd meg az `app/db.py`-t** a fenti Interfaces szerint.

Az oszlopneveket az `update_run` a `psycopg.sql.Identifier`-rel illeszti az SQL-be, az értékeket paraméterként adja át; szöveget SQL-be összefűzni tilos. A `get_run` a `uuid.UUID(run_id)` sikertelenségére ad `None`-t, mielőtt lekérdezne.

- [ ] **Step 8: Futtasd, hogy átmenjen**

Run: `pytest tests -q`
Expected: PASS, a korábbi tesztekkel együtt.

- [ ] **Step 9: Commit**

```bash
git add docker-compose.dev.yml backend/dev backend/schema.sql backend/app/db.py backend/app/core/config.py backend/requirements.txt backend/tests/conftest.py backend/tests/test_db.py
git commit -m "feat(backend): add Postgres schema and psycopg data access module"
```

---

### Task 3: LLM-kliens – opencode Go, tokenszám

**Files:**
- Modify: `backend/app/services/llm_client.py`, `backend/app/services/persona_engine.py`, `backend/app/services/blueprint_generator.py`, `backend/app/services/synthesis_service.py`, `backend/app/services/run_processor.py` (csak a hívások igazítása), `backend/app/models/persona.py`, `backend/app/core/config.py`
- Modify: `backend/tests/conftest.py`
- Test: `backend/tests/services/test_llm_client.py`, `backend/tests/services/test_persona_engine.py`, `backend/tests/services/test_run_processor.py` (csak igazítás)

**Interfaces:**
- Consumes: a 2. feladat `settings_env` fixture-je.
- Produces (`llm_client.py`):
  - `USER_AGENT = "swarmsense/0.1"`
  - `@dataclass(frozen=True) class TokenUsage`: `input_tokens: int = 0`, `output_tokens: int = 0`, és `__add__(other: TokenUsage) -> TokenUsage`.
  - `class LLMClient.__init__(self, *, session_id: str, transport: TransportFn | None = None, sleep=asyncio.sleep, max_attempts: int = 3, base_backoff_seconds: float = 0.5)`
  - `async LLMClient.generate_json(self, *, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> tuple[dict[str, Any], TokenUsage]`
  - `LLMProviderError.error_code` értékei: `RATE_LIMITED` (429), `NETWORK_ERROR` (nincs státusz), `UPSTREAM_ERROR` (5xx), `REQUEST_FAILED` (egyéb), `MISSING_API_KEY`.
- Produces (többi modul):
  - `generate_persona_blueprints(*, topic, audience, count, llm_client: LLMClient) -> tuple[list[PersonaBlueprint], TokenUsage]`
  - `execute_synthesis(*, personas, topic, audience, llm_client: LLMClient) -> tuple[SynthesisResult, TokenUsage]`
  - `execute_persona_engine(*, topic, audience, llm_client: LLMClient, concurrency_limit=5, total_personas=DEFAULT_PERSONA_COUNT, blueprints=None, on_persona_completed=None) -> PersonaRunResult` – az `llm_client` kötelező.
  - `PersonaRunResult`: a `cost_usd` helyett `input_tokens: int = 0` és `output_tokens: int = 0`; ha az engine maga generálta a personákat, annak tokenjei is benne vannak.
- Produces (`config.py`): `llm_api_key: str` (kötelező), `llm_model: str = "deepseek-v4.1-flash"`, `llm_base_url: AnyHttpUrl = "https://opencode.ai/zen/go/v1"`. Az `openrouter_*` és a `kimi_api_key` mező törlődik.

- [ ] **Step 1: Írd át a bukó teszteket (`test_llm_client.py`)**

A `_seed_openrouter_env` segédfüggvény törlődik (a `settings_env` fixture pótolja; a conftest átmeneti blokkjában az `OPENROUTER_API_KEY` és a `KIMI_API_KEY` helyére `SWARMSENSE_LLM_API_KEY=test-llm-key` kerül). A négy meglévő teszt neve és logikája marad, az új nevekre és hibakódokra igazítva. A kérés alakját vizsgáló teszt új állításai, plusz két új teszt:

```python
def test_request_shape():
    seen = {}

    async def fake_transport(url, headers, payload):
        seen.update(url=url, headers=headers, payload=payload)
        return {
            "choices": [{"message": {"content": '{"ok": true}', "reasoning_content": "..."}}],
            "usage": {"prompt_tokens": 79, "completion_tokens": 74, "total_tokens": 153},
        }

    client = LLMClient(session_id="swarmsense-run-1", transport=fake_transport)
    data, usage = asyncio.run(client.generate_json(system_prompt="s", user_prompt="u"))

    assert seen["url"] == "https://opencode.ai/zen/go/v1/chat/completions"
    assert seen["headers"]["x-opencode-session"] == "swarmsense-run-1"
    assert seen["headers"]["User-Agent"] == "swarmsense/0.1"
    assert seen["headers"]["Authorization"] == "Bearer test-llm-key"
    assert seen["payload"]["model"] == "deepseek-v4.1-flash"
    assert seen["payload"]["response_format"] == {"type": "json_object"}
    assert data == {"ok": True}
    assert usage == TokenUsage(input_tokens=79, output_tokens=74)


@pytest.mark.parametrize("usage", [None, {}, {"prompt_tokens": None}, {"prompt_tokens": "x"}, "nem objektum"])
def test_missing_or_malformed_usage_gives_zero_tokens(usage):
    async def fake_transport(url, headers, payload):
        body = {"choices": [{"message": {"content": '{"ok": true}'}}]}
        if usage is not None:
            body["usage"] = usage
        return body

    client = LLMClient(session_id="s", transport=fake_transport)
    _, tokens = asyncio.run(client.generate_json(system_prompt="s", user_prompt="u"))
    assert tokens == TokenUsage(0, 0)


def test_token_usage_adds():
    assert TokenUsage(1, 2) + TokenUsage(10, 20) == TokenUsage(11, 22)
```

A retry-teszt állítása: három 429 után `LLMProviderError`, `error_code == "RATE_LIMITED"`, pontosan 3 kísérlet. A terminális hibáé: 400 után egyetlen kísérlet, `error_code == "REQUEST_FAILED"`.

- [ ] **Step 2: Írd át a `test_persona_engine.py` két engine-tesztjét**

A hamis kliens `generate_json`-t valósít meg, és `(válasz, TokenUsage(10, 5))`-öt ad vissza. Új állítások a párhuzamossági tesztben: `result.input_tokens == 180` és `result.output_tokens == 90` (18 persona, előre megadott `blueprints`). A hibagyűjtő tesztben a kiesett persona `error_code`-ja az új kódok egyike.

- [ ] **Step 3: Futtasd, hogy elbukjon**

Run: `pytest tests/services/test_llm_client.py tests/services/test_persona_engine.py -q`
Expected: FAIL, `ImportError: cannot import name 'LLMClient'`

- [ ] **Step 4: Írd át az `llm_client.py`-t és a `config.py`-t**

- Az osztály neve `LLMClient`; a `generate_persona_response` burkoló törlődik (nincs hívója), a `generate_persona_response_with_meta` neve `generate_json`.
- A fejlécek: `Authorization`, `Content-Type`, `x-opencode-session: <session_id>`, `User-Agent: USER_AGENT`.
- Az `_extract_cost_usd` helyére `_extract_usage(payload) -> TokenUsage` kerül: a `usage.prompt_tokens` és a `usage.completion_tokens` értékét olvassa; ami hiányzik, nem egész szám vagy negatív, az 0.
- A hibaüzenetekből és a hibakódokból kikerül az „OpenRouter” szó.

- [ ] **Step 5: Igazítsd a három service-t és a `PersonaRunResult`-ot** az Interfaces szerint. A `run_processor.py`-ban ebben a feladatban csak annyi változik, hogy lefordul és a tesztjei zöldek: létrehoz egy `LLMClient(session_id=f"swarmsense-{run_id}")`-t, átadja az engine-nek és a szintézisnek, a `cost_usd`-t pedig 0-nak veszi. A teljes átírás a 4. feladat.

- [ ] **Step 6: A helyi `.env` változóneveinek átírása** (értékek kiírása nélkül):

```bash
sed -i 's/^SWARMSENSE_OPENROUTER_/SWARMSENSE_LLM_/; /^SWARMSENSE_KIMI_API_KEY=/d' backend/.env
grep -c '^SWARMSENSE_LLM_' backend/.env
```

Expected: `3`

- [ ] **Step 7: Futtasd, hogy átmenjen**

Run: `pytest tests -q`
Expected: PASS

Run: `grep -rni "openrouter\|kimi" backend/app`
Expected: nincs találat.

- [ ] **Step 8: Commit**

```bash
git add -A backend
git commit -m "feat(backend): switch LLM client to opencode Go and report token usage"
```

---

### Task 4: Futásfeldolgozó és végpontok Postgresen

**Files:**
- Modify: `backend/app/services/run_processor.py`, `backend/app/routers/runs.py`, `backend/app/models/run.py`, `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/core/errors.py`, `backend/requirements.txt`, `backend/Dockerfile`, `backend/.env.example`, `backend/tests/conftest.py`
- Delete: `backend/app/core/database.py`, `backend/app/core/cost_enforcement.py`, `backend/app/services/email_service.py`
- Rewrite: `backend/tests/services/test_run_processor.py`, `backend/tests/routers/test_runs.py`

**Interfaces:**
- Consumes: `db.create_run`, `db.get_run`, `db.update_run`, `db.apply_schema` (2. feladat); `LLMClient`, `TokenUsage`, `execute_persona_engine`, `execute_synthesis` (3. feladat).
- Produces:
  - `async process_run(*, run_id: str, topic: str, audience: str, llm_client: LLMClient | None = None) -> PersonaRunResult`
  - `dispatch_run_processing(*, run_id: str, topic: str, audience: str, llm_client: LLMClient | None = None) -> None` – soha nem dob.
  - `_resolve_final_status(*, result: PersonaRunResult, synthesis: SynthesisResult | None) -> str`
  - `POST /api/v1/runs` – kérés: `{"topic": str, "audience": str}`; válasz: `{"run_id", "status", "created_at"}`.
  - `GET /api/v1/runs/{run_id}/status` – válasz változatlan: `{"run_id", "status", "persona_count", "total_personas", "updated_at"}`.
  - `ErrorCode`: `UNAUTHORIZED`, `RUN_NOT_FOUND`, `RUN_START_FAILED`.
  - `Settings` végleges mezői: `database_url`, `llm_api_key`, `llm_model`, `llm_base_url`, `internal_secret`, `frontend_origin`, `environment`.

**A feldolgozó viselkedése** (a meglévő logika, a költség-, e-mail- és Sentry-részek nélkül):

| Helyzet | `status` | Egyéb |
|---|---|---|
| Indulás | `running` | `persona_count = 0` |
| Persona elkészül | `running` | `persona_count` nő |
| 12-nél kevesebb sikeres persona | `failed` | szintézis nem fut |
| Personák megvannak | `composing` | |
| Minden persona és a szintézis sikeres | `completed` | |
| Kiesett legalább egy persona, **vagy a szintézis elbukott** | `partial` | szintézis-oszlopok `NULL`, ha a szintézis bukott |
| Bármilyen nem várt kivétel | `failed` | a `dispatch_run_processing` elnyeli és naplózza |

Minden végállapotnál kitöltődik a `completed_at`, az `input_tokens` és az `output_tokens` (personák + persona-generálás + szintézis összege). A Sentry-hívások helyére `logging.getLogger("swarmsense.run")` kerül: kivételnél `logger.exception`, a futás végén egy összefoglaló sor `logger.info`-val (futásazonosító, státusz, eltelt idő másodpercben, tokenek, kiesettek száma). A téma és a célközönség szövege nem kerül a naplóba.

- [ ] **Step 1: Írd újra a `test_run_processor.py`-t (bukó tesztek)**

A `FakeQuery`, `FakeResponse` és minden Supabase-, költség-, e-mail- és Sentry-teszt törlődik. A tesztek valódi adatbázist (`clean_db`) és hamis transportot használnak. Segédfüggvény a fájlban:

```python
def make_fake_llm(*, failing_personas: frozenset[str] = frozenset(), synthesis_fails: bool = False, blueprint_fails: bool = False) -> LLMClient:
    """Hamis LLM: a system prompt alapján dönti el, melyik hívás jött.

    - blueprint-hívás: 18 personát ad vissza "Persona 1" ... "Persona 18" névvel
    - persona-hívás: érvényes választ ad a user promptban szereplő névvel;
      ha a név benne van a failing_personas-ban, TransportError(status_code=400)
    - szintézis-hívás: érvényes SynthesisResult-ot ad
    Minden sikeres válasz usage-e: prompt_tokens=10, completion_tokens=5.
    """
```

A stance-ek kiosztása a persona sorszáma szerint: 1–10 `support`, 11–15 `reject`, 16–18 `conditional`.

```python
def _run(clean_db, **fake_kwargs):
    row = db.create_run(topic="Árazás", audience="KKV vezetők")
    dispatch_run_processing(
        run_id=row["id"], topic="Árazás", audience="KKV vezetők",
        llm_client=make_fake_llm(**fake_kwargs),
    )
    return db.get_run(row["id"])


def test_completed_run_stores_counts_synthesis_and_tokens(clean_db):
    run = _run(clean_db)
    assert run["status"] == "completed"
    assert run["persona_count"] == 18
    assert (run["support_count"], run["reject_count"], run["conditional_count"]) == (10, 5, 3)
    assert run["synthesis_summary"]
    assert isinstance(run["synthesis_main_barriers"], list)
    assert (run["input_tokens"], run["output_tokens"]) == (200, 100)  # 20 hívás
    assert run["completed_at"] is not None


def test_partial_when_some_personas_fail(clean_db):
    run = _run(clean_db, failing_personas=frozenset({"Persona 1", "Persona 2", "Persona 3"}))
    assert run["status"] == "partial"
    assert run["persona_count"] == 15
    assert run["support_count"] == 7
    assert (run["input_tokens"], run["output_tokens"]) == (170, 85)  # 17 sikeres hívás


def test_failed_below_threshold_skips_synthesis(clean_db):
    failing = frozenset(f"Persona {i}" for i in range(1, 8))  # 11 marad
    run = _run(clean_db, failing_personas=failing)
    assert run["status"] == "failed"
    assert run["persona_count"] == 11
    assert run["synthesis_summary"] is None
    assert run["completed_at"] is not None


def test_exactly_threshold_is_not_failed(clean_db):
    failing = frozenset(f"Persona {i}" for i in range(1, 7))  # 12 marad
    assert _run(clean_db, failing_personas=failing)["status"] == "partial"


def test_partial_when_synthesis_fails(clean_db):
    run = _run(clean_db, synthesis_fails=True)
    assert run["status"] == "partial"
    assert run["persona_count"] == 18
    assert run["synthesis_summary"] is None
    assert run["support_count"] == 10


def test_failed_when_persona_generation_fails(clean_db):
    run = _run(clean_db, blueprint_fails=True)  # a dispatch nem dobhat
    assert run["status"] == "failed"
    assert run["completed_at"] is not None


def test_summary_log_has_no_topic_text(clean_db, caplog):
    with caplog.at_level("INFO", logger="swarmsense.run"):
        _run(clean_db)
    assert any("completed" in r.getMessage() for r in caplog.records)
    assert "Árazás" not in caplog.text
```

A négy `test_result_payload_*` konszenzus-teszt megmarad: a `_build_result_payload`-ot közvetlenül, kézzel összerakott `PersonaRunResult`-tal hívják, monkeypatch nélkül, változatlan állításokkal. A három `test_extract_provider_error_metadata_*` teszt és maga a függvény törlődik, ha az átírás után nincs hívója.

- [ ] **Step 2: Írd újra a `test_runs.py`-t (bukó tesztek)**

Valódi adatbázis (`clean_db`); a háttérfeladatot minden teszt lecseréli: `monkeypatch.setattr(runs_router, "dispatch_run_processing", recorder)`, ahol a `recorder` a kapott kulcsszavas argumentumokat egy listába teszi. Kliens: `TestClient(create_app())`, `with` blokkban (így lefut a `lifespan`).

```python
HEADERS = {"X-Internal-Secret": "test-internal-secret"}

def test_create_run_inserts_row_and_dispatches(client, dispatched):
    r = client.post("/api/v1/runs", json={"topic": "  Árazás ", "audience": "KKV vezetők"}, headers=HEADERS)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "queued"
    assert db.get_run(body["run_id"])["topic"] == "Árazás"
    assert dispatched == [{"run_id": body["run_id"], "topic": "Árazás", "audience": "KKV vezetők"}]

@pytest.mark.parametrize("headers", [{}, {"X-Internal-Secret": "rossz"}])
def test_create_run_without_valid_secret_is_401(client, dispatched, headers): ...
    # 401, code == "UNAUTHORIZED", a runs tábla üres, dispatched == []

def test_trailing_slash_still_requires_secret(client, dispatched): ...
    # POST /api/v1/runs/ titok nélkül: 401

@pytest.mark.parametrize("payload", [
    {"topic": "", "audience": "a"},
    {"topic": "   ", "audience": "a"},
    {"topic": "a", "audience": ""},
    {"topic": "x" * 501, "audience": "a"},
    {"topic": "a", "audience": "x" * 501},
    {"topic": "a"},
    {"topic": "a", "audience": "b", "user_id": "u1"},
])
def test_create_run_invalid_payload_is_422(client, dispatched, payload): ...
    # 422, a runs tábla üres, dispatched == []

def test_create_run_accepts_exactly_500_chars(client, dispatched): ...
    # topic és audience 500-500 karakter: 200

def test_create_run_db_failure_returns_code_and_does_not_dispatch(client, dispatched, monkeypatch):
    def boom(**_): raise RuntimeError("connection refused: postgres://user:titok@host")
    monkeypatch.setattr(db, "create_run", boom)
    r = client.post("/api/v1/runs", json={"topic": "a", "audience": "b"}, headers=HEADERS)
    assert r.status_code == 500
    assert r.json()["code"] == "RUN_START_FAILED"
    assert "titok" not in r.text
    assert dispatched == []

def test_get_status_returns_progress(client):
    row = db.create_run(topic="a", audience="b")
    db.update_run(row["id"], status="running", persona_count=7)
    body = client.get(f"/api/v1/runs/{row['id']}/status").json()
    assert body == {"run_id": row["id"], "status": "running", "persona_count": 7,
                    "total_personas": 18, "updated_at": body["updated_at"]}
    assert body["updated_at"] is not None

@pytest.mark.parametrize("run_id", [str(uuid.uuid4()), "abc", "x" * 200])
def test_get_status_unknown_or_malformed_id_is_404(client, run_id): ...
    # 404, code == "RUN_NOT_FOUND"

def test_startup_applies_schema_on_empty_database(...): ...
    # a három tábla eldobása után `with TestClient(create_app())`, majd db.create_run sikeres
```

Megmarad változatlan állításokkal: `test_docs_disabled_in_production`, `test_cors_allows_frontend_origin`, `test_cors_blocks_unknown_origin`.

- [ ] **Step 3: Futtasd, hogy elbukjon**

Run: `pytest tests/services/test_run_processor.py tests/routers/test_runs.py -q`
Expected: FAIL (a `dispatch_run_processing` nem fogad `llm_client`-et; a végpont `user_id`-t vár).

- [ ] **Step 4: `models/run.py`**

A `RunCreateRequest`-ből kikerül a `user_id` és a hozzá tartozó két validátor. A `topic` és az `audience` szóközvágás után 1–500 karakter (`MAX_FIELD_LENGTH = 500` konstans a modulban); az `extra="forbid"` marad.

- [ ] **Step 5: `run_processor.py` átírása** a fenti viselkedéstábla és Interfaces szerint.

Törlődik: minden `sentry_sdk`, `cost`, `Decimal`, `email`, `get_supabase_client` hivatkozás és a hozzájuk tartozó segédfüggvények (`_should_increment_monthly_cost`, `_load_run_row`, `_normalize_cost`, `_increment_monthly_cost`, `_capture_cost_threshold_warning`, `_dispatch_result_email`, `_load_user_email`, `_capture_failed_run`). Az `_update_run_row` helyett közvetlen `db.update_run(run_id, ...)` hívások mennek. Ha a hívó nem ad `llm_client`-et, a `process_run` hozza létre: `LLMClient(session_id=f"swarmsense-{run_id}")`. A `_build_result_payload` és segédfüggvényei változatlanul maradnak (a B terv 4. lépése használja őket), a `personas_for_email` változó neve `personas` lesz.

- [ ] **Step 6: `routers/runs.py` átírása**

- `POST`: `db.create_run(topic=..., audience=...)`; kivételnél `error_response(500, "Failed to create run", ErrorCode.RUN_START_FAILED)` és `logger.exception`; sikernél `background_tasks.add_task(dispatch_run_processing, run_id=..., topic=..., audience=...)`.
- `GET status`: `db.get_run(run_id)`; `None`-ra 404 `RUN_NOT_FOUND`. Az `updated_at` a `completed_at`, ennek híján a `created_at`.
- A Supabase-válasz alakját ellenőrző kód (`cast`, `isinstance` láncok) törlődik: a `db.py` típusos sorokat ad.

- [ ] **Step 7: `main.py`, `config.py`, `errors.py`, takarítás**

- `main.py`: `lifespan` függvény, amely induláskor meghívja a `db.apply_schema()`-t; `FastAPI(lifespan=lifespan, ...)`. A CORS marad, fölé megjegyzés: „átmeneti, a B terv 3. lépése szünteti meg”.
- `config.py`: csak a hét végleges mező marad.
- `errors.py`: a két `COST_*` kód törlődik, új a `RUN_START_FAILED`.
- Töröld a `core/database.py`, `core/cost_enforcement.py`, `services/email_service.py` fájlt.
- `requirements.txt`: kikerül a `sentry-sdk`, a `supabase` és a `resend` (a `resend` a B terv 5. lépésében jön vissza). Utána: `pip uninstall -y sentry-sdk supabase resend`.
- `conftest.py`: az átmeneti blokk törlődik.
- `Dockerfile`: új sor a `COPY ... app ./app` után: `COPY --chown=app:app schema.sql ./schema.sql`.

- [ ] **Step 8: `backend/.env.example`** (teljes tartalom)

```
SWARMSENSE_DATABASE_URL=postgresql://swarmsense:swarmsense@localhost:5433/swarmsense
SWARMSENSE_LLM_API_KEY=your-opencode-go-key
SWARMSENSE_LLM_MODEL=deepseek-v4.1-flash
SWARMSENSE_LLM_BASE_URL=https://opencode.ai/zen/go/v1
SWARMSENSE_INTERNAL_SECRET=change-me
SWARMSENSE_FRONTEND_ORIGIN=http://localhost:3000
SWARMSENSE_ENVIRONMENT=development
```

A helyi `backend/.env`-ből a már nem olvasott sorok törlése (értékek kiírása nélkül):

```bash
sed -i -E '/^SWARMSENSE_(SUPABASE_URL|SUPABASE_SERVICE_KEY|OPERATOR_API_KEY|BACKEND_ORIGIN|RESEND_API_KEY|EMAIL_FROM|EMAIL_REPLY_TO|DISABLE_SINGLE_RUN_LIMIT)=/d' backend/.env
cut -d= -f1 backend/.env | sort
```

Expected: pontosan a fenti hét név.

- [ ] **Step 9: Futtasd, hogy átmenjen**

Run: `pytest tests -q`
Expected: PASS

Run: `grep -rni "supabase\|sentry\|openrouter" backend/app backend/tests backend/requirements.txt backend/.env.example`
Expected: nincs találat.

- [ ] **Step 10: Commit**

```bash
git add -A backend
git commit -m "feat(backend): run processing on Postgres without Supabase, Sentry or cost tracking"
```

---

### Task 5: Frontend – törlés és közvetlen futásindítás

**Files:**
- Delete: `frontend/app/{blocked,pro,qualifier,verify}/`, `frontend/app/research/{email,sent}/`, `frontend/app/api/emails/`, `frontend/emails/`
- Delete: `frontend/app/actions/{join-waitlist,submit-run,verify-token}.ts` és tesztjeik
- Delete: `frontend/components/{blocking-screen,persona-card}.tsx` és tesztjeik, `frontend/components/ui/{input,radio-group,select}.tsx`
- Delete: `frontend/sentry.client.config.ts`, `frontend/sentry.server.config.ts`
- Modify: `frontend/app/actions/start-run.ts`, `frontend/app/research/page.tsx`, `frontend/app/waiting/[run_id]/page.tsx`, `frontend/components/waiting-screen.tsx`, `frontend/app/layout.tsx`, `frontend/next.config.ts`, `frontend/lib/errors.ts`, `frontend/lib/messages.ts`, `frontend/package.json`, `frontend/.gitignore`, `frontend/.env.example`
- Test: `frontend/app/actions/start-run.test.ts`, `frontend/app/research/page.test.tsx`, `frontend/components/waiting-screen.test.tsx`

**Interfaces:**
- Consumes: backend `POST /api/v1/runs` (`{topic, audience}` → `{run_id, status, created_at}`; hibánál `{detail, code}`; `422`-nél a FastAPI saját hibaformátuma, `code` nélkül).
- Produces:
  - `startRunAction(input: { topic: string; audience: string }): Promise<{ ok: true; run_id: string } | { ok: false; code: string }>` – soha nem dob.
  - Hibakódok a `lib/errors.ts`-ben: `RUN_START_FAILED`, `INVALID_INPUT`.
  - `WaitingScreen` propjai: `{ runId: string; apiBaseUrl: string }`.

- [ ] **Step 1: Töröld a fenti fájlokat és a függőségeket**

```bash
cd frontend && pnpm remove @sentry/nextjs @react-email/components @react-email/render
```

A `next.config.ts` a `withSentryConfig` burkoló nélkül, sima `export default nextConfig`. A `layout.tsx`-ből kikerül a `plausibleDomain`, a `<Script>` blokk és a `Script` import.

- [ ] **Step 2: Írd át a bukó teszteket**

`start-run.test.ts` (a `fetch` mockolva, `API_URL=http://backend:8000`, `INTERNAL_SECRET=s3cret` beállítva):

```ts
it("posts trimmed topic and audience with the internal secret", async () => {
  fetchMock.mockResolvedValue(new Response(JSON.stringify({ run_id: "r-1", status: "queued", created_at: "2026-10-07T12:00:00Z" }), { status: 200 }));
  const result = await startRunAction({ topic: "  Árazás ", audience: " KKV vezetők " });
  expect(result).toEqual({ ok: true, run_id: "r-1" });
  const [url, init] = fetchMock.mock.calls[0];
  expect(url).toBe("http://backend:8000/api/v1/runs");
  expect(init.headers["X-Internal-Secret"]).toBe("s3cret");
  expect(JSON.parse(init.body)).toEqual({ topic: "Árazás", audience: "KKV vezetők" });
});

it("returns the backend error code on failure", async () => {
  // 500 + {"detail": "...", "code": "RUN_START_FAILED"}  ->  { ok: false, code: "RUN_START_FAILED" }
});

it("maps 422 to INVALID_INPUT", async () => {
  // 422 + {"detail": [...]}  ->  { ok: false, code: "INVALID_INPUT" }
});

it("returns RUN_START_FAILED when the backend is unreachable", async () => {
  fetchMock.mockRejectedValue(new TypeError("fetch failed"));
  await expect(startRunAction({ topic: "a", audience: "b" })).resolves.toEqual({ ok: false, code: "RUN_START_FAILED" });
});

it("returns RUN_START_FAILED on a non-JSON or run_id-less response", async () => {
  // 200 + "<html>"  és  200 + {}  ->  { ok: false, code: "RUN_START_FAILED" }
});

it("returns INVALID_INPUT without calling the backend for empty or over-500-char input", async () => {
  // { topic: "   ", audience: "b" } és { topic: "x".repeat(501), audience: "b" }: fetch nem hívódik
});

it("returns RUN_START_FAILED when API_URL or INTERNAL_SECRET is missing", async () => {
  // fetch nem hívódik
});
```

`research/page.test.tsx`: a `startRunAction` mockolva (`vi.mock("@/app/actions/start-run")`). A négy „letiltott / hibaüzenet / nem navigál” teszt marad. A két navigációs teszt helyére:

```ts
it("starts a run and navigates to the waiting screen", async () => {
  startRunMock.mockResolvedValue({ ok: true, run_id: "r-1" });
  // két mező kitöltése, submit
  await waitFor(() => expect(mockPush).toHaveBeenCalledWith("/waiting/r-1"));
  expect(startRunMock).toHaveBeenCalledWith({ topic: "Árazási teszt", audience: "KKV vezetők" });
});

it("shows the mapped error message and re-enables submit when start fails", async () => {
  startRunMock.mockResolvedValue({ ok: false, code: "RUN_START_FAILED" });
  // submit után: megjelenik az errorMessages.RUN_START_FAILED szöveg (role="alert"),
  // a gomb újra aktív, mockPush nem hívódott
});

it("disables submit while the run is starting", async () => {
  // függőben hagyott promise mellett a gomb disabled; második kattintásra a mock egyszer hívódott
});
```

`waiting-screen.test.tsx`: minden renderből kikerül az `email` prop; új állítás a „completed” tesztben: a képernyőn nem szerepel az „e-mail” szó.

- [ ] **Step 3: Futtasd, hogy elbukjon**

Run: `pnpm exec vitest run app/actions/start-run.test.ts app/research/page.test.tsx components/waiting-screen.test.tsx`
Expected: FAIL

- [ ] **Step 4: `start-run.ts`** az Interfaces szerint.

A cookie-kezelés és a `parseRunContext` törlődik. A teljes törzs `try`/`catch`-ben fut; a `catch` ága `{ ok: false, code: "RUN_START_FAILED" }`. Az URL: `process.env.API_URL` (a `NEXT_PUBLIC_API_URL` tartalék itt megszűnik).

- [ ] **Step 5: `research/page.tsx`**

A `handleSubmit` a `router.push('/research/email?...')` helyett a `startRunAction`-t hívja `useTransition`-nel; sikernél `router.push(\`/waiting/${run_id}\`)`, hibánál a `getErrorMessageByCode(code)` szövege jelenik meg a gomb fölött `role="alert"` elemben. A gomb `disabled`, amíg az indítás folyamatban van.

- [ ] **Step 6: Várakozó oldal és képernyő**

A `waiting/[run_id]/page.tsx`-ből kikerül a cookie-olvasás és az `email`. A `waiting-screen.tsx`-ből kikerül az `email` prop, a `canCloseNotice` bekezdés, az e-mail-értesítő blokk és a `Mail` ikon importja. A pollingon ez a feladat nem változtat.

- [ ] **Step 7: Szövegek**

`lib/errors.ts` teljes tartalma két kód:

```ts
export const errorMessages = {
  RUN_START_FAILED: "Nem sikerült elindítani az elemzést. Kérjük, próbáld újra.",
  INVALID_INPUT: "Mindkét mezőt töltsd ki, mezőnként legfeljebb 500 karakterrel.",
} as const;
```

`lib/messages.ts`:

- Törlődik: a `qualifier`, `blockingScreen`, `verify` és `email` szakasz, a `research.form.email` blokk és a `research.form.errors.email`, valamint a `waiting.canCloseNotice` és a `waiting.emailDeliveryNotice`.
- Módosul (a hero `highlight: "pár perc"` szándékos, marad):

| Kulcs | Új szöveg |
|---|---|
| `research.form.subheadline` | `Írd le a kutatási kérdést és a célcsoportot. Az elemzés nagyjából másfél perc alatt lefut.` |
| `research.form.submitCta` | `Elemzés indítása` |
| `research.form.helper` | `Regisztráció és e-mail-cím nélkül.` |
| `waiting.subheadline` | `A szintetikus personák a háttérben futnak. Ez nagyjából másfél percig tart.` |
| `waiting.partialStatusHint` | `Részleges lefutás: nem minden persona válaszolt` |
| `landing` „hogyan működik” 3. lépés `title` / `description` | `Megkapod az eredményt` / `Az összefoglaló és a personák válaszai az oldalon jelennek meg.` |
| `landing.stats.items[2]` | `{ value: "Strukturált elemzés", label: "az oldalon, azonnal" }` |
| `landing.closingCta.helper` | `Regisztráció nélkül.` |

A sikertelen futás utáni link a várakozó képernyőn a `research.form.submitCta`-t használja; az új szöveggel is értelmes, nem kell külön kulcs.

- [ ] **Step 8: Env példa**

`frontend/.gitignore`: a `.env*` sor alá `!.env.example`. A `frontend/.env.example` teljes tartalma (a meglévő fájlt felülírva, hogy biztosan ne maradjon benne valódi érték):

```
API_URL=http://localhost:8000
# Átmeneti: a várakozó képernyő még közvetlenül kérdezi a backendet (a B terv megszünteti).
NEXT_PUBLIC_API_URL=http://localhost:8000
INTERNAL_SECRET=change-me
```

A helyi `frontend/.env.local`-ból: `sed -i '/^NEXT_PUBLIC_PLAUSIBLE_DOMAIN=/d; /^NEXT_PUBLIC_SENTRY_DSN=/d' frontend/.env.local`

- [ ] **Step 9: Teljes ellenőrzés** (a `frontend/` mappából)

Run: `pnpm lint && pnpm exec tsc --noEmit && pnpm test && pnpm build`
Expected: mind zöld; a build kimenetében az útvonalak: `/`, `/research`, `/waiting/[run_id]`, `/privacy`, `/terms`.

Run: `grep -rniE "sentry|plausible|react-email|magic|qualifier|waitlist" app components lib next.config.ts package.json`
Expected: nincs találat.

- [ ] **Step 10: Commit**

```bash
git add -A frontend
git commit -m "feat(frontend): start runs directly from the form and drop the email funnel"
```

---

### Task 6: Repo-takarítás és CI

**Files:**
- Delete (csak követett fájlok): `_bmad-output/`, `supabase/`, `docker-compose.swarmsense-backend.yml`, `.github/workflows/deploy.yml`, `.github/workflows/supabase-migrations-draft.yml`, a `docs/` minden fájlja a `docs/superpowers/` kivételével
- Modify: `.github/workflows/ci.yml`, `CLAUDE.md`

**Interfaces:**
- Consumes: `docker-compose.dev.yml` (2. feladat), a `SWARMSENSE_TEST_DATABASE_URL` változó (2. feladat conftest).

A `deploy.yml` törlése azt is megakadályozza, hogy a `master`-re kerülő új backend a régi Hetzner szerverre települjön. A régi éles oldal ettől nem áll le; a lekapcsolása a C terv 7. lépése.

- [ ] **Step 1: Törlés**

```bash
git rm -r -q _bmad-output supabase docker-compose.swarmsense-backend.yml .github/workflows/deploy.yml .github/workflows/supabase-migrations-draft.yml
git ls-files docs | grep -v '^docs/superpowers/' | xargs git rm -q
```

- [ ] **Step 2: `ci.yml`**

- `workflow_sanity`: a „Prepare backend env for compose validation” és a „Validate production compose syntax” lépés helyére egy lépés: `docker compose -f docker-compose.dev.yml config`.
- `backend` job: `services.postgres` (image `postgres:17`, env `POSTGRES_USER=swarmsense`, `POSTGRES_PASSWORD=swarmsense`, `POSTGRES_DB=swarmsense_test`, port `5432:5432`, health check `pg_isready -U swarmsense`), a „Test” lépés env-je: `SWARMSENSE_TEST_DATABASE_URL: postgresql://swarmsense:swarmsense@localhost:5432/swarmsense_test`.
- A `frontend` job változatlan.

Run: `docker compose -f docker-compose.dev.yml config >/dev/null && echo ok`
Expected: `ok`. (Az `actionlint` a CI-ban fut; ha helyben telepítve van, futtasd.)

- [ ] **Step 3: `CLAUDE.md`**

A „Parancsok” szakaszban a backend rész elé kerül a `docker compose -f docker-compose.dev.yml up -d` (Postgres a `localhost:5433`-on), és a szakasz elejéről törlődik a „psycopg-re való átállás után … frissíteni kell” mondat. A „Hol tart a projekt” első bekezdése frissül: a backend és a frontend magja már az új alapon áll; a trace, az eredményoldal, a PDF, az e-mail és a keretek még hiányoznak.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: remove legacy docs, Supabase and old deploy; run CI against Postgres"
```

---

### Task 7: Végellenőrzés valódi futással

**Files:**
- Modify: `TRACKING.md`, `CLAUDE.md` (az A terv jelölőnégyzetei)

Ez a feladat egy valódi futást indít, ami az opencode Go keretből kb. 20 hívást fogyaszt.

- [ ] **Step 1: Teljes tesztkör**

Run (`backend/`): `pytest tests -q` → PASS
Run (`frontend/`): `pnpm lint && pnpm exec tsc --noEmit && pnpm test && pnpm build` → zöld

- [ ] **Step 2: Valódi futás helyben**

Három terminál: `docker compose -f docker-compose.dev.yml up -d`; a `backend/` mappában `set -a && . ./.env && set +a && python -m uvicorn app.main:app --port 8000`; a `frontend/` mappában `pnpm dev`. A `backend/.env` `SWARMSENSE_INTERNAL_SECRET` és a `frontend/.env.local` `INTERNAL_SECRET` értékének egyeznie kell, és a `frontend/.env.local`-ban `API_URL=http://localhost:8000` és `NEXT_PUBLIC_API_URL=http://localhost:8000` legyen.

A böngészőben: `http://localhost:3000/research` → két mező kitöltése → „Elemzés indítása”.

Expected: átirányítás a `/waiting/<id>` oldalra; a számláló 18-ig megy; kb. másfél perc után „Az eredmény elkészült”.

- [ ] **Step 3: Az adatbázis ellenőrzése**

Run: `psql postgresql://swarmsense:swarmsense@localhost:5433/swarmsense -c "select status, persona_count, support_count + reject_count + conditional_count as stances, input_tokens > 0 as has_tokens, synthesis_summary is not null as has_synthesis, completed_at is not null as done from runs order by created_at desc limit 1"`
Expected: `completed` vagy `partial`; `persona_count` legalább 12 és egyenlő a `stances` értékével; `has_tokens`, `done` igaz.

A backend naplójában egy összefoglaló sor van a futásról, a kérdés szövege nélkül.

- [ ] **Step 4: Az A terv kritériumainak kipipálása**

A `CLAUDE.md` „A terv: Új alap” öt pontja kipipálva. A `TRACKING.md`-ben az 1. és 2. lépés „kész”, az A terv sora a tervfájlra mutat „kész” állapottal, a „Most” sor: a B terv megírása következik. Ha építés közben valami eltért a spectől, sor kerül az „Eltérések” táblába, és a spec is frissül.

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md TRACKING.md
git commit -m "docs: mark plan A complete"
```
