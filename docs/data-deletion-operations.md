# Data Deletion Request Operations

This runbook defines the MVP process for handling GDPR Article 17 data deletion requests in SwarmSense.

## Scope and Intake Channel

- Intake mailbox: `privacy@swarmsense.ai`
- Request channel (MVP): email only
- No public self-service deletion portal is provided in MVP

## SLA Guardrails

- Acknowledge request within 15 minutes of receipt
- Complete deletion within 7 calendar days
- Send completion confirmation email immediately after deletion

## Operator Accountability

- Primary owner: on-duty operator assigned for compliance workflows
- Backup owner: secondary operator for weekends/holidays
- Escalation trigger: if acknowledgement exceeds 10 minutes or completion reaches day 6 without closure

## Validation Checklist

Before deletion execution, confirm all checks:

1. Request received from the email address to be deleted, or identity validated through a reply confirmation.
2. Email normalized to lowercase and trimmed form.
3. Request logged with timestamp and operator initials.
4. CLI command prepared with `--dry-run` first, then `--confirm`.

## Execution Procedure

Run from repository root:

```bash
python backend/delete_user_data.py --email "user@example.com" --dry-run --confirm
python backend/delete_user_data.py --email "user@example.com" --confirm
```

Expected output fields:

- `status`
- `email`
- `user_found`
- `dry_run`
- `deleted_rows` per table (`users`, `runs`, `qualifier_responses`, `magic_link_tokens`, `waitlist`)

## Mailbox Templates (Hungarian)

Use the exact templates below.

### Acknowledgement (<= 15 minutes)

- Subject: `SwarmSense adatorlesi kerelem - visszaigazolas`
- Body: `Koszonjuk, hogy jelezted adatorlesi igenyedet. A kerelmet rogzitettuk, es legkesobb 15 percen belul visszaigazoljuk. A torlest legkesobb 7 naptari napon belul elvegezzuk, majd kulon megerosito emailt kuldunk.`

### Completion (<= 7 calendar days)

- Subject: `SwarmSense adatorlesi kerelem - teljesitve`
- Body: `Ezuton megerositjuk, hogy a kapcsolodo szemelyes adataid torleset elvegeztuk a kerelem beadasatol szamitott 7 naptari napon belul.`

## Logging and Audit Expectations

Log all timestamps in ISO 8601 UTC format:

- `request_received_at`
- `ack_sent_at`
- `deletion_completed_at`
- `completion_email_sent_at`

Record alongside:

- requester email (normalized)
- operator id/initials
- deletion result payload (`deleted_rows`)
- any exception/fallback notes

## Weekend and Holiday Escalation

- If primary operator is unavailable, backup owner must acknowledge within SLA.
- If both owners are unavailable, escalate to incident channel and compliance lead immediately.
- If SLA breach risk exists, send interim status update to requester before SLA expiry.
