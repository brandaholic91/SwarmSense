#!/usr/bin/env python3
"""
Test script: send a follow-up email directly, bypassing DB eligibility checks.

Usage — manual recipient:
    cd backend
    python scripts/send_test_followup.py --to your@email.com --day day1
    python scripts/send_test_followup.py --to your@email.com --day day3 --user-id <uuid>

Usage — from a run (fetches recipient, synthesis data automatically):
    python scripts/send_test_followup.py --run-id <uuid> --day day1
    python scripts/send_test_followup.py --run-id <uuid> --day all
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make sure the app is importable from the backend root
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import get_supabase_client
from app.services.email_service import send_followup_email

VALID_DAYS = ("day1", "day3", "day7", "all")


def _fetch_run(run_id: str) -> dict:
    supabase = get_supabase_client()
    resp = (
        supabase.table("runs")
        .select(
            "id, topic, audience, support_count, reject_count, conditional_count,"
            " synthesis_summary, synthesis_main_barriers, synthesis_winning_conditions,"
            " synthesis_best_target_segment, synthesis_strategic_recommendation,"
            " users(id, email)"
        )
        .eq("id", run_id)
        .single()
        .execute()
    )
    if not resp.data:
        print(f"Run {run_id!r} not found.", file=sys.stderr)
        sys.exit(1)
    return resp.data


def _send(*, recipient_email: str, day: str, user_id: str, run: dict | None) -> None:
    kwargs: dict = {}
    if run:
        kwargs = dict(
            topic=run.get("topic"),
            audience=run.get("audience"),
            support_count=run.get("support_count"),
            reject_count=run.get("reject_count"),
            conditional_count=run.get("conditional_count"),
            synthesis_summary=run.get("synthesis_summary"),
            synthesis_main_barriers=run.get("synthesis_main_barriers"),
            synthesis_winning_conditions=run.get("synthesis_winning_conditions"),
            synthesis_best_target_segment=run.get("synthesis_best_target_segment"),
            synthesis_strategic_recommendation=run.get("synthesis_strategic_recommendation"),
        )
    print(f"Sending {day} follow-up to {recipient_email} ...")
    send_followup_email(recipient_email=recipient_email, day=day, user_id=user_id, **kwargs)
    print(f"{day} done.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a test follow-up email.")
    parser.add_argument("--run-id", help="Fetch recipient and synthesis data from this run ID")
    parser.add_argument("--to", help="Recipient email address (required without --run-id)")
    parser.add_argument(
        "--day",
        required=True,
        choices=VALID_DAYS,
        help="Which follow-up to send: day1 | day3 | day7 | all",
    )
    parser.add_argument(
        "--user-id",
        default="test-user-id",
        help="User ID for the unsubscribe link (ignored when --run-id is set)",
    )
    args = parser.parse_args()

    if args.run_id:
        run = _fetch_run(args.run_id)
        user = run["users"]
        recipient_email = user["email"]
        user_id = user["id"]
    else:
        if not args.to:
            parser.error("--to is required when --run-id is not provided")
        run = None
        recipient_email = args.to
        user_id = args.user_id

    days = ("day1", "day3", "day7") if args.day == "all" else (args.day,)
    for day in days:
        _send(recipient_email=recipient_email, day=day, user_id=user_id, run=run)


if __name__ == "__main__":
    main()
