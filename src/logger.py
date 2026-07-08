"""Structured logging configuration."""

import logging
import sys
from pathlib import Path


def setup_logger(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    """Configure structured logging."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Console handler with formatted output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Format: timestamp | level | module | message
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler.setFormatter(formatter)

    # Only add handler if it doesn't already exist
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger


# Create default logger
logger = setup_logger("360-LR")
