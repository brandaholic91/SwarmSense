-- Qualifier survey answers linked to a queued run
create table if not exists public.qualifier_responses (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references public.runs (id) on delete cascade,
  user_id uuid not null references public.users (id),
  role_answer text not null,
  use_case_answer text not null,
  created_at timestamptz not null default now(),
  constraint qualifier_role_answer_nonempty check (length(trim(role_answer)) > 0),
  constraint qualifier_use_case_answer_nonempty check (length(trim(use_case_answer)) > 0)
);

alter table public.qualifier_responses enable row level security;

create policy "service_role_only_qualifier_responses"
on public.qualifier_responses
for all
using (auth.role() = 'service_role')
with check (auth.role() = 'service_role');
