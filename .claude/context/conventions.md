# Code Conventions

## Overview

This document defines the coding standards and conventions for the Wikipedia Medicine project. All code must follow these guidelines for consistency, maintainability, and quality.

---

## Python Style Guide

### PEP 8 Compliance

Follow [PEP 8](https://pep8.org/) with the following adjustments:

- **Line Length**: 120 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Blank Lines**: 2 between top-level definitions, 1 between methods

### Automated Formatting

Use **Black** for automatic code formatting:

```bash
black src tests --line-length 120
```

**Black Configuration** (in `pyproject.toml`):
```toml
[tool.black]
line-length = 120
target-version = ['py39', 'py310', 'py311']
```

---

## Import Organization

### Order

1. Standard library imports
2. Third-party library imports
3. Local application imports

### Use isort

```bash
isort src tests
```

**isort Configuration** (in `pyproject.toml`):
```toml
[tool.isort]
profile = "black"
line_length = 120
```

### Example

```python
# Standard library
import logging
import os
from typing import Dict, List, Optional

# Third-party
import pymysql
from dotenv import load_dotenv

# Local
from src.config import BATCH_SIZE, MAX_CONNECTIONS
from src.utils import is_ip_address, escape_title
```

---

## Naming Conventions

### Functions and Variables

Use `snake_case`:

```python
def get_editor_statistics(lang: str, year: str) -> Dict[str, int]:
    editor_count = 0
    total_edits = 0
```

### Classes

Use `PascalCase`:

```python
class DatabaseManager:
    pass

class EditorProcessor:
    pass
```

### Constants

Use `UPPER_SNAKE_CASE`:

```python
BATCH_SIZE = 100
MAX_CONNECTIONS = 5
DEFAULT_YEAR = "2024"
```

### Private Methods/Variables

Prefix with single underscore:

```python
class Database:
    def _connect(self):
        """Private method for internal use."""
        pass
    
    def _load_credentials(self):
        """Private method for internal use."""
        pass
```

### "Internal" (Name Mangling)

Prefix with double underscore only when truly needed:

```python
class Database:
    def __init__(self):
        self.__password = None  # Name mangled to prevent accidental access
```

---

## Type Hints

### Always Use for Public Functions

```python
def process_language(
    lang: str, 
    titles: List[str], 
    year: str
) -> Dict[str, int]:
    """Process a language and return editor statistics."""
    pass
```

### Use for Complex Types

```python
from typing import Dict, List, Optional, Tuple, Any

def get_database_mapping() -> Dict[str, str]:
    """Return mapping of language to database name."""
    pass

def execute_query(query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Execute a query and return results."""
    pass
```

### Modern Type Hints (Python 3.9+)

Prefer built-in types over typing module when possible:

```python
# Preferred (Python 3.9+)
def process_titles(titles: list[str]) -> dict[str, int]:
    pass

# Also acceptable
from typing import List, Dict
def process_titles(titles: List[str]) -> Dict[str, int]:
    pass
```

---

## Docstrings

### Use Google Style

```python
def get_editors(titles: List[str], year: str, batch_size: int = 100) -> Dict[str, int]:
    """
    Retrieve editor statistics for the given titles.
    
    This function queries the database for all editors who made revisions
    to the specified articles during the given year. Results are batched
    to prevent query timeouts.
    
    Args:
        titles: List of article titles to query (URL-encoded with underscores)
        year: Year to filter revisions (e.g., "2024")
        batch_size: Number of titles to process per query (default: 100)
    
    Returns:
        Dictionary mapping editor usernames to their edit counts.
        Example: {"Editor1": 150, "Editor2": 75}
    
    Raises:
        pymysql.err.OperationalError: If database connection fails
        ValueError: If titles list is empty
    
    Note:
        - Bot accounts are automatically filtered out
        - IP addresses are excluded from results
        - Titles must be URL-encoded (spaces as underscores)
    
    Example:
        >>> editors = get_editors(["Barack_Obama", "Python_(programming)"], "2024")
        >>> print(editors["JohnDoe"])
        42
    """
    pass
```

### Module-Level Docstrings

```python
"""
Database connection management module.

This module provides the Database class for managing connections to
Wikimedia Toolforge databases. It implements connection pooling,
automatic retry logic, and proper resource cleanup.

Classes:
    Database: Context manager for database connections

Example:
    >>> with Database("enwiki.analytics.db.svc.wikimedia.cloud", "enwiki_p") as db:
    ...     results = db.execute("SELECT * FROM page LIMIT 10")
"""
```

### Class Docstrings

```python
class EditorProcessor:
    """
    Process and aggregate editor statistics.
    
    This class handles the processing of editor data from database queries,
    including filtering of bot accounts and IP addresses, aggregation of
    edit counts, and batch processing of large title lists.
    
    Attributes:
        batch_size: Number of titles to process per database query
        logger: Logger instance for this class
    
    Example:
        >>> processor = EditorProcessor(batch_size=100)
        >>> editors = processor.process_language("es", titles, "eswiki", "2024")
    """
    
    def __init__(self, batch_size: int = 100):
        """
        Initialize the EditorProcessor.
        
        Args:
            batch_size: Number of titles per batch (default: 100)
        """
        pass
```

---

## Error Handling

### Use Specific Exceptions

❌ **Wrong**:
```python
try:
    result = database.execute(query)
except:
    print("Error occurred")
```

✅ **Correct**:
```python
try:
    result = database.execute(query)
except pymysql.err.OperationalError as e:
    logger.error("Database connection failed: %s", e)
    raise
except pymysql.err.ProgrammingError as e:
    logger.error("Query syntax error: %s\nQuery: %s", e, query)
    return []
```

### Always Log Errors

```python
try:
    result = risky_operation()
except ValueError as e:
    logger.error("Invalid value: %s", e, exc_info=True)
    raise
```

### Provide Context

```python
try:
    with open(filename, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    logger.error("File not found: %s", filename)
    raise
except json.JSONDecodeError as e:
    logger.error("Invalid JSON in %s: %s", filename, e)
    raise
```

---

## Logging

### Logger Creation

```python
import logging

logger = logging.getLogger(__name__)
```

### Log Levels

```python
# DEBUG: Detailed diagnostic information
logger.debug("Processing batch %d/%d with %d titles", batch_num, total_batches, len(batch))

# INFO: General informational messages
logger.info("Processing language: %s (%d articles)", lang, len(titles))

# WARNING: Something unexpected but recoverable
logger.warning("Skipped bot account: %s", username)

# ERROR: Error that prevented an operation
logger.error("Failed to connect to %s: %s", dbname, str(e), exc_info=True)

# CRITICAL: Serious error that may prevent program from continuing
logger.critical("Could not load credentials file: %s", credential_file)
```

### Structured Logging

```python
# Include relevant context
logger.info(
    "Query completed",
    extra={
        "lang": lang,
        "batch": batch_num,
        "results": len(results),
        "duration_ms": duration
    }
)
```

### Don't Log Sensitive Data

❌ **Wrong**:
```python
logger.info("Password: %s", password)
```

✅ **Correct**:
```python
logger.info("Authentication successful")
```

---

## Database Code

### Always Use Context Managers

❌ **Wrong**:
```python
conn = pymysql.connect(host=host, database=db)
cursor = conn.cursor()
cursor.execute(query)
results = cursor.fetchall()
cursor.close()
conn.close()
```

✅ **Correct**:
```python
with Database(host, db) as database:
    results = database.execute(query)
```

### Escape User Input

❌ **Wrong**:
```python
query = f"SELECT * FROM page WHERE page_title = '{title}'"
```

✅ **Correct**:
```python
escaped_title = pymysql.converters.escape_string(title)
query = f"SELECT * FROM page WHERE page_title = '{escaped_title}'"
```

### Batch Large Queries

❌ **Wrong**:
```python
# Query with 10,000 titles in IN clause
titles_str = "', '".join(all_titles)
query = f"SELECT * FROM page WHERE page_title IN ('{titles_str}')"
```

✅ **Correct**:
```python
# Process in batches of 100
for batch in batched(all_titles, 100):
    escaped = [pymysql.converters.escape_string(t) for t in batch]
    titles_str = "', '".join(escaped)
    query = f"SELECT * FROM page WHERE page_title IN ('{titles_str}')"
    results = database.execute(query)
```

---

## Testing

### Test File Naming

```
tests/
  unit/
    test_database.py
    test_processor.py
    test_utils.py
  integration/
    test_queries.py
    test_workflow.py
```

### Test Function Naming

```python
def test_is_ip_address_with_ipv4():
    """Test IP detection with valid IPv4 address."""
    pass

def test_is_ip_address_with_username():
    """Test IP detection with regular username."""
    pass

def test_get_editors_filters_bots():
    """Test that bot accounts are filtered from results."""
    pass
```

### Use pytest Markers

```python
import pytest

@pytest.mark.unit
def test_escape_title():
    """Test SQL title escaping."""
    pass

@pytest.mark.integration
@pytest.mark.slow
def test_full_workflow():
    """Test complete data pipeline."""
    pass

@pytest.mark.db
def test_database_connection():
    """Test database connection."""
    pass
```

### Mock External Dependencies

```python
@pytest.mark.unit
def test_process_language(mocker):
    """Test language processing with mocked database."""
    # Mock the database connection
    mock_db = mocker.Mock()
    mock_db.execute.return_value = [
        {"actor_name": "User1", "count": 10},
        {"actor_name": "User2", "count": 5}
    ]
    
    processor = EditorProcessor()
    result = processor.process_language("es", ["Title1"], "eswiki", "2024")
    
    assert result == {"User1": 10, "User2": 5}
```

---

## File Organization

### Module Structure

```python
"""
Module docstring.
"""

# Imports
import standard_lib
from third_party import something
from local import module

# Constants
CONSTANT_NAME = value

# Private module functions
def _private_function():
    pass

# Public module functions
def public_function():
    pass

# Classes
class MyClass:
    pass

# Main execution
if __name__ == "__main__":
    main()
```

### Class Structure

```python
class MyClass:
    """Class docstring."""
    
    # Class variables
    class_var = value
    
    def __init__(self, param):
        """Initialize the instance."""
        # Instance variables
        self.param = param
        self._private_var = None
    
    # Public methods
    def public_method(self):
        """Public method docstring."""
        pass
    
    # Private methods
    def _private_method(self):
        """Private method docstring."""
        pass
    
    # Special methods
    def __str__(self):
        """String representation."""
        return f"MyClass({self.param})"
```

---

## Comments

### When to Comment

✅ **Do comment**:
- Complex algorithms or logic
- Non-obvious business rules
- Workarounds for bugs
- Performance-critical sections
- SQL queries

❌ **Don't comment**:
- Obvious code
- Redundant information
- Instead of fixing bad code

### Good Comments

```python
# Calculate edit velocity: edits per day over the past 30 days
# This helps identify highly active editors
velocity = total_edits / days_active

# Escape title to prevent SQL injection (see OWASP Top 10)
escaped = pymysql.converters.escape_string(title)

# Use LIKE for year filtering instead of YEAR() for performance
# Index on rev_timestamp supports LIKE but not YEAR()
query = "WHERE rev_timestamp LIKE '2024%'"
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

---

## Code Smells to Avoid

### Magic Numbers

❌ **Wrong**:
```python
if len(batch) > 100:
    process_batch(batch)
```

✅ **Correct**:
```python
BATCH_SIZE = 100

if len(batch) > BATCH_SIZE:
    process_batch(batch)
```

### Long Functions

❌ **Wrong**: 200-line function doing everything

✅ **Correct**: Break into smaller, focused functions

```python
def process_language(lang, titles, dbname, year):
    """Process a single language."""
    batches = _create_batches(titles)
    results = _query_all_batches(batches, dbname, year)
    filtered = _filter_invalid_editors(results)
    aggregated = _aggregate_counts(filtered)
    return aggregated
```

### Deeply Nested Code

❌ **Wrong**:
```python
if condition1:
    if condition2:
        if condition3:
            if condition4:
                do_something()
```

✅ **Correct**: Use early returns
```python
if not condition1:
    return

if not condition2:
    return

if not condition3:
    return

if condition4:
    do_something()
```

---

## Git Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process or auxiliary tool changes

### Examples

```
feat(database): Add connection pooling

Implement connection pooling to prevent max_user_connections errors.
Connections are now reused across queries for the same database.

Closes #42
```

```
fix(processor): Filter IPv6 addresses correctly

Previous regex only matched IPv4. Updated to handle both IPv4 and IPv6.

Fixes #56
```

```
docs(readme): Add installation instructions

Added detailed step-by-step installation guide including virtual
environment setup and credential configuration.
```

---

## Security

### Never Commit Credentials

Add to `.gitignore`:
```
replica.my.cnf
.env
*.cnf
*.pem
*_key
```

### Validate Input

```python
def process_titles(titles: List[str]) -> Dict[str, int]:
    """Process article titles."""
    if not titles:
        raise ValueError("Titles list cannot be empty")
    
    if len(titles) > 10000:
        raise ValueError("Too many titles (max: 10000)")
    
    for title in titles:
        if not isinstance(title, str):
            raise TypeError(f"Expected str, got {type(title)}")
    
    # Process...
```

### Use Prepared Statements

When possible, use parameterized queries:

```python
# If pymysql supports it for your query
cursor.execute(
    "SELECT * FROM page WHERE page_id = %s",
    (page_id,)
)
```

---

## Performance

### Profile Before Optimizing

```python
import time

start = time.time()
result = expensive_operation()
duration = time.time() - start
logger.info("Operation took %.2f seconds", duration)
```

### Cache When Appropriate

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_database_mapping() -> Dict[str, str]:
    """Get database mapping (cached)."""
    # This result is cached
    pass
```

### Iterate, Don't Load All

❌ **Wrong**:
```python
results = cursor.fetchall()  # Loads all into memory
for row in results:
    process(row)
```

✅ **Correct**:
```python
for row in cursor:  # Iterates one at a time
    process(row)
```

---

## Code Review Checklist

Before submitting code, verify:

- [ ] Follows naming conventions
- [ ] Has type hints
- [ ] Has docstrings
- [ ] Handles errors appropriately
- [ ] Logs important events
- [ ] Passes all tests
- [ ] Has test coverage >80%
- [ ] No hardcoded values
- [ ] No SQL injection vulnerabilities
- [ ] Uses context managers for resources
- [ ] No credentials in code
- [ ] Formatted with Black
- [ ] Imports sorted with isort
- [ ] Passes flake8
- [ ] Documentation updated

---

*These conventions should be followed consistently across the entire codebase.*
