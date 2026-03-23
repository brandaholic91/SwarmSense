alter table public.cost_tracking
add column if not exists alert_80_sent_at timestamptz;
