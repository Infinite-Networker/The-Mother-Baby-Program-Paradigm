"""
Logger utility for the Mother-Baby Paradigm.
Created by: Cherry Computer Ltd.
"""

import logging
import sys
from typing import Optional


_loggers = {}

def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Return a named logger with consistent formatting.

    Args:
        name: Logger name (usually the class/module name).
        level: Log level string ("DEBUG", "INFO", "WARNING", "ERROR").

    Returns:
        A configured logging.Logger instance.
    """
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(f"MBPP.{name}")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    _loggers[name] = logger
    return logger
