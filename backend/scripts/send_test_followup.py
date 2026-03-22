#!/usr/bin/env python3
"""
Test script: send a follow-up email directly, bypassing DB eligibility checks.

Usage:
    cd backend
    python scripts/send_test_followup.py --to your@email.com --day day1
    python scripts/send_test_followup.py --to your@email.com --day day3
    python scripts/send_test_followup.py --to your@email.com --day day7
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make sure the app is importable from the backend root
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.email_service import send_followup_email

VALID_DAYS = ("day1", "day3", "day7")


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a test follow-up email.")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument(
        "--day",
        required=True,
        choices=VALID_DAYS,
        help="Which follow-up to send: day1 | day3 | day7",
    )
    parser.add_argument(
        "--user-id",
        default="test-user-id",
        help="User ID used for the unsubscribe link (default: test-user-id)",
    )
    args = parser.parse_args()

    print(f"Sending {args.day} follow-up to {args.to} ...")
    send_followup_email(recipient_email=args.to, day=args.day, user_id=args.user_id)
    print("Done.")


if __name__ == "__main__":
    main()
