-- Users table with RLS and email normalization
create table if not exists public.users (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  has_consent boolean not null,
  consent_timestamp timestamptz,
  unsubscribed_at timestamptz,
  created_at timestamptz not null default now(),
  constraint users_email_unique unique (email),
  constraint users_email_normalized check (email = lower(trim(email))),
  constraint users_email_nonempty check (length(email) > 0),
  constraint users_consent_ts check (not has_consent or consent_timestamp is not null),
  constraint users_unsub_after_created check (unsubscribed_at is null or unsubscribed_at >= created_at)
);

-- RLS enabled; no anon/authenticated policies added.
-- Service role bypasses RLS by default in Supabase.
alter table public.users enable row level security;
