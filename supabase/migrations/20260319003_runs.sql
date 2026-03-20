-- Run records for synthetic research lifecycle and follow-up cadence
create table if not exists public.runs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users (id),
  topic text not null,
  audience text not null,
  status text not null default 'queued',
  persona_count integer,
  cost_usd numeric,
  day1_sent boolean not null default false,
  day3_sent boolean not null default false,
  day7_sent boolean not null default false,
  created_at timestamptz not null default now(),
  completed_at timestamptz,
  constraint runs_topic_nonempty check (length(trim(topic)) > 0),
  constraint runs_audience_nonempty check (length(trim(audience)) > 0),
  constraint runs_status_valid check (
    status in ('queued', 'running', 'composing', 'completed', 'partial', 'failed')
  )
);

alter table public.runs enable row level security;

create policy "service_role_only_runs"
on public.runs
for all
using (auth.role() = 'service_role')
with check (auth.role() = 'service_role');
