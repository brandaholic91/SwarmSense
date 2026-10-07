import logging


def test_run_summary_logger_is_enabled_with_a_single_handler():
    # Az import a tesztben van, mert az app modul import-kor létrehozza az appot.
    from app.main import create_app

    create_app()
    create_app()

    assert logging.getLogger("swarmsense.run").isEnabledFor(logging.INFO)
    assert len(logging.getLogger("swarmsense").handlers) == 1
