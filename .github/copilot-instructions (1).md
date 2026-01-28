# GitHub Copilot Instructions

This file provides context and guidelines for GitHub Copilot when assisting with the Wikipedia Medicine Editor Analysis project.

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
    mocker.patch('src.processor.Database', return_value=mock_db)
    
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
CURRENT_YEAR: str = str(datetime.now().year)
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

# Use LIKE for year filtering instead of YEAR() for performance
# The index on rev_timestamp supports LIKE but not YEAR()
query = f"WHERE rev_timestamp LIKE '{year}%'"
```

### SQL Query Comments
```python
query = """
    SELECT actor_name, COUNT(*) as count
    FROM revision
    JOIN actor ON rev_actor = actor_id  -- Link revisions to editors
    JOIN page ON rev_page = page_id      -- Link revisions to pages
    WHERE page_title IN (%(titles)s)
      AND page_namespace = 0              -- Main article namespace only
      AND rev_timestamp LIKE '2024%%'     -- Filter by year (uses index)
      AND LOWER(CAST(actor_name AS CHAR)) NOT LIKE '%%bot%%'  -- Exclude bots
    GROUP BY actor_id
    ORDER BY count DESC
"""
```

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

## Common Commands

```bash
# Development
python -m src.main --log-level DEBUG
python -m src.main --year 2023

# Testing
pytest tests/unit -v
pytest tests/integration -v -m "not slow"
pytest --cov=src --cov-report=html

# Code Quality
black src tests
isort src tests
flake8 src tests
mypy src
```

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

---

*Follow these patterns for consistent, high-quality code that aligns with project standards.*
