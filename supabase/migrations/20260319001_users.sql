-- Users table with RLS and email normalization
create table if not exists public.users (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  has_consent boolean not null,
  consent_timestamp timestamptz,
  unsubscribed_at timestamptz,
  created_at timestamptz not null default now(),
  constraint users_email_unique unique (email),
  constraint users_email_normalized check (email = lower(trim(email)))
);

alter table public.users enable row level security;
