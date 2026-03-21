# Follow-up Cron Operations

This document defines the daily Supabase `pg_cron` invocation for Story 5.4.

## Schedule

- Frequency: once per day
- Suggested UTC schedule: `0 7 * * *`
- Trigger target: `POST /api/v1/operator/send-followups`

## Secure HTTP Invocation

Use a static Bearer token (`SWARMSENSE_OPERATOR_API_KEY`) and never expose it client-side.

```sql
select
  cron.schedule(
    'swarmsense_followups_daily',
    '0 7 * * *',
    $$
      select
        net.http_post(
          url := 'https://<backend-domain>/api/v1/operator/send-followups',
          headers := jsonb_build_object(
            'Authorization', 'Bearer <SWARMSENSE_OPERATOR_API_KEY>',
            'Content-Type', 'application/json'
          ),
          body := '{}'::jsonb
        );
    $$
  );
```

## Verification

1. Run the endpoint manually with valid token and verify `{"sent": N}` response.
2. Confirm `runs.day1_sent/day3_sent/day7_sent` flip to `true` only after successful sends.
3. Confirm users with `users.unsubscribed_at IS NOT NULL` are skipped.
4. Confirm Sentry events include day/run/user/timestamp context for skip/failure/success paths.
