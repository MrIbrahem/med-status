# GitHub Copilot Instructions

This file provides context and guidelines for GitHub Copilot when assisting with the Wikipedia Medicine Editor Analysis project.

## Quick Start Guide

**Before making any changes, read this section first:**

1. **Project Purpose**: Analyze Wikipedia Medicine project editor contributions across multiple languages by querying Wikimedia Toolforge databases
2. **Tech Stack**: Python 3.9+ (CI uses 3.11), PyMySQL, colorlog, pytest
3. **Critical Commands**:
   - Format code: `make format` (ALWAYS run before committing)
   - Run tests: `pytest tests/unit -v -m "unit and not db"`
   - Lint code: `make lint`
   - Run application: `python -m src.main`

4. **CI Requirements** (must pass for PR approval):
   - ✅ Black code formatting check
   - ✅ isort import ordering check
   - ✅ Unit tests (excluding DB tests)
   - ⚠️ Type checking with mypy (advisory)
   - ⚠️ Integration tests (advisory)

5. **Common Pitfalls to Avoid**:
   - ❌ Don't use bare `except:` clauses (use specific exceptions)
   - ❌ Don't manually manage database connections (use context managers)
   - ❌ Don't build SQL with f-strings (use escaping or parameterization)
   - ❌ Don't forget to run `make format` before committing
   - ❌ Don't use hardcoded years (use dynamic calculation from datetime)

6. **Repository Layout**:
   - `src/`: Source code
     - `main.py`: Application entry point
     - `database.py`: Database connection management
     - `queries.py`: SQL query templates
     - `processor.py`: Data processing logic
     - `reports.py`: WikiText report generation
     - `config.py`: Configuration constants
     - `utils.py`: Helper functions
     - `logging_config.py`: Logging setup
   - `tests/`: Test suite (unit/ and integration/)
   - `.github/`: CI/CD workflows and this instructions file
   - `.claude/`: Claude AI assistant context (separate from Copilot)

## Project Context

**Purpose**: Analyze editor contributions across Wikipedia's Medicine projects in multiple languages by querying Wikimedia Toolforge databases.

**Tech Stack**: Python 3.9+, PyMySQL, colorlog, pytest

**Key Features**:
- Multi-language Wikipedia data analysis
- Batch processing of database queries
- Color-coded console logging
- WikiText report generation
- Comprehensive error handling

## Code Style & Standards

### Formatting
- **Line Length**: 120 characters
- **Formatter**: Black
- **Import Sorter**: isort
- **Linter**: flake8, pylint
- **Type Checker**: mypy

### Python Conventions
```python
# Functions and variables: snake_case
def process_language(lang: str) -> Dict[str, int]:
    editor_count = 0

# Classes: PascalCase
class EditorProcessor:
    pass

# Constants: UPPER_SNAKE_CASE
BATCH_SIZE = 100
MAX_CONNECTIONS = 5

# Private methods: _prefixed
def _internal_helper(self):
    pass
```

### Type Hints
Always include type hints for function signatures:

```python
from typing import Dict, List, Optional

def process_titles(
    titles: List[str],
    year: str,
    batch_size: int = 100
) -> Dict[str, int]:
    """Process article titles and return editor statistics."""
    pass
```

### Docstrings
Use Google-style docstrings for all public functions and classes:

```python
def get_editors(titles: List[str], year: str) -> Dict[str, int]:
    """
    Retrieve editor statistics for the given titles.

    This function queries the database for all editors who made revisions
    to the specified articles during the given year.

    Args:
        titles: List of article titles (URL-encoded with underscores)
        year: Year to filter revisions (e.g., "2024")

    Returns:
        Dictionary mapping editor usernames to their edit counts.
        Example: {"Editor1": 150, "Editor2": 75}

    Raises:
        pymysql.err.OperationalError: If database connection fails
        ValueError: If titles list is empty

    Example:
        >>> editors = get_editors(["Barack_Obama"], "2024")
        >>> print(editors["JohnDoe"])
        42
    """
    pass
```

## Logging Patterns

### Setup
Always use the centralized logging configuration:

```python
from src.logging_config import get_logger

logger = get_logger(__name__)
```

### Log Levels with Colors

```python
# DEBUG - Cyan - Detailed diagnostic information
logger.debug("Processing batch %d/%d with %d titles", batch_num, total_batches, len(batch))

# INFO - Green - Normal progress updates
logger.info("=" * 60)
logger.info("Step 1: Retrieving medicine titles")
logger.info("=" * 60)
logger.info("✓ Found %d articles across %d languages", article_count, lang_count)
logger.info("Processing language: %s (%d articles)", lang, len(titles))

# WARNING - Yellow - Recoverable issues
logger.warning("Skipped bot account: %s", username)
logger.warning("Skipped IP address: %s", ip_address)
logger.warning("Retrying connection (attempt %d/%d)", attempt, max_attempts)

# ERROR - Red - Failures requiring attention
logger.error("Failed to connect to %s: %s", dbname, str(e))
logger.error("Query execution failed: %s", str(e), exc_info=True)

# CRITICAL - Red/White - Fatal errors
logger.critical("Could not load credentials file: %s", credential_file)
logger.critical("Fatal error: Cannot continue execution")
```

### String Formatting
Use lazy evaluation (not f-strings) for performance:

```python
# ✓ Good - Lazy evaluation
logger.debug("Processing %s with %d items", name, len(items))

# ✗ Bad - Always evaluated even if DEBUG disabled
logger.debug(f"Processing {name} with {len(items)} items")
```

## Database Patterns

### Always Use Context Managers
Never manually manage database connections:

```python
# ✓ Good - Automatic cleanup
with Database(host, database) as db:
    results = db.execute(query)
# Connection automatically closed

# ✗ Bad - Manual management
db = Database(host, database)
db._connect()
results = db.execute(query)
db.connection.close()  # Easy to forget!
```

### SQL Injection Prevention
Always escape user input:

```python
from src.utils import escape_title

# ✓ Good - Escaped input
escaped_titles = [escape_title(t) for t in titles]
titles_str = "', '".join(escaped_titles)
query = f"WHERE page_title IN ('{titles_str}')"

# ✗ Bad - Direct string interpolation
titles_str = "', '".join(titles)  # Not escaped!
query = f"WHERE page_title IN ('{titles_str}')"
```

### Batch Processing
Always batch large queries:

```python
# ✓ Good - Batched
BATCH_SIZE = 100
for i in range(0, len(titles), BATCH_SIZE):
    batch = titles[i:i + BATCH_SIZE]
    query = QueryBuilder.get_editors_standard(batch, year)
    results = db.execute(query)
    # Process batch...

# ✗ Bad - All at once (can timeout)
query = QueryBuilder.get_editors_standard(titles, year)  # 10,000 titles!
results = db.execute(query)
```

## Error Handling

### Use Specific Exceptions
Never use bare except clauses:

```python
# ✓ Good - Specific exceptions
try:
    results = db.execute(query)
except pymysql.err.OperationalError as e:
    logger.error("Database connection failed: %s", e)
    raise
except pymysql.err.ProgrammingError as e:
    logger.error("Query syntax error: %s", e)
    return []

# ✗ Bad - Bare except
try:
    results = db.execute(query)
except:  # Catches everything, even KeyboardInterrupt!
    logger.error("Something failed")
```

### Always Log Errors with Context
```python
try:
    result = risky_operation()
except ValueError as e:
    logger.error(
        "Failed to process language '%s': %s",
        lang,
        str(e),
        exc_info=True  # Includes stack trace
    )
    raise
```

### Retry Logic with Exponential Backoff
```python
import time

for attempt in range(1, MAX_RETRIES + 1):
    try:
        connection = pymysql.connect(...)
        logger.info("✓ Connected successfully")
        break
    except pymysql.err.OperationalError as e:
        logger.warning("Connection failed (attempt %d/%d): %s", attempt, MAX_RETRIES, e)
        if attempt < MAX_RETRIES:
            wait_time = 2 ** attempt  # Exponential backoff: 2, 4, 8 seconds
            logger.info("Retrying in %d seconds...", wait_time)
            time.sleep(wait_time)
        else:
            logger.error("Failed to connect after %d attempts", MAX_RETRIES)
            raise
```

## Testing Patterns

### Use pytest Markers
```python
import pytest

@pytest.mark.unit
def test_is_ip_address():
    """Test IP address detection."""
    assert is_ip_address("192.168.1.1") is True
    assert is_ip_address("Username") is False

@pytest.mark.integration
@pytest.mark.slow
def test_full_workflow():
    """Test complete data pipeline."""
    pass

@pytest.mark.db
def test_database_query():
    """Test actual database query."""
    pass
```

### Parametrized Tests
```python
@pytest.mark.unit
@pytest.mark.parametrize("ip,expected", [
    ("192.168.1.1", True),
    ("255.255.255.255", True),
    ("Username123", False),
    ("2001:0db8:85a3::8a2e:0370:7334", True),
])
def test_is_ip_address(ip, expected):
    """Test IP detection with various inputs."""
    assert is_ip_address(ip) == expected
```

### Mock External Dependencies
```python
from unittest.mock import Mock, patch

@pytest.mark.unit
def test_process_language(mocker):
    """Test language processing with mocked database."""
    # Mock database connection
    mock_db = mocker.Mock()
    mock_db.execute.return_value = [
        {"actor_name": "User1", "count": 10},
        {"actor_name": "User2", "count": 5}
    ]

    # Mock Database class
    mocker.patch('src.services.processor.Database', return_value=mock_db)

    processor = EditorProcessor()
    result = processor.process_language("es", ["Title1"], "eswiki", "2024")

    assert result == {"User1": 10, "User2": 5}
```

## Special Cases

### Arabic Wikipedia
Uses project assessment directly (no title filtering):

```python
if lang == "ar":
    query = QueryBuilder.get_editors_arabic(year)
    # No titles needed for Arabic
```

### English Wikipedia
Uses WikiProject Medicine templatelinks:

```python
if lang == "en":
    query = QueryBuilder.get_editors_english(year)
    # Uses templatelinks instead of langlinks
```

### Bot Filtering
Case-insensitive check for "bot" in username:

```python
def is_bot(username: str) -> bool:
    """Check if username is a bot account."""
    return "bot" in username.lower()
```

### IP Address Filtering
Detect both IPv4 and IPv6:

```python
import re

def is_ip_address(text: str) -> bool:
    """Check if text is an IP address."""
    ipv4_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    ipv6_pattern = r'^([0-9a-fA-F]{0,4}:){7}[0-9a-fA-F]{0,4}$'
    return bool(re.match(ipv4_pattern, text) or re.match(ipv6_pattern, text))
```

## File Structure Patterns

### Module Organization
```python
"""
Module docstring explaining purpose.
"""

# Standard library imports
import logging
import os
from typing import Dict, List

# Third-party imports
import pymysql

# Local imports
from src.config import BATCH_SIZE
from src.utils import escape_title

# Module logger
logger = logging.getLogger(__name__)

# Constants
MAX_RETRIES = 3

# Private functions
def _helper_function():
    pass

# Public functions
def public_function():
    pass

# Classes
class MyClass:
    pass
```

### Class Structure
```python
class MyClass:
    """Class docstring."""

    # Class variables
    class_var = "value"

    def __init__(self, param: str):
        """Initialize instance."""
        self.param = param
        self._private_var = None

    # Public methods
    def public_method(self) -> str:
        """Public method docstring."""
        return self._private_method()

    # Private methods
    def _private_method(self) -> str:
        """Private method docstring."""
        return "result"

    # Special methods
    def __str__(self) -> str:
        """String representation."""
        return f"MyClass({self.param})"
```

## Common Patterns

### Progress Logging
```python
def log_progress(current: int, total: int, item_name: str = "items"):
    """Log progress with visual indicator."""
    percentage = (current / total) * 100
    bar_length = 40
    filled = int(bar_length * current / total)
    bar = '█' * filled + '░' * (bar_length - filled)

    logger.info(
        "Progress: [%s] %.1f%% (%d/%d %s)",
        bar, percentage, current, total, item_name
    )
```

### Statistics Formatting
```python
def log_statistics(stats: Dict[str, Any]):
    """Log statistics in formatted table."""
    logger.info("=" * 60)
    logger.info("STATISTICS SUMMARY")
    logger.info("-" * 60)
    for key, value in stats.items():
        if isinstance(value, float):
            logger.info("  %-30s: %10.2f", key, value)
        elif isinstance(value, int):
            logger.info("  %-30s: %,10d", key, value)
        else:
            logger.info("  %-30s: %10s", key, value)
    logger.info("=" * 60)
```

### File Operations with UTF-8
```python
import json

# Writing JSON
with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Reading JSON
with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Writing text
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
```

## Configuration

### Dynamic Year Calculation
```python
from datetime import datetime

# Always use dynamic calculation
LAST_YEAR: str = str(datetime.now().year - 1)

# ✗ Never hardcode years
# LAST_YEAR = "2024"  # Will become outdated!
```

### Database Configuration
```python
DATABASE_CONFIG = {
    "port": 3306,
    "charset": "utf8mb4",
    "connect_timeout": 30,
    "read_timeout": 60,
    "autocommit": True,
}
```

## Security Best Practices

### Never Log Sensitive Data
```python
# ✓ Good
logger.info("Authentication successful")

# ✗ Bad
logger.info("Password: %s", password)  # Never!
```

### Validate Input
```python
def process_titles(titles: List[str]) -> Dict[str, int]:
    """Process titles with validation."""
    if not titles:
        raise ValueError("Titles list cannot be empty")

    if len(titles) > 10000:
        raise ValueError("Too many titles (max: 10000)")

    for title in titles:
        if not isinstance(title, str):
            raise TypeError(f"Expected str, got {type(title)}")

    # Process...
```

### Credential Management
```python
# ✓ Good - Load from file
credentials = load_credentials_from_file("~/replica.my.cnf")

# ✗ Bad - Hardcoded
user = "my_username"  # Never!
password = "my_password"  # Never!
```

## Performance Tips

### Use Generators for Large Datasets
```python
# ✓ Good - Generator (memory efficient)
def process_results(cursor):
    for row in cursor:
        yield process_row(row)

# ✗ Bad - Load all into memory
results = cursor.fetchall()  # Can be huge!
for row in results:
    process_row(row)
```

### Cache Expensive Operations
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_database_mapping() -> Dict[str, str]:
    """Get database mapping (cached)."""
    # Expensive operation
    return mapping
```

## Documentation

### Inline Comments for Complex Logic
```python
# Calculate edit velocity: edits per day over past 30 days
# This helps identify highly active editors
velocity = total_edits / days_active

## Workflow Reference

The application follows these steps:

1. **Retrieve Medicine Titles** (enwiki_p)
   - Query Medicine project articles with language links
   - Output: `languages/{lang}.json`

2. **Get Database Mapping** (meta_p)
   - Map language codes to database names
   - Output: Dictionary in memory

3. **Process Each Language** ({lang}wiki_p)
   - Query editor statistics (batched)
   - Special handling for Arabic and English
   - Filter bots and IPs
   - Output: `editors/{lang}.json`

4. **Generate Language Reports**
   - Create WikiText tables per language
   - Output: `reports/{lang}.wiki`

5. **Generate Global Report**
   - Combine all editor data
   - Sort globally by edit count
   - Output: `reports/total_report.wiki`

## Build, Test, and Validation Commands

### Environment Setup

**Prerequisites:**
- Python 3.9+ (project uses Python 3.11 in CI)
- Access to Wikimedia Toolforge (for production use)
- `~/replica.my.cnf` credential file (for production database access)

**Initial Setup Sequence:**
```bash
# Alternative: Manual installation
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install
```

### Code Quality Checks (Run BEFORE committing)

**1. Format Code (Auto-fix issues):**
```bash
make format
# This runs: black src tests && isort src tests
# Takes ~2-5 seconds
```

**2. Lint Code (Check for issues):**
```bash
make lint
# This runs: flake8 src tests && pylint src && mypy src --ignore-missing-imports
# Expected: Some pylint warnings are acceptable (see pyproject.toml for disabled checks)
# Takes ~10-15 seconds
```

**Individual linting commands:**
```bash
# Check syntax errors and critical issues only
flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics

# Full flake8 check (warnings allowed)
flake8 src tests

# Check code formatting (does not modify files)
black --check src tests

# Check import sorting (does not modify files)
isort --check-only src tests

# Type checking (some errors expected due to dynamic typing)
mypy src --ignore-missing-imports
```

### Testing Sequence

**1. Run Unit Tests (Fast, no external dependencies):**
```bash
# Recommended: Run unit tests only (excluding DB tests)
pytest tests/unit -v -m "unit and not db"
# Expected: All tests should pass
# Takes ~5-10 seconds

# Alternative: Run all unit tests
make test
# This runs: pytest tests/ -v
```

**2. Run Integration Tests (May require mocks):**
```bash
# Integration tests with mocked database
pytest tests/integration -v -m "not network"
# Expected: Most should pass; some may be marked as xfail
# Takes ~10-20 seconds
```

**3. Run Tests with Coverage:**
```bash
make coverage
# This runs: pytest tests/ --cov=src --cov-report=html --cov-report=term
# Expected: >80% coverage for new code
# Generates: htmlcov/index.html (open in browser to view detailed report)
# Takes ~15-30 seconds
```

**4. Run Specific Test Files:**
```bash
# Test a specific module
pytest tests/unit/test_utils.py -v

# Test a specific function
pytest tests/unit/test_utils.py::test_is_ip_address -v

# Run tests matching a pattern
pytest -k "test_database" -v
```

### Running the Application

**Development Mode (with debug logging):**
```bash
make run
# This runs: python -m src.main
# Default behavior: Processes all languages for current year

# With debug logging
python -m src.main --log-level DEBUG

# With custom year
python -m src.main --year 2024

# Process specific languages only
python -m src.main --languages es,fr,de

# Skip title retrieval (use cached data)
python -m src.main --skip-titles

# Generate reports only (no data processing)
python -m src.main --reports-only
```

**Note:** Running the full application requires database credentials in `~/replica.my.cnf`. For testing without database access, use unit tests or integration tests with mocked connections.

### Cleaning Build Artifacts

```bash
make clean
# Removes: __pycache__, *.pyc, .pytest_cache, .mypy_cache, htmlcov/, .coverage, dist/, build/
# Takes ~1-2 seconds
```

### Common Development Workflows

**Workflow 1: Making a Code Change**
```bash
# 1. Format and lint
make format
make lint

# 2. Run unit tests
pytest tests/unit -v -m "unit and not db"

# 3. If tests pass, commit
git add .
git commit -m "Your commit message"

# 4. Push (triggers CI)
git push
```

**Workflow 2: Adding a New Feature**
```bash
# 1. Write tests first (TDD approach)
# Create test_new_feature.py in tests/unit/

# 2. Run new tests (should fail)
pytest tests/unit/test_new_feature.py -v

# 3. Implement feature
# Edit src/your_module.py

# 4. Run tests again (should pass)
pytest tests/unit/test_new_feature.py -v

# 5. Check coverage
pytest tests/unit/test_new_feature.py -v --cov=src.your_module --cov-report=term-missing

# 6. Format, lint, and commit
make format
make lint
git add .
git commit -m "Add new feature: [description]"
```

**Workflow 3: Debugging Test Failures**
```bash
# Run tests with verbose output and stop on first failure
pytest tests/unit -v -x

# Run tests with print statements visible
pytest tests/unit -v -s

# Run tests with detailed traceback
pytest tests/unit -v --tb=long

# Run tests with Python debugger
pytest tests/unit -v --pdb
```

## CI/CD Pipeline

### GitHub Actions Workflows

The repository has two main CI workflows that run automatically:

**1. Tests Workflow (`.github/workflows/pytest.yml`)**
- **Triggers**: Pull requests, manual dispatch
- **Python Version**: 3.11
- **Steps**:
  1. Syntax check with flake8 (E9, F63, F7, F82 errors are blockers)
  2. Code formatting check with black (must pass)
  3. Type checking with mypy (continue-on-error)
  4. Unit tests with pytest (must pass)
  5. Integration tests (continue-on-error)
  6. Security scan with Bandit (continue-on-error)
  7. Coverage upload to Codecov
- **Must Pass**: Syntax check, formatting check, unit tests
- **Advisory**: Type checking, integration tests, security scan

**2. Linting Workflow (`.github/workflows/lint.yml`)**
- **Triggers**: Push to main/develop branches, pull requests
- **Python Version**: 3.11
- **Steps**:
  1. flake8 (continue-on-error)
  2. black --check (must pass)
  3. isort --check (must pass)
  4. pylint (continue-on-error)
- **Must Pass**: black, isort
- **Advisory**: flake8, pylint

### Pre-commit Hooks

The repository uses pre-commit hooks to catch issues before committing:

```bash
# Install hooks (done automatically by make install-dev)
pre-commit install

# Run all hooks manually
pre-commit run --all-files

# Skip hooks for a specific commit (use sparingly)
git commit --no-verify -m "Your message"
```

**Configured hooks** (see `.pre-commit-config.yaml`):
- Trailing whitespace removal
- End-of-file fixer
- YAML syntax check
- Large file prevention
- black code formatting
- isort import sorting
- flake8 linting

### Common CI Failures and Fixes

**Failure: "Black formatting check failed"**
```bash
# Fix: Run black formatter
make format
git add .
git commit --amend --no-edit
git push --force-with-lease
```

**Failure: "Import order check failed"**
```bash
# Fix: Run isort
make format  # includes isort
git add .
git commit --amend --no-edit
git push --force-with-lease
```

**Failure: "Flake8 syntax errors (E9, F63, F7, F82)"**
```bash
# Check errors
flake8 src --select=E9,F63,F7,F82 --show-source

# Fix syntax errors manually, then:
git add .
git commit --amend --no-edit
git push --force-with-lease
```

**Failure: "Unit tests failed"**
```bash
# Run tests locally to debug
pytest tests/unit -v -x  # Stop on first failure

# Fix issues, then:
pytest tests/unit -v  # Verify all pass
git add .
git commit --amend --no-edit
git push --force-with-lease
```

## Troubleshooting Common Issues

**Issue: "Command not found: make"**
```bash
# Solution: Run commands directly
pip install -r requirements.txt
pip install -r requirements-dev.txt
black src tests
pytest tests/unit -v
```

**Issue: "Permission denied" when running scripts**
```bash
# Solution: Use Python module syntax
python -m src.main
# Instead of: ./src/main.py
```

### Testing Issues

**Issue: Tests pass locally but fail in CI**
- **Cause**: Python version mismatch (CI uses 3.11)
- **Solution**: Test with Python 3.11 locally or check Python version:
  ```bash
  python --version  # Should be 3.11.x for CI compatibility
  ```

**Issue: "Database connection failed" in integration tests**
- **Cause**: Integration tests expect mocked database
- **Solution**: Ensure pytest-mock is installed:
  ```bash
  pip install pytest-mock
  pytest tests/integration -v
  ```

**Issue: Coverage report not generated**
- **Cause**: Missing pytest-cov plugin
- **Solution**:
  ```bash
  pip install pytest-cov
  make coverage
  ```

### Code Quality Issues

**Issue: Black and manual formatting conflict**
- **Solution**: Always run `make format` AFTER making changes, never before
- Black is the source of truth for formatting

**Issue: "Line too long" from flake8 but black doesn't fix it**
- **Cause**: String literals or comments exceeding 120 characters
- **Solution**: Manually break long strings:
  ```python
  # Bad
  long_string = "This is a very long string that exceeds 120 characters and should be broken up"

  # Good
  long_string = (
      "This is a very long string that exceeds 120 characters "
      "and should be broken up"
  )
  ```

**Issue: Mypy errors on valid code**
- **Cause**: Dynamic typing or third-party library without type stubs
- **Solution**: Add type: ignore comment or update pyproject.toml:
  ```python
  result = dynamic_function()  # type: ignore
  ```

### Performance Issues

**Issue: Tests running slowly**
- **Solution**: Run only changed tests or use markers:
  ```bash
  pytest tests/unit/test_specific.py -v
  pytest -m "unit and not slow" -v
  ```

**Issue: Application uses too much memory**
- **Cause**: Fetching large result sets into memory
- **Solution**: Use cursor iteration (see Performance Tips section)

### Git and CI Issues

**Issue: Pre-commit hooks slow down commits**
- **Temporary fix**: Skip hooks for rapid iteration:
  ```bash
  git commit --no-verify -m "WIP: testing"
  ```
- **Before pushing**: Run hooks and fix issues:
  ```bash
  pre-commit run --all-files
  git add .
  git commit --amend --no-edit
  ```

**Issue: CI workflow not triggering**
- **Check**: Workflow file syntax with yamllint
- **Check**: Repository Actions settings are enabled
- **Check**: Branch protection rules

## Reference Documentation

For detailed information, see:
- **Architecture**: `.claude/context/architecture.md`
- **Database Schema**: `.claude/context/database_schema.md`
- **Conventions**: `.claude/context/conventions.md`
- **Color Logging**: `.claude/context/color_logging_guide.md`
- **Full Plan**: `plans/wikipedia_medicine_project_plan_v2.md`

## Quick Checklist

When writing code, ensure:
- [ ] Type hints on function signatures
- [ ] Google-style docstrings
- [ ] Proper logging with appropriate levels
- [ ] Specific exception handling
- [ ] Context managers for resources
- [ ] SQL injection prevention
- [ ] No hardcoded credentials
- [ ] UTF-8 encoding for files
- [ ] Unit tests with markers
- [ ] Line length ≤ 120 characters

## Agent Workflow Best Practices

When Copilot coding agent is working on this repository:

1. **Before Starting**:
   - Read this entire instructions file
   - Understand the project structure and workflow
   - Check existing tests to understand patterns

2. **During Development**:
   - Make minimal, focused changes
   - Follow existing code patterns and conventions
   - Write tests for new functionality
   - Run `make format` after code changes
   - Run unit tests to verify changes

3. **Before Submitting**:
   - Run full linting: `make lint`
   - Run full test suite: `pytest tests/unit -v -m "unit and not db"`
   - Check coverage for new code: `pytest --cov=src --cov-report=term-missing`
   - Verify no debug statements or print() calls left in code
   - Update documentation if behavior changed

4. **Understanding Errors**:
   - Read full error messages and stack traces
   - Check similar code in the repository for patterns
   - Review test files for examples of correct usage
   - Consult the reference documentation in `.claude/context/`

5. **When Stuck**:
   - Review existing implementations for similar functionality
   - Check test files for usage examples
   - Read the database schema documentation
   - Look at the workflow reference section

## Important Notes for Coding Agents

### Database Connections
- **NEVER** query production databases without proper credentials
- **ALWAYS** use context managers to ensure connections are closed
- **TEST** with mocked connections first
- **BATCH** large queries (100 items per batch)

### Testing Strategy
- Write unit tests with mocked dependencies FIRST
- Integration tests should use pytest-mock for database calls
- Tests marked with `@pytest.mark.db` require actual database access
- Keep tests fast (< 1 second per test for unit tests)

### Security Considerations
- All SQL inputs MUST be escaped using `pymysql.converters.escape_string()`
- Never log sensitive data (credentials, passwords, tokens)
- Validate all user inputs before processing
- Use Bandit security scanner findings as guidance (run in CI)

### Performance Optimization
- Use generators for large result sets
- Implement batch processing for bulk operations
- Cache expensive operations with `@lru_cache`
- Monitor memory usage with large datasets

### Code Review Checklist for Agents
Before marking work as complete, verify:
- [ ] All CI checks pass (black, isort, unit tests)
- [ ] No new flake8 or pylint warnings introduced
- [ ] Test coverage maintained or improved
- [ ] Documentation updated (docstrings, README if needed)
- [ ] No hardcoded values (use config.py constants)
- [ ] Error handling follows project patterns
- [ ] Logging uses correct levels and formats
- [ ] Database operations use context managers
- [ ] No SQL injection vulnerabilities

---

*Follow these patterns for consistent, high-quality code that aligns with project standards.*

*Last updated: 2026-01-28*
