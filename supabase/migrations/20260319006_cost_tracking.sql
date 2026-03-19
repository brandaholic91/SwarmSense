-- Cost tracking table and pg_cron extension
create table if not exists public.cost_tracking (
  month text primary key,
  total_usd numeric not null default 0,
  constraint cost_tracking_month_format check (month ~ '^[0-9]{4}-[0-9]{2}$')
);

create extension if not exists pg_cron with schema extensions;
