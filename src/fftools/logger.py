import logging
import re
import sys
from pathlib import Path
from typing import Any

from loguru import logger
from whenever import Instant, ZonedDateTime


class Timestamp:
    """timestamp class for logging related strings."""

    def __init__(self, timezone="Europe/Zurich", timestamp_format="%Y-%m-%dT%H:%M:%S") -> None:
        """set timezone and format specific preferences.

        Args:
            timezone: timezone to use for timestamps.
                Defaults to DEFAULT_TIMEZONE.
            timestamp_format: `strftime` format string to use for timestamps.
                Defaults to DEFAULT_TS_FULL.
        """
        self.timezone = timezone
        self.timestamp_format = timestamp_format

    @property
    def datetime(self) -> ZonedDateTime:
        return Instant.now().to_tz(self.timezone)

    @property
    def now(self) -> str:
        return self.datetime.py_datetime().strftime(self.timestamp_format)  # type: ignore[no-any-return]

    @property
    def now_crossplatform(self) -> str:
        return re.sub(r'"|:|<|>|/|\\|\||\?|\*', "_", self.now)

    @property
    def ts_ymd(self) -> str:
        return self.datetime.py_datetime().strftime("%Y-%m-%d")  # type: ignore[no-any-return]

    @property
    def ts_hms(self) -> str:
        return self.datetime.py_datetime().strftime("%H:%M:%S")  # type: ignore[no-any-return]


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
    logfmt = "{time:%Y-%m-%dT%H:%M:%S%z} <level>[{level: <7}]</level> [{name: <10}] [{function: <20}]: {message}"

    stdout_handler: dict[str, Any] = {
        "sink": sys.stdout,
        "level": loglevel,
        "format": logfmt,
    }
    file_handler: dict[str, Any] = {
        "sink": logfile,
        "level": loglevel,
        "format": logfmt,
    }
    handlers = [stdout_handler, file_handler] if logfile else [stdout_handler]

    logging.basicConfig(handlers=[InterceptHandler()], level=loglevel)
    logger.configure(handlers=handlers)  # pyright: ignore[reportArgumentType]
