-- Waitlist signup table for returning users blocked from free reruns
create table if not exists public.waitlist (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  created_at timestamptz not null default now(),
  constraint waitlist_email_unique unique (email),
  constraint waitlist_email_normalized check (email = lower(trim(email))),
  constraint waitlist_email_nonempty check (length(email) > 0)
);

alter table public.waitlist enable row level security;
