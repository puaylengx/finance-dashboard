import logging
import os
from logging.handlers import RotatingFileHandler

import colorlog

_LOG_COLORS = {
    "DEBUG":    "cyan",
    "INFO":     "green",
    "WARNING":  "yellow",
    "ERROR":    "red",
    "CRITICAL": "bold_red",
}

_CONSOLE_FMT = "%(log_color)s%(levelname)-8s %(asctime)s [%(name)s] %(message)s%(reset)s"
_FILE_FMT    = "%(levelname)-8s %(asctime)s [%(name)s] %(message)s"
_DATE_FMT    = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    from app.core.config import settings

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.propagate = False
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(level)

    console = colorlog.StreamHandler()
    console.setFormatter(colorlog.ColoredFormatter(
        _CONSOLE_FMT,
        datefmt=_DATE_FMT,
        log_colors=_LOG_COLORS,
        reset=True,
    ))
    logger.addHandler(console)

    log_dir = settings.log_dir
    os.makedirs(log_dir, exist_ok=True)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=10,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter(_FILE_FMT, datefmt=_DATE_FMT))
    logger.addHandler(file_handler)

    return logger
