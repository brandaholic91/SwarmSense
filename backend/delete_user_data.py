from __future__ import annotations

import argparse
import json
import sys

from app.services.data_deletion_service import delete_user_data_by_email


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Delete SwarmSense user data by email."
    )
    parser.add_argument("--email", required=True, help="Requester email address")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Explicitly confirm destructive deletion",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview deletion counts without deleting data",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        result = delete_user_data_by_email(
            email=args.email,
            confirm=args.confirm,
            dry_run=args.dry_run,
        )
    except ValueError as exc:
        msg = str(exc)
        if "confirmation" in msg:
            print(json.dumps({"status": "guard_blocked", "detail": msg}))
            return 2
        print(json.dumps({"status": "validation_error", "detail": msg}))
        return 1
    except RuntimeError as exc:
        print(json.dumps({"status": "error", "detail": str(exc)}))
        return 3

    print(
        json.dumps(
            {
                "status": "ok",
                "dry_run": result.dry_run,
                "email": result.email,
                "user_found": result.user_found,
                "deleted_rows": result.deleted_rows,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
