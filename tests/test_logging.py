import logging
import sys
from io import StringIO

import pytest

from link_shortener.log_config import configure_logging


@pytest.fixture(autouse=True)
def reset_link_shortener_logging():
    app_logger = logging.getLogger("link_shortener")
    app_logger.handlers.clear()
    app_logger.setLevel(logging.NOTSET)
    app_logger.propagate = True
    yield
    app_logger.handlers.clear()
    app_logger.setLevel(logging.NOTSET)
    app_logger.propagate = True


def test_info_and_below_go_to_stdout(monkeypatch):
    stdout = StringIO()
    stderr = StringIO()
    monkeypatch.setattr(sys, "stdout", stdout)
    monkeypatch.setattr(sys, "stderr", stderr)

    configure_logging(level=logging.DEBUG)
    logger = logging.getLogger("link_shortener.test")
    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")

    out = stdout.getvalue()
    err = stderr.getvalue()

    assert "debug message" in out
    assert "info message" in out
    assert "warning message" not in out
    assert "error message" not in out
    assert "warning message" in err
    assert "error message" in err


def test_configure_logging_is_idempotent():
    configure_logging()
    logger = logging.getLogger("link_shortener")
    handler_count = len(logger.handlers)

    configure_logging()

    assert len(logger.handlers) == handler_count
