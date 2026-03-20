-- Magic link token storage for email authentication flow
create table if not exists public.magic_link_tokens (
  token uuid primary key,
  user_id uuid not null references public.users (id),
  expires_at timestamptz not null,
  used_at timestamptz,
  created_at timestamptz not null default now()
);

alter table public.magic_link_tokens enable row level security;

create policy "service_role_only_magic_link_tokens"
on public.magic_link_tokens
for all
using (auth.role() = 'service_role')
with check (auth.role() = 'service_role');
