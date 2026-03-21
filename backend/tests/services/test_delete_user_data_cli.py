from __future__ import annotations

import json

from app.services.data_deletion_service import DeletionExecutionResult

import delete_user_data


def test_cli_rejects_invalid_email(capsys) -> None:
    code = delete_user_data.main(["--email", "invalid", "--confirm"])

    captured = json.loads(capsys.readouterr().out)
    assert code == 2
    assert captured["status"] == "validation_error"


def test_cli_requires_confirm(capsys) -> None:
    code = delete_user_data.main(["--email", "user@example.com"])

    captured = json.loads(capsys.readouterr().out)
    assert code == 2
    assert captured == {
        "status": "guard_blocked",
        "detail": "Deletion requires --confirm",
        "email": "user@example.com",
    }


def test_cli_executes_dry_run(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        delete_user_data,
        "delete_user_data_by_email",
        lambda **_kwargs: DeletionExecutionResult(
            email="user@example.com",
            user_found=True,
            dry_run=True,
            deleted_rows={
                "qualifier_responses": 2,
                "runs": 1,
                "magic_link_tokens": 1,
                "waitlist": 1,
                "users": 1,
            },
        ),
    )

    code = delete_user_data.main(
        ["--email", "User@Example.com", "--confirm", "--dry-run"]
    )

    captured = json.loads(capsys.readouterr().out)
    assert code == 0
    assert captured == {
        "status": "ok",
        "dry_run": True,
        "email": "user@example.com",
        "user_found": True,
        "deleted_rows": {
            "qualifier_responses": 2,
            "runs": 1,
            "magic_link_tokens": 1,
            "waitlist": 1,
            "users": 1,
        },
    }
