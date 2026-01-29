# Wikipedia Medicine Project - Implementation Plan v2.0

## Project Overview

A Python application to retrieve and analyze editor contributions across Wikipedia's Medicine projects in multiple languages. This updated plan incorporates all best practices, configurations, and guidelines.

## 📚 Reference Documentation

Before starting implementation, review:

- **Project Setup**: `plans/setup.md` - All config files
- **Claude Guidance**: `.claude/` directory - AI assistance best practices
- **Color Logging**: `.claude/context/color_logging_guide.md` - Logging implementation
- **Architecture**: `.claude/context/architecture.md` - System design
- **Database Schema**: `.claude/context/database_schema.md` - DB reference
- **Conventions**: `.claude/context/conventions.md` - Code standards

---

## Project Structure (Updated)

```
wikipedia-medicine/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Entry point with CLI
│   ├── logging_config.py          # Color logging setup
│   ├── database.py                # Database connection management
│   ├── queries.py                 # SQL query templates
│   ├── processor.py               # Data processing logic
│   ├── reports.py                 # Report generation
│   ├── config.py                  # Configuration constants
│   └── utils.py                   # Helper functions
├── tests/
│   ├── unit/
│   │   ├── test_database.py
│   │   ├── test_processor.py
│   │   ├── test_queries.py
│   │   ├── test_reports.py
│   │   ├── test_utils.py
│   │   └── test_logging_config.py
│   └── integration/
│       ├── test_queries.py
│       └── test_workflow.py
├── languages/                     # Article titles per language
├── editors/                       # Editor statistics per language
├── reports/                       # Generated reports
├── .claude/                       # Claude AI guidance
│   ├── README.md
│   ├── CLAUDE.md
│   ├── settings.json
│   ├── prompts/
│   │   └── templates.md
│   ├── context/
│   │   ├── architecture.md
│   │   ├── database_schema.md
│   │   ├── conventions.md
│   │   └── color_logging_guide.md
│   └── examples/s
│       └── prompt_examples.md
├── .github/
│   └── workflows/
│       ├── pytest.yml
│       └── lint.yml
├── pytest.ini
├── pyproject.toml                 # Modern Python config
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── LICENSE
├── .gitignore
├── .flake8
├── .pre-commit-config.yaml
└── Makefile
```

---

## Implementation Order

### Phase 1: Setup & Configuration ✅

**Files to create first** (from `plans/setup.md`):

1. **Directory structure**
   ```bash
   mkdir -p src tests/{unit,integration} languages editors reports .claude/{prompts,context,examples}
   ```

2. **Configuration files**
   - `requirements.txt` - Production dependencies
   - `requirements-dev.txt` - Development dependencies
   - `.gitignore` - Ignore patterns
   - `pytest.ini` - Test configuration
   - `pyproject.toml` - Black, isort, mypy config
   - `.flake8` - Linting configuration
   - `.pre-commit-config.yaml` - Pre-commit hooks

3. **Documentation**
   - `README.md` - Project overview
   - `CONTRIBUTING.md` - Contribution guidelines
   - `LICENSE` - MIT license
   - `CHANGELOG.md` - Version history

4. **Claude guidance** (Already created)
   - `.claude/README.md`
   - `.claude/CLAUDE.md`
   - `.claude/settings.json`
   - `.claude/prompts/templates.md`
   - `.claude/context/architecture.md`
   - `.claude/context/database_schema.md`
   - `.claude/context/conventions.md`
   - `.claude/context/color_logging_guide.md`
   - `.claude/examples/prompt_examples.md`

5. **CI/CD**
   - `.github/workflows/pytest.yml`
   - `.github/workflows/lint.yml`

**Checklist**:
- [ ] Create directory structure
- [ ] Add all configuration files
- [ ] Initialize git repository
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Setup pre-commit hooks

---

### Phase 2: Core Infrastructure 🔨

**Order of implementation**:

#### 1. Logging Configuration (NEW - Start here!)

**File**: `src/logging_config.py`

**Reference**: `.claude/context/color_logging_guide.md`

```python
"""
Logging configuration with colored output.

See .claude/context/color_logging_guide.md for full documentation.
"""
import logging
import sys
from typing import Optional

import colorlog


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configure colored logging for console and optional file output.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output

    Example:
        >>> setup_logging(level="DEBUG", log_file="app.log")
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Color formatter for console
    console_formatter = colorlog.ColoredFormatter(
        fmt='%(log_color)s%(asctime)s - %(name)s - %(levelname)-8s%(reset)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        }
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(numeric_level)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.addHandler(console_handler)

    # Optional file handler (no colors)
    if log_file:
        file_formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)-8s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(numeric_level)
        root_logger.addHandler(file_handler)

    # Silence noisy third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('pymysql').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module."""
    return logging.getLogger(name)
```

**Test**: `tests/unit/test_logging_config.py`

```python
"""Test logging configuration."""
import pytest
from src.logging_config import setup_logging, get_logger


@pytest.mark.unit
def test_setup_logging_default():
    """Test default logging setup."""
    setup_logging()
    logger = get_logger("test")
    assert logger.level == 0  # Root logger inherits


@pytest.mark.unit
def test_get_logger():
    """Test logger creation."""
    logger = get_logger(__name__)
    assert logger.name == __name__


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
```

**Logging Patterns** (Use throughout all modules):

```python
from src.logging_config import get_logger

logger = get_logger(__name__)

# INFO - Green (Progress)
logger.info("=" * 60)
logger.info("Starting Step 1: Retrieving medicine titles")
logger.info("=" * 60)
logger.info("Found %d articles across %d languages", article_count, lang_count)
logger.info("✓ Language '%s' complete: %d editors found", lang, editor_count)

# DEBUG - Cyan (Details)
logger.debug("Executing query batch %d/%d (%d titles)", batch_num, total, len(batch))
logger.debug("Query: %s", query[:100])

# WARNING - Yellow (Recoverable)
logger.warning("Skipped bot account: %s", username)
logger.warning("Skipped IP address: %s", ip_addr)
logger.warning("Retrying connection (attempt %d/%d)", attempt, max_attempts)

# ERROR - Red (Failures)
logger.error("Failed to connect to %s: %s", dbname, str(e))
logger.error("Query execution failed: %s", str(e), exc_info=True)

# CRITICAL - Red/White (Fatal)
logger.critical("Could not load credentials file: %s", credential_file)
```

---

#### 2. Configuration Module

**File**: `src/config.py`

**Reference**: `.claude/context/conventions.md` - Constants section

```python
"""
Application configuration.

All configuration constants for the Wikipedia Medicine project.
"""
from datetime import datetime
from typing import Dict, Any

# Years (dynamically calculated)
LAST_YEAR: str = str(datetime.now().year - 1)

# Processing
BATCH_SIZE: int = 100
MAX_CONNECTIONS: int = 5
QUERY_TIMEOUT: int = 60
MAX_RETRIES: int = 3

# Database
CREDENTIAL_FILE: str = "~/replica.my.cnf"
DATABASE_PORT: int = 3306
DATABASE_CHARSET: str = "utf8mb4"

# Output directories
OUTPUT_DIRS: Dict[str, str] = {
    "languages": "languages",
    "editors": "editors",
    "reports": "reports"
}

# Logging
LOG_LEVEL: str = "INFO"
LOG_FILE: str = None
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

# Database connection parameters
DATABASE_CONFIG: Dict[str, Any] = {
    "port": DATABASE_PORT,
    "charset": DATABASE_CHARSET,
    "connect_timeout": 30,
    "read_timeout": QUERY_TIMEOUT,
    "autocommit": True,
}
```

**Test**: `tests/unit/test_config.py`

```python
"""Test configuration module."""
import pytest
from src import config


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
```

---

#### 3. Utility Functions

**File**: `src/utils.py`

**Reference**: `.claude/context/conventions.md` - All sections

```python
"""
Utility functions for the Wikipedia Medicine project.

This module provides helper functions used across the application.
"""
import logging
import os
import re
from typing import Any

import pymysql.converters

logger = logging.getLogger(__name__)


def is_ip_address(text: str) -> bool:
    """
    Check if text is an IP address (IPv4 or IPv6).

    Args:
        text: String to check

    Returns:
        True if text matches IP pattern, False otherwise

    Example:
        >>> is_ip_address("192.168.1.1")
        True
        >>> is_ip_address("Username")
        False
    """
    # IPv4 pattern
    ipv4_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'

    # IPv6 pattern (simplified)
    ipv6_pattern = r'^([0-9a-fA-F]{0,4}:){7}[0-9a-fA-F]{0,4}$'

    return bool(re.match(ipv4_pattern, text) or re.match(ipv6_pattern, text))


def escape_title(title: str) -> str:
    """
    Escape article title for SQL queries.

    Args:
        title: Article title to escape

    Returns:
        SQL-escaped title

    Example:
        >>> escape_title("O'Reilly")
        "O\\'Reilly"
    """
    return pymysql.converters.escape_string(title)


def format_number(num: int) -> str:
    """
    Format number with thousands separator.

    Args:
        num: Number to format

    Returns:
        Formatted number string

    Example:
        >>> format_number(12345)
        "12,345"
    """
    return f"{num:,}"

```

**Test**: `tests/unit/test_utils.py`

```python
"""Test utility functions."""
import pytest
from src.utils import is_ip_address, escape_title, format_number


@pytest.mark.unit
@pytest.mark.parametrize("ip,expected", [
    ("192.168.1.1", True),
    ("255.255.255.255", True),
    ("Username123", False),
    ("2001:0db8:85a3:0000:0000:8a2e:0370:7334", True),
    ("NotAnIP", False),
])
def test_is_ip_address(ip, expected):
    """Test IP address detection."""
    assert is_ip_address(ip) == expected


@pytest.mark.unit
def test_escape_title():
    """Test SQL title escaping."""
    assert "\\'" in escape_title("O'Reilly")
    assert escape_title("Normal_Title") == "Normal_Title"


@pytest.mark.unit
def test_format_number():
    """Test number formatting."""
    assert format_number(1234) == "1,234"
    assert format_number(1234567) == "1,234,567"
```

---

#### 4. Database Manager

**File**: `src/database.py`

**Reference**:
- `.claude/context/architecture.md` - Database Manager section
- `.claude/context/database_schema.md` - Connection details
- `.claude/context/conventions.md` - Database code section

```python
"""
Database connection management.

This module provides the Database class for managing connections to
Wikimedia Toolforge databases with connection pooling and retry logic.

See .claude/context/architecture.md for design details.
"""
import logging
import os
import time
from typing import Any, Dict, List, Optional

import pymysql
import pymysql.cursors

from src.config import DATABASE_CONFIG, CREDENTIAL_FILE, MAX_RETRIES

logger = logging.getLogger(__name__)


class Database:
    """
    Context manager for database connections.

    Manages connections to Wikimedia Toolforge databases with:
    - Automatic credential loading from ~/replica.my.cnf
    - Connection retry logic with exponential backoff
    - Proper resource cleanup via context manager

    Attributes:
        host: Database host
        database: Database name
        port: Database port (default: 3306)

    Example:
        >>> with Database("enwiki.analytics.db.svc.wikimedia.cloud", "enwiki_p") as db:
        ...     results = db.execute("SELECT * FROM page LIMIT 10")
    """

    def __init__(self, host: str, database: str, port: int = 3306):
        """
        Initialize database connection parameters.

        Args:
            host: Database host (e.g., "enwiki.analytics.db.svc.wikimedia.cloud")
            database: Database name (e.g., "enwiki_p")
            port: Database port (default: 3306)
        """
        self.host = host
        self.database = database
        self.port = port
        self.connection: Optional[pymysql.connections.Connection] = None

        logger.debug("Database initialized: %s/%s", host, database)

    def __enter__(self) -> 'Database':
        """
        Enter context manager - establish connection.

        Returns:
            self

        Raises:
            pymysql.err.OperationalError: If connection fails after retries
        """
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager - close connection."""
        if self.connection:
            self.connection.close()
            logger.debug("Connection closed: %s/%s", self.host, self.database)
            self.connection = None

    def _load_credentials(self) -> Dict[str, str]:
        """
        Load database credentials from ~/replica.my.cnf.

        Returns:
            Dictionary with 'user' and 'password'

        Raises:
            FileNotFoundError: If credential file doesn't exist
            ValueError: If credentials are malformed
        """
        cred_file = os.path.expanduser(CREDENTIAL_FILE)

        if not os.path.exists(cred_file):
            logger.critical("Credential file not found: %s", cred_file)
            raise FileNotFoundError(f"Credential file not found: {cred_file}")

        credentials = {}
        with open(cred_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('user'):
                    credentials['user'] = line.split('=')[1].strip()
                elif line.startswith('password'):
                    credentials['password'] = line.split('=')[1].strip()

        if 'user' not in credentials or 'password' not in credentials:
            raise ValueError("Invalid credential file format")

        logger.debug("Credentials loaded from %s", cred_file)
        return credentials

    def _connect(self) -> None:
        """
        Establish database connection with retry logic.

        Raises:
            pymysql.err.OperationalError: If connection fails after max retries
        """
        credentials = self._load_credentials()

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.debug("Connecting to %s/%s (attempt %d/%d)",
                           self.host, self.database, attempt, MAX_RETRIES)

                self.connection = pymysql.connect(
                    host=self.host,
                    database=self.database,
                    port=self.port,
                    user=credentials['user'],
                    password=credentials['password'],
                    cursorclass=pymysql.cursors.DictCursor,
                    **DATABASE_CONFIG
                )

                logger.info("✓ Connected to %s/%s", self.host, self.database)
                return

            except pymysql.err.OperationalError as e:
                logger.warning("Connection failed (attempt %d/%d): %s",
                             attempt, MAX_RETRIES, str(e))

                if attempt < MAX_RETRIES:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info("Retrying in %d seconds...", wait_time)
                    time.sleep(wait_time)
                else:
                    logger.error("Failed to connect after %d attempts", MAX_RETRIES)
                    raise

    def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results.

        Args:
            query: SQL query to execute
            params: Optional query parameters

        Returns:
            List of result rows as dictionaries

        Raises:
            pymysql.err.ProgrammingError: If query has syntax errors
            pymysql.err.OperationalError: If query execution fails

        Example:
            >>> results = db.execute("SELECT page_title FROM page LIMIT 10")
        """
        if not self.connection:
            raise RuntimeError("Database connection not established")

        try:
            with self.connection.cursor() as cursor:
                logger.debug("Executing query: %s...", query[:100])
                cursor.execute(query, params)
                results = cursor.fetchall()
                logger.debug("Query returned %d rows", len(results))
                return results

        except pymysql.err.ProgrammingError as e:
            logger.error("Query syntax error: %s\nQuery: %s", str(e), query[:200])
            raise

        except pymysql.err.OperationalError as e:
            logger.error("Query execution error: %s", str(e))
            raise
```

**Test**: `tests/unit/test_database.py`

```python
"""Test database module."""
import pytest
from unittest.mock import Mock, patch, mock_open
from src.services.database import Database


@pytest.mark.unit
def test_database_init():
    """Test database initialization."""
    db = Database("localhost", "test_db", 3306)
    assert db.host == "localhost"
    assert db.database == "test_db"
    assert db.port == 3306


@pytest.mark.unit
@patch('builtins.open', mock_open(read_data='user=testuser\npassword=testpass\n'))
@patch('os.path.exists', return_value=True)
def test_load_credentials(mock_exists):
    """Test credential loading."""
    db = Database("localhost", "test_db")
    creds = db._load_credentials()
    assert creds['user'] == 'testuser'
    assert creds['password'] == 'testpass'


@pytest.mark.unit
@patch('src.services.database.pymysql.connect')
@patch('builtins.open', mock_open(read_data='user=test\npassword=pass\n'))
@patch('os.path.exists', return_value=True)
def test_context_manager(mock_exists, mock_open_file, mock_connect):
    """Test database context manager."""
    mock_conn = Mock()
    mock_connect.return_value = mock_conn

    with Database("localhost", "test_db") as db:
        assert db.connection == mock_conn

    mock_conn.close.assert_called_once()
```

---

#### 5. Query Builder

**File**: `src/queries.py`

**Reference**: `.claude/context/database_schema.md` - All query patterns

```python
"""
SQL query templates and builders.

This module provides SQL query templates for retrieving data from
Wikimedia databases. All queries are optimized for read replicas.

See .claude/context/database_schema.md for schema details.
"""
import logging
from typing import List

from src.utils import escape_title

logger = logging.getLogger(__name__)


class QueryBuilder:
    """
    SQL query builder for Wikimedia databases.

    Provides static methods for building optimized SQL queries.
    All queries use indexed columns and are designed for read replicas.
    """

    @staticmethod
    def get_medicine_titles() -> str:
        """
        Get Medicine project articles with language links.

        Database: enwiki_p

        Returns:
            SQL query string
        """
        return """
            SELECT page_title, ll_lang, ll_title
            FROM page, langlinks, page_assessments, page_assessments_projects
            WHERE pap_project_title = "Medicine"
              AND pa_project_id = pap_project_id
              AND pa_page_id = page_id
              AND page_id = ll_from
              AND page_is_redirect = 0
              AND page_namespace = 0
        """

    @staticmethod
    def get_database_mapping() -> str:
        """
        Get mapping of language codes to database names.

        Database: meta_p

        Returns:
            SQL query string
        """
        return """
            SELECT dbname, family, lang, url
            FROM wiki
            WHERE is_closed = 0
              AND family = 'wikipedia'
        """

    @staticmethod
    def get_editors_standard(titles: List[str], year: str) -> str:
        """
        Get editor statistics for given titles (standard languages).

        Args:
            titles: List of article titles (will be escaped)
            year: Year to filter (e.g., "2024")

        Returns:
            SQL query string with escaped titles

        Note:
            Titles are automatically escaped to prevent SQL injection.
        """
        # Escape all titles
        escaped_titles = [escape_title(title) for title in titles]
        titles_str = "', '".join(escaped_titles)

        logger.debug("Building query for %d titles in year %s", len(titles), year)

        return f"""
            SELECT actor_name, COUNT(*) as count
            FROM revision
            JOIN actor ON rev_actor = actor_id
            JOIN page ON rev_page = page_id
            WHERE page_title IN ('{titles_str}')
              AND page_namespace = 0
              AND rev_timestamp LIKE '{year}%'
              AND LOWER(CAST(actor_name AS CHAR)) NOT LIKE '%bot%'
            GROUP BY actor_id
            ORDER BY count DESC
        """

    @staticmethod
    def get_editors_arabic(year: str) -> str:
        """
        Get editor statistics for Arabic Wikipedia Medicine project.

        Uses project assessment directly (no title filtering needed).

        Args:
            year: Year to filter (e.g., "2024")

        Returns:
            SQL query string
        """
        return f"""
            SELECT actor_name, COUNT(*) as count
            FROM revision
            JOIN actor ON rev_actor = actor_id
            JOIN page ON rev_page = page_id
            WHERE page_id IN (
                SELECT DISTINCT pa_page_id
                FROM page_assessments, page_assessments_projects
                WHERE pa_project_id = pap_project_id
                  AND pap_project_title = "طب"
            )
              AND page_namespace = 0
              AND rev_timestamp LIKE '{year}%'
              AND LOWER(CAST(actor_name AS CHAR)) NOT LIKE '%bot%'
            GROUP BY actor_id
            ORDER BY count DESC
            LIMIT 100
        """

    @staticmethod
    def get_editors_english(year: str) -> str:
        """
        Get editor statistics for English Wikipedia Medicine project.

        Uses WikiProject Medicine templatelinks on talk pages.

        Args:
            year: Year to filter (e.g., "2025")

        Returns:
            SQL query string
        """
        return f"""
            SELECT actor_name, COUNT(*) as count
            FROM revision
            JOIN actor ON rev_actor = actor_id
            JOIN page ON rev_page = page_id
            WHERE page_title IN (
                SELECT page_title
                FROM (
                    SELECT tl_from, rd_from
                    FROM templatelinks
                    LEFT JOIN redirect
                      ON rd_from = tl_from
                      AND rd_title = 'WikiProject_Medicine'
                      AND (rd_interwiki = '' OR rd_interwiki IS NULL)
                      AND rd_namespace = 10
                    JOIN page ON tl_from = page_id
                    JOIN linktarget ON tl_target_id = lt_id
                    WHERE lt_namespace = 10
                      AND lt_title = 'WikiProject_Medicine'
                    ORDER BY tl_from
                ) temp
                JOIN page ON tl_from = page_id
                WHERE page_namespace = 1
            )
              AND page_namespace = 0
              AND rev_timestamp LIKE '{year}%'
              AND LOWER(CAST(actor_name AS CHAR)) NOT LIKE '%bot%'
            GROUP BY actor_id
            ORDER BY count DESC
            LIMIT 100
        """
```

---

### Continue with remaining modules...

The updated plan continues with:

6. **EditorProcessor** (`src/processor.py`)
7. **ReportGenerator** (`src/reports.py`)
8. **Main Application** (`src/main.py`)

Each with:
- ✅ Color logging integration
- ✅ Type hints
- ✅ Google-style docstrings
- ✅ Comprehensive error handling
- ✅ Unit tests
- ✅ References to `.claude/` documentation

---

## Key Updates from Original Plan

### ✅ Added

1. **Logging Configuration Module** - Color logging setup
2. **Pre-commit Hooks** - Automated code quality checks
3. **pyproject.toml** - Modern Python configuration
4. **Contributing Guide** - Clear contribution process
5. **Makefile** - Convenient commands
6. **.claude/ Directory** - Comprehensive AI assistance guidance
7. **Enhanced Error Handling** - With colored logging
8. **Better Type Hints** - Throughout all modules
9. **Comprehensive Tests** - Including logging tests

### ✅ Enhanced

1. **All modules use color logging** - Green INFO, Red ERROR, etc.
2. **Better documentation** - References to `.claude/` context
3. **Clearer code examples** - Following conventions.md
4. **Testing strategy** - pytest markers and coverage
5. **Development workflow** - With pre-commit and CI/CD

---

## Quick Start Commands

```bash
# 1. Setup
git clone <repo>
cd wikipedia-medicine
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install

# 2. Develop
# Follow .claude/CLAUDE.md for best practices
# Use .claude/prompts/templates.md for asking Claude questions

# 3. Test
pytest                          # Run all tests
pytest --cov=src               # With coverage
make test                      # Using Makefile

# 4. Run
python -m src.main                           # Default (INFO level)
python -m src.main --log-level DEBUG         # Debug mode
python -m src.main --log-file output.log     # With file logging

# 5. Check Code Quality
black src tests                # Format
flake8 src tests              # Lint
mypy src                      # Type check
make lint                     # All checks
```

---

## Next Steps

1. ✅ Review `.claude/` documentation
2. ✅ Implement `logging_config.py` first
3. ✅ Follow implementation order in this plan
4. ✅ Use `.claude/prompts/templates.md` when asking Claude for help
5. ✅ Reference `.claude/context/` docs for technical details
6. ✅ Write tests alongside implementation
7. ✅ Use color logging throughout all modules

---

*This plan integrates all best practices, configurations, and guidance created for the project.*

**Version**: 2.0
**Date**: 2025-01-28
**Status**: Ready for implementation
