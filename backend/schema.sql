create table if not exists runs (
  id uuid primary key default gen_random_uuid(),
  topic text not null check (length(trim(topic)) > 0),
  audience text not null check (length(trim(audience)) > 0),
  status text not null default 'queued'
    check (status in ('queued', 'running', 'composing', 'completed', 'partial', 'failed')),
  persona_count integer not null default 0,
  support_count integer,
  reject_count integer,
  conditional_count integer,
  synthesis_summary text,
  synthesis_main_barriers text[],
  synthesis_winning_conditions text,
  synthesis_best_target_segment text,
  synthesis_strategic_recommendation text,
  result jsonb,
  pdf bytea,
  is_sample boolean not null default false,
  ip_hash text,
  input_tokens integer not null default 0,
  output_tokens integer not null default 0,
  created_at timestamptz not null default now(),
  completed_at timestamptz
);
create index if not exists runs_created_at_idx on runs (created_at);
create index if not exists runs_ip_hash_created_at_idx on runs (ip_hash, created_at);

create table if not exists run_events (
  id bigserial primary key,
  run_id uuid not null references runs (id) on delete cascade,
  type text not null,
  persona_index integer,
  persona_name text,
  attempt integer,
  error_code text,
  duration_ms integer,
  input_tokens integer,
  output_tokens integer,
  created_at timestamptz not null default now()
);
create index if not exists run_events_run_id_id_idx on run_events (run_id, id);

create table if not exists email_requests (
  id bigserial primary key,
  run_id uuid not null references runs (id) on delete cascade,
  email text not null,
  created_at timestamptz not null default now(),
  sent_at timestamptz
);
create index if not exists email_requests_created_at_idx on email_requests (created_at);
