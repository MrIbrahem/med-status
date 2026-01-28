"""Test logging configuration."""

import pytest
import logging
from src.logging_config import setup_logging, get_logger


@pytest.mark.unit
def test_setup_logging_default():
    """Test default logging setup."""
    setup_logging()
    logger = get_logger("test")
    assert logger is not None
    assert isinstance(logger, logging.Logger)


@pytest.mark.unit
def test_get_logger():
    """Test logger creation."""
    logger = get_logger(__name__)
    assert logger.name == __name__
    assert isinstance(logger, logging.Logger)


@pytest.mark.unit
def test_setup_logging_levels():
    """Test different log levels."""
    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        setup_logging(level=level)
        logger = get_logger("test_level")
        assert logger is not None


@pytest.mark.unit
def test_all_log_levels(capsys):
    """Test all log levels output."""
    setup_logging(level="DEBUG")
    logger = get_logger("test")

    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    captured = capsys.readouterr()
    assert "Debug message" in captured.out
    assert "Info message" in captured.out
    assert "Warning message" in captured.out
    assert "Error message" in captured.out
