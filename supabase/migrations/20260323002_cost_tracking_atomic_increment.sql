-- Atomic monthly cost increment with threshold detection.
-- Replaces the read-compute-write pattern in run_processor.py with a single
-- locked DB operation, eliminating the race condition where concurrent runs
-- could double-fire the 80% Sentry alert or produce an incorrect total.
create or replace function public.increment_monthly_cost(
  p_month text,
  p_run_cost numeric,
  p_threshold_usd numeric default 40.00
)
returns jsonb
language plpgsql
security definer
as $$
declare
  v_old_total        numeric;
  v_new_total        numeric;
  v_old_alert_at     timestamptz;
  v_alert_triggered  boolean := false;
begin
  -- Ensure the row exists before acquiring the lock.
  insert into public.cost_tracking (month, total_usd)
  values (p_month, 0)
  on conflict (month) do nothing;

  -- Lock the row for atomic read-modify-write.
  select total_usd, alert_80_sent_at
    into v_old_total, v_old_alert_at
    from public.cost_tracking
   where month = p_month
     for update;

  v_new_total := coalesce(v_old_total, 0) + p_run_cost;

  -- Detect first threshold crossing this month.
  if v_old_total < p_threshold_usd
     and v_new_total >= p_threshold_usd
     and v_old_alert_at is null
  then
    v_alert_triggered := true;
  end if;

  update public.cost_tracking
     set total_usd       = v_new_total,
         alert_80_sent_at = case
           when v_alert_triggered then now()
           else alert_80_sent_at
         end
   where month = p_month;

  return jsonb_build_object(
    'total_usd',       v_new_total,
    'alert_triggered', v_alert_triggered
  );
end;
$$;
