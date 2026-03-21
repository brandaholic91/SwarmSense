-- Enforce one qualifier response per run (idempotency guard)
alter table public.qualifier_responses
  add constraint qualifier_responses_run_id_unique unique (run_id);
