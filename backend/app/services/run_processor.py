from __future__ import annotations


def dispatch_run_processing(
    *,
    run_id: str,
    user_id: str,
    topic: str,
    audience: str,
) -> None:
    # Story 4.2 dispatch seam only; heavy persona processing is implemented in Story 4.3.
    _ = (run_id, user_id, topic, audience)
