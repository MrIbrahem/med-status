"""
Logging configuration with colored output.
"""

import logging
import sys
from pathlib import Path

import colorlog


def prepare_log_file(log_file, project_logger):
    log_file = Path(log_file).expanduser()
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        project_logger.error(f"Failed to create log directory: {e}")
        log_file = None
    return log_file


def setup_logging(
    level: str = "INFO",
    name: str = "status",
    log_file: str | None = None,
) -> None:
    """
    Configure colored logging for console and optional file output.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output

    Example:
        >>> setup_logging(level="DEBUG", log_file="app.log")
    """
    project_logger = logging.getLogger(name)

    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO) if isinstance(level, str) else level

    # Create color formatter for console
    console_formatter = colorlog.ColoredFormatter(
        fmt="%(log_color)s%(asctime)s - %(name)s - %(levelname)-8s%(reset)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(numeric_level)

    # Root logger configuration
    project_logger.setLevel(numeric_level)
    project_logger.addHandler(console_handler)

    # Optional file handler (no colors)
    if log_file:
        log_file = prepare_log_file(log_file, project_logger)
        setup_file_handler(project_logger, log_file, numeric_level)

    # Silence noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("pymysql").setLevel(logging.WARNING)


def setup_file_handler(project_logger, log_file, level):
    file_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)-8s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(level)
    project_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Module initialized")
    """
    return logging.getLogger(name)
