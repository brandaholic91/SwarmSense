"""A kiválasztott futás exportja a seed fájlba.

Használat (a backend/ mappából): python -m scripts.export_sample <run_id>
"""

from __future__ import annotations

import sys
from collections import Counter

from app import db


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

    # A minta a teljes terméket mutatja: csak befejezett, összefoglalóval záruló futás jó.
    run = db.get_run(run_id)
    if run is None or run["status"] != "completed":
        print(
            "A futás nem használható mintának: nem 'completed' állapotú.",
            file=sys.stderr,
        )
        return 1

    counts = Counter(event["type"] for event in db.list_events(run_id))

    db.SEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    db.SEED_PATH.write_text(sql_text, encoding="utf-8")
    print(f"Kiírva: {db.SEED_PATH}")
    for event_type, count in sorted(counts.items()):
        print(f"{event_type}: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
