# Story 5-6: Enrich Follow-up Emails with Run Synthesis and Research Results

## Status: ready-for-dev

---

## Story

**As a** SwarmSense user who completed a free research run,
**I want** to receive follow-up emails that include my original research topic, audience, stance breakdown, and synthesis summary,
**So that** I can recall the value of my research and be motivated to join the Pro waitlist.

---

## Business Context

Follow-up emails (day 1, day 3, day 7) currently send generic text with no reference to the user's actual research. This makes them feel impersonal and reduces re-engagement. The synthesis data (summary, barriers, winning conditions, best target, strategic recommendation) and stance counts (support/reject/conditional) are generated during run processing but never persisted — they exist only in the result email.

This story persists the synthesis and stance counts to the `runs` table at run completion time, then passes them through the follow-up email pipeline so each follow-up email shows the user's own research results.

---

## Acceptance Criteria

### AC-1: DB Migration — New columns on runs table
**Given** the runs table in Supabase,
**When** migration is applied,
**Then** the following columns are added with NULL default (existing rows are unaffected):
- `support_count INTEGER`
- `reject_count INTEGER`
- `conditional_count INTEGER`
- `synthesis_summary TEXT`
- `synthesis_main_barriers TEXT[]`
- `synthesis_winning_conditions TEXT`
- `synthesis_best_target_segment TEXT`
- `synthesis_strategic_recommendation TEXT`

### AC-2: Synthesis persisted at run completion
**Given** a run completes with synthesis data,
**When** `process_run()` updates the runs table on completion,
**Then** all 8 new columns are written alongside `status`, `persona_count`, `completed_at`, `cost_usd`.
- Stance counts are derived from `result.responses` (count by `stance` field: "support", "reject", "conditional")
- If synthesis is None (not generated), all synthesis columns remain NULL — no error

### AC-3: Follow-up candidates query includes new fields
**Given** the `_fetch_followup_candidates()` helper in email_service.py,
**When** it queries eligible runs,
**Then** it also SELECTs: `topic`, `audience`, `support_count`, `reject_count`, `conditional_count`, `synthesis_summary`, `synthesis_main_barriers`, `synthesis_winning_conditions`, `synthesis_best_target_segment`, `synthesis_strategic_recommendation`

### AC-4: New data passed through follow-up send pipeline
**Given** `send_followup_email()` has access to the enriched run data,
**When** it renders the follow-up email via the frontend API,
**Then** it passes all new fields as props in the render request body.
- Fields that are NULL are passed as `null` in JSON — templates handle gracefully

### AC-5: Frontend render route accepts new props
**Given** the `/api/emails/render-followup` route,
**When** it receives a POST with the new fields,
**Then** it validates and passes them to the email template components.

### AC-6: Follow-up email templates render research summary section
**Given** all three follow-up templates (day1, day3, day7),
**When** rendered with research data present,
**Then** each email includes a "Kutatásod eredménye" section showing:
- Research topic (`topic`)
- Target audience (`audience`)
- Stance bar: "X támogatta · Y feltételes · Z elutasította" out of total
- Synthesis summary text
- Fő akadályok (bulleted list from `synthesis_main_barriers`)
- Sikerhez szükséges (`synthesis_winning_conditions`)
- Kire érdemes fókuszálni (`synthesis_best_target_segment`)
- Stratégiai ajánlás (`synthesis_strategic_recommendation`)

**When** rendered with NULL synthesis data (older runs),
**Then** the section is omitted entirely — no broken layout, no empty fields shown.

### AC-7: Existing follow-up tests updated
**Given** existing pytest tests for `dispatch_followup_sequence` and `send_followup_email`,
**When** tests run after this change,
**Then** all existing tests pass with updated mock data including new fields.

### AC-8: Email layout is consistent with result email design tokens
**Given** the research summary section in follow-up emails,
**When** rendered,
**Then** it uses the same design tokens (`emailBorder`, `emailSurface`, `emailTextPrimary`, `emailTextSecondary`, `accent`) and table-based layout as `result-email.tsx`.

---

## Tasks

### Task 1: Database Migration
- [ ] Create new migration file: `supabase/migrations/20260322004_runs_synthesis_columns.sql`
- [ ] Add 8 new nullable columns to `runs` table (see AC-1)
- [ ] Verify migration does not break existing RLS policy

### Task 2: Backend — Persist synthesis at run completion
- [ ] In `backend/app/services/run_processor.py`, update `process_run()`
- [ ] After `execute_synthesis()` call, count stances from `result.responses`
- [ ] Add new columns to the runs table update dict (lines ~130-137)
- [ ] Handle `synthesis=None` case gracefully (pass `None` values)

### Task 3: Backend — Enrich follow-up query and send pipeline
- [ ] In `backend/app/services/email_service.py`:
  - Update `_fetch_followup_candidates()` SQL SELECT to include 10 new fields (topic, audience + 8 synthesis)
  - Update `RunFollowupCandidate` dataclass/namedtuple (or dict) to carry new fields
  - Update `send_followup_email()` signature and render props to include new fields
  - Update `dispatch_followup_sequence()` to pass new fields through to `send_followup_email()`

### Task 4: Frontend — Render route update
- [ ] In `frontend/app/api/emails/render-followup/route.ts`:
  - Add new optional fields to `FollowUpEmailRenderRequest` interface
  - Pass fields through to template components

### Task 5: Frontend — Email template props and rendering
- [ ] Update `FollowUpEmailProps` interface in all three templates to include new optional fields
- [ ] Create a shared `ResearchSummarySection` inline component (table-based, email-safe HTML)
- [ ] Add section to `follow-up-day1.tsx`, `follow-up-day3.tsx`, `follow-up-day7.tsx`
- [ ] Section renders only when `topic` is present; synthesis sub-sections render only when their data is present

### Task 6: Tests
- [ ] Update backend pytest mocks for `_fetch_followup_candidates` to include new fields
- [ ] Update `send_followup_email` test to assert new props are passed to render API
- [ ] Add test case: NULL synthesis data → section omitted in render request
- [ ] Update frontend email snapshot/render tests if they exist

---

## Technical Implementation Guide

### File Locations

| File | Change Type |
|---|---|
| `supabase/migrations/20260322004_runs_synthesis_columns.sql` | NEW — migration |
| `backend/app/services/run_processor.py` | MODIFY — persist synthesis on completion |
| `backend/app/services/email_service.py` | MODIFY — enrich query + pass props |
| `frontend/app/api/emails/render-followup/route.ts` | MODIFY — new request fields |
| `frontend/emails/follow-up-day1.tsx` | MODIFY — new props + section |
| `frontend/emails/follow-up-day2.tsx` | MODIFY — new props + section |
| `frontend/emails/follow-up-day3.tsx` | MODIFY — new props + section |
| `backend/tests/services/test_followup_email_service.py` | MODIFY — update mocks |

### DB Migration Pattern
Follow existing migration pattern. File naming: `20260322004_runs_synthesis_columns.sql`.
```sql
ALTER TABLE runs
  ADD COLUMN support_count INTEGER,
  ADD COLUMN reject_count INTEGER,
  ADD COLUMN conditional_count INTEGER,
  ADD COLUMN synthesis_summary TEXT,
  ADD COLUMN synthesis_main_barriers TEXT[],
  ADD COLUMN synthesis_winning_conditions TEXT,
  ADD COLUMN synthesis_best_target_segment TEXT,
  ADD COLUMN synthesis_strategic_recommendation TEXT;
```
No RLS change needed — existing `service_role` only policy covers new columns.

### Stance Count Derivation (run_processor.py)
```python
support_count = sum(1 for r in result.responses if r.stance == "support")
reject_count = sum(1 for r in result.responses if r.stance == "reject")
conditional_count = sum(1 for r in result.responses if r.stance == "conditional")
```
Add to the existing update dict alongside `status`, `persona_count`, etc.

### `SynthesisResult` Model (backend/app/models/persona.py)
Already exists:
```python
class SynthesisResult(BaseModel):
    summary: str
    main_barriers: list[str]
    winning_conditions: str
    best_target_segment: str
    strategic_recommendation: str
```
Access as `synthesis.summary`, `synthesis.main_barriers`, etc.

### Follow-up Candidate Query — Current Pattern
`_fetch_followup_candidates()` currently returns run dicts with: `id`, `user_id`, `completed_at`, `status`, `day1_sent`, `day3_sent`, `day7_sent`. Extend SELECT to also fetch all new columns.

### Frontend FollowUpEmailProps Extension
```typescript
export interface FollowUpEmailProps {
  unsubscribe_url: string;
  // New optional research context fields
  topic?: string | null;
  audience?: string | null;
  support_count?: number | null;
  reject_count?: number | null;
  conditional_count?: number | null;
  synthesis_summary?: string | null;
  synthesis_main_barriers?: string[] | null;
  synthesis_winning_conditions?: string | null;
  synthesis_best_target_segment?: string | null;
  synthesis_strategic_recommendation?: string | null;
}
```

### Email Section Design
Use table-based HTML (email-safe, no flexbox/grid). Mirror the visual pattern from `result-email.tsx` — bordered container, label rows in `emailTextSecondary`, values in `emailTextPrimary`, accent color for section dividers. The section sits between the body paragraph and the CTA button.

Section copy structure:
```
[Divider]
"A kutatásod eredménye"   ← section heading
Topic: {topic}
Célközönség: {audience}
Eredmény: X támogatta · Y feltételes · Z elutasította

Összefoglalás: {synthesis_summary}

Fő akadályok:
  • {barrier1}
  • {barrier2}

Sikerhez szükséges: {winning_conditions}
Kire érdemes fókuszálni: {best_target_segment}
Stratégiai ajánlás: {strategic_recommendation}
```

### `FollowUpEmailRenderRequest` Extension (route.ts)
```typescript
export interface FollowUpEmailRenderRequest {
  day: "day1" | "day3" | "day7";
  unsubscribe_url: string;
  topic?: string | null;
  audience?: string | null;
  support_count?: number | null;
  reject_count?: number | null;
  conditional_count?: number | null;
  synthesis_summary?: string | null;
  synthesis_main_barriers?: string[] | null;
  synthesis_winning_conditions?: string | null;
  synthesis_best_target_segment?: string | null;
  synthesis_strategic_recommendation?: string | null;
}
```

---

## Critical Constraints

1. **Null safety everywhere** — Runs completed before this migration have NULL synthesis columns. Every layer (backend, frontend template) must handle null gracefully. The email section MUST be omitted entirely when `topic` is null.
2. **No re-generation** — Do NOT call the synthesis LLM again in the follow-up path. Only use persisted data.
3. **Email-safe HTML only** — No flexbox, no CSS grid, no external fonts in the email section. Table-based layout only. Mirror `result-email.tsx` patterns exactly.
4. **Idempotency preserved** — The `_mark_followup_sent()` SQL condition logic must not be changed.
5. **Migration naming** — Follow the `YYYYMMDDNNN_description.sql` pattern. Use `20260322004`.
6. **No new endpoints** — This story adds no new API routes. All changes are within existing service functions and email templates.
7. **Backend auth unchanged** — The operator endpoint auth (`SWARMSENSE_OPERATOR_API_KEY`) is not modified.

---

## Follow-up Email Copy

The copy below is **already written** in `frontend/lib/messages.ts` under `messages.email.followup`. The dev agent must NOT change this copy — it is finalized. It is included here for reference so the developer understands the email's tone and purpose when building the template layout.

### Day 1
| Field | Value |
|---|---|
| `preview` | Tetszett az eredmény? Mutatunk többet. |
| `title` | Egy futtatás csak az eleje. |
| `body` | Képzeld el, hogy minden kampányüzeneted, árazási döntésed és go-to-market hipotézised előtt lefuttatod ezt. A Pro hozzáférés hamarosan nyílik — iratkozz fel, hogy ne maradj le róla. |

### Day 3
| Field | Value |
|---|---|
| `preview` | Már több százan várják a Pro hozzáférést. |
| `title` | Feliratkoztál már a várólistára? |
| `body` | Az ingyenes próba megmutatta, mire képes a szintetikus kutatás. A Pro verzióval korlátlanul futtathatod — kampányonként, termékenként, piaconként. Az első körben értesítünk. |

### Day 7
| Field | Value |
|---|---|
| `preview` | Utolsó emlékeztető a Pro várólistáról. |
| `title` | Egy hete gondolkodsz — itt az ideje dönteni. |
| `body` | A Pro hozzáférés korlátozott helyszámmal indul. Ha szeretnél az elsők között lenni, most érdemes feliratkozni — utána már csak sorban állás. |

### Shared fields (all days)
| Field | Value |
|---|---|
| `ctaLabel` | Feliratkozás a Pro várólistára |
| `ctaHref` | /blocked |
| `unsubscribeLabel` | Leiratkozás |
| `footerNote` | Ez egy automatikus marketing levél. Bármikor leiratkozhatsz. |

**Email structure per day:**
```
[Brand header: SwarmSense]
[title]
[body]
[Research summary section — only if topic present]
[CTA button: ctaLabel → ctaHref]
[footerNote]
[unsubscribeLabel link]
```

---

## Messages.ts Context

The follow-up email copy in `frontend/lib/messages.ts` under `messages.email.followup` has already been updated (in a separate session) with new title/body/preview text. The new research summary section uses its own inline labels (Hungarian), not messages.ts keys, to keep template logic simple.

Labels to use inline in template (not in messages.ts):
- Section heading: `"A kutatásod eredménye"`
- Topic label: `"Téma"`
- Audience label: `"Célközönség"`
- Synthesis summary label: `"Összefoglalás"`
- Barriers label: `"Fő akadályok"`
- Winning conditions label: `"Sikerhez szükséges"`
- Best target label: `"Kire érdemes fókuszálni"`
- Strategic recommendation label: `"Stratégiai ajánlás"`

---

## Definition of Done

- [ ] Migration applied cleanly against local Supabase
- [ ] `run_processor.py` saves synthesis + stance counts on every completed run
- [ ] Follow-up emails rendered with topic/audience/synthesis when data present
- [ ] Follow-up emails render correctly (no broken layout) when synthesis is NULL
- [ ] All existing backend follow-up tests pass
- [ ] No TypeScript errors in frontend email templates
- [ ] Manual test: trigger a test follow-up render via `/api/emails/render-followup` with and without synthesis data
