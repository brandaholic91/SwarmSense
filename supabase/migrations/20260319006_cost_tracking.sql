-- Cost tracking table, RLS, and pg_cron extension
create schema if not exists extensions;

create table if not exists public.cost_tracking (
  month text primary key,
  total_usd numeric not null default 0,
  constraint cost_tracking_month_format check (month ~ '^[0-9]{4}-(0[1-9]|1[0-2])$'),
  constraint cost_tracking_nonneg check (total_usd >= 0)
);

-- RLS enabled; service role bypasses by default.
alter table public.cost_tracking enable row level security;

create extension if not exists pg_cron with schema extensions;
