# Story 1.2: Database Foundation — Users & Cost Tracking Schema

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want the `users` and `cost_tracking` database tables created with RLS policies,
so that user records and monthly API spend tracking are securely in place before any auth or cost enforcement logic is built.

## Acceptance Criteria

1. Given a running local Supabase instance, when migration files `20260319_001_users.sql` and `20260319_006_cost_tracking.sql` are applied via `supabase db push`, then the `users` table exists with columns: `id` (UUID PK), `email` (text unique not null), `has_consent` (boolean not null), `consent_timestamp` (timestamptz), `unsubscribed_at` (timestamptz null), `created_at` (timestamptz default now()).
2. The `cost_tracking` table exists with columns: `month` (text PK, format YYYY-MM), `total_usd` (numeric not null default 0).
3. A Supabase RLS policy is active on `users` ensuring no row is readable or writable without the service role key.
4. Running `SELECT * FROM users` from the Supabase anonymous client returns an empty result (RLS blocks access).
5. Email values are stored in normalized form (lowercase, trimmed) as enforced by a check constraint or migration note.
6. The pg_cron extension is enabled in the Supabase project, verified by `SELECT extname FROM pg_extension WHERE extname = 'pg_cron'` returning one row (required by Story 5.4 follow-up scheduling).

## Tasks / Subtasks

- [ ] Create `supabase/migrations/20260319_001_users.sql` (AC: 1, 3, 5)
  - [ ] Create `users` table with required columns and defaults (`created_at` default `now()`, `id` UUID PK default `gen_random_uuid()` if available).
  - [ ] Add unique constraint on `email` and a normalization check constraint (e.g., `email = lower(trim(email))`).
  - [ ] Enable RLS on `users` and ensure no anon/authenticated policies are added (service role bypass only).
- [ ] Create `supabase/migrations/20260319_006_cost_tracking.sql` (AC: 2, 6)
  - [ ] Create `cost_tracking` table with `month` TEXT PK and `total_usd` NUMERIC NOT NULL DEFAULT 0.
  - [ ] Add format guard for `month` (e.g., `CHECK (month ~ '^[0-9]{4}-[0-9]{2}$')`).
  - [ ] Enable `pg_cron` extension (`create extension if not exists pg_cron with schema extensions;`) if not already enabled.
- [ ] Apply and verify migrations locally (AC: 1, 2, 4, 6)
  - [ ] Run `supabase db push`.
  - [ ] Verify schema in Supabase Studio or via SQL: `\d users`, `\d cost_tracking`.
  - [ ] Verify `pg_cron` installed: `SELECT extname FROM pg_extension WHERE extname = 'pg_cron';`.
  - [ ] Verify RLS blocks anon access: query `SELECT * FROM users` using anon key returns 0 rows / permission denied.

## Dev Notes

- Use Supabase CLI migrations only; place files in `supabase/migrations/` with exact names `20260319_001_users.sql` and `20260319_006_cost_tracking.sql` (no extra migrations in this story).
- RLS requirement is “service role only”: enable RLS on `users` and do not add anon/authenticated policies. The service role bypasses RLS by default.
- Email normalization must be enforced at the DB layer with a check constraint or explicit note in the migration (even though the API will normalize at input boundary later).
- Keep to architecture naming conventions (`snake_case` tables/columns, `idx_{table}_{column}` if adding indexes).
- Do not introduce new tooling or infrastructure files; scope is DB schema only.

### Project Structure Notes

- Migrations live under `supabase/migrations/` and are applied with `supabase db push`.
- Tables required at MVP: `users` and `cost_tracking` are part of the core schema list; other tables (magic_link_tokens, runs, qualifier_responses, waitlist) are handled in later stories.

### References

- `_bmad-output/planning-artifacts/epics.md#Story 1.2` (acceptance criteria, migration filenames, RLS, pg_cron requirement)
- `_bmad-output/planning-artifacts/architecture.md#Data Architecture` (Supabase CLI migrations, core tables list)
- `_bmad-output/planning-artifacts/architecture.md#Naming Patterns` (snake_case, index naming)
- `_bmad-output/planning-artifacts/architecture.md#Format Patterns` (email normalization rule)

## Dev Agent Record

### Agent Model Used

openai/gpt-5.2-codex

### Debug Log References

### Completion Notes List

### File List
