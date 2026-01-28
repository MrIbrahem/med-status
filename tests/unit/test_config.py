"""Test configuration module."""

import pytest
from src import config


@pytest.mark.unit
def test_current_year_is_string():
    """Test CURRENT_YEAR is a string."""
    assert isinstance(config.CURRENT_YEAR, str)
    assert len(config.CURRENT_YEAR) == 4
    assert config.CURRENT_YEAR.isdigit()


@pytest.mark.unit
def test_last_year_is_string():
    """Test LAST_YEAR is a string."""
    assert isinstance(config.LAST_YEAR, str)
    assert len(config.LAST_YEAR) == 4
    assert config.LAST_YEAR.isdigit()


@pytest.mark.unit
def test_batch_size():
    """Test batch size is reasonable."""
    assert config.BATCH_SIZE > 0
    assert config.BATCH_SIZE <= 1000


@pytest.mark.unit
def test_output_dirs():
    """Test output directories are defined."""
    assert "languages" in config.OUTPUT_DIRS
    assert "editors" in config.OUTPUT_DIRS
    assert "reports" in config.OUTPUT_DIRS


@pytest.mark.unit
def test_database_config():
    """Test database configuration exists."""
    assert isinstance(config.DATABASE_CONFIG, dict)
    assert "charset" in config.DATABASE_CONFIG
    assert config.DATABASE_CONFIG["charset"] == "utf8mb4"


@pytest.mark.unit
def test_max_retries():
    """Test MAX_RETRIES is positive."""
    assert config.MAX_RETRIES > 0
    assert config.MAX_RETRIES <= 10
