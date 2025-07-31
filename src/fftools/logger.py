import logging
import sys
from pathlib import Path
from typing import Any

from loguru import logger


LOGURU_FMT = "{time:%Y-%m-%dT%H:%M:%S%z} <level>[{level: <7}]</level> [{name: <10}] [{function: <20}]: {message}"


class InterceptHandler(logging.Handler):
    """Intercept python logging messages and log them via loguru.logger."""

    def emit(self, record: Any) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # pyright:ignore
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def prepare_logger(loglevel: int = 20, logfile: Path | None = None) -> None:
    """init logger with specified loglevel and logfile.

    Args:
        loglevel: level to set. 10 = debug, 20 = info, 30 = warning, etc.
        logfile: logfile to write log messages into.
    """
    stdout_handler: dict[str, Any] = {
        "sink": sys.stdout,
        "level": loglevel,
        "format": LOGURU_FMT,
    }
    file_handler: dict[str, Any] = {
        "sink": logfile,
        "level": loglevel,
        "format": LOGURU_FMT,
    }
    handlers = [stdout_handler, file_handler] if logfile else [stdout_handler]

    logging.basicConfig(handlers=[InterceptHandler()], level=loglevel)
    logger.configure(handlers=handlers)  # pyright: ignore
