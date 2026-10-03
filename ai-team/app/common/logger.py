"""
Logging setup.

    from app.common.logger import get_logger
    logger = get_logger(__name__)

Every line carries the current request id, so one question can be
followed across the API and the worker.
"""

import logging
import sys

from app.common.context import get_request_id

_LOG_FORMAT = "[%(asctime)s] %(levelname)-8s [%(name)s] [%(request_id)s] %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_initialized = False


class _RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


def setup_logging(level: int = logging.INFO) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    global _initialized
    if _initialized:
        return

    root = logging.getLogger("rag")
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
    handler.addFilter(_RequestIdFilter())

    root.addHandler(handler)
    root.propagate = False
    _initialized = True


def get_logger(name: str = "rag") -> logging.Logger:
    if name in {"__main__", "app.server"}:
        name = "server"
    name = name.removeprefix("app.")
    if not name.startswith("rag"):
        name = f"rag.{name}"
    return logging.getLogger(name)
