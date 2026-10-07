"""A kiválasztott futás exportja a seed fájlba.

Használat (a backend/ mappából): python -m scripts.export_sample <run_id>
"""

from __future__ import annotations

import sys
from collections import Counter

from app import db

REQUIRED_EVENTS = ("persona_retry", "persona_failed")


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("Használat: python -m scripts.export_sample <run_id>", file=sys.stderr)
        return 2
    run_id = argv[0]
    try:
        sql_text = db.export_sample_sql(run_id)
    except (LookupError, ValueError):
        print(f"Nincs ilyen futás: {run_id}", file=sys.stderr)
        return 1

    counts = Counter(event["type"] for event in db.list_events(run_id))
    missing = [name for name in REQUIRED_EVENTS if counts[name] == 0]
    if missing:
        print(
            f"A futás nem használható mintának, hiányzó esemény: {', '.join(missing)}",
            file=sys.stderr,
        )
        return 1

    db.SEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    db.SEED_PATH.write_text(sql_text, encoding="utf-8")
    print(f"Kiírva: {db.SEED_PATH}")
    for event_type, count in sorted(counts.items()):
        print(f"{event_type}: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
