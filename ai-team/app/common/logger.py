"""
Structured logging setup for the RAG service.

Usage in any module:
    from common.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Query received", extra={"query": query})
"""

import logging
import sys


_LOG_FORMAT = "[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_initialized = False


def setup_logging(level: int = logging.INFO) -> None:
    """
    Initialize the root logger. Call once at application startup.
    """
    global _initialized
    if _initialized:
        return

    root = logging.getLogger("rag")
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))

    root.addHandler(handler)
    _initialized = True


def get_logger(name: str = "rag") -> logging.Logger:
    """
    Get a child logger under the 'rag' namespace.

    Examples:
        get_logger(__name__)
        get_logger("api.routes")
    """
    if not name.startswith("rag"):
        name = f"rag.{name}"
    return logging.getLogger(name)
