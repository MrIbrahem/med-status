# Color Logging Guide

## Overview

This project uses **colorlog** for colored console output to improve log readability during development and production monitoring.

## Installation

```bash
pip install colorlog==6.8.2
```

Already included in `requirements.txt`.

---

## Color Scheme

### Standard Colors by Level

```python
LOG_COLORS = {
    'DEBUG':    'cyan',
    'INFO':     'green',
    'WARNING':  'yellow',
    'ERROR':    'red',
    'CRITICAL': 'red,bg_white',
}
```

### Visual Reference

```
DEBUG    → Cyan       (detailed diagnostic info)
INFO     → Green      (normal progress updates)
WARNING  → Yellow     (recoverable issues)
ERROR    → Red        (failures requiring attention)
CRITICAL → Red/White  (severe errors)
```

---

## Implementation

### Basic Setup (src/logging_config.py)

```python
"""
Logging configuration with colored output.
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
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create color formatter for console
    console_formatter = colorlog.ColoredFormatter(
        fmt='%(log_color)s%(asctime)s - %(name)s - %(levelname)-8s%(reset)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(numeric_level)

    # Root logger configuration
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
```

---

## Usage in Modules

### Standard Pattern

```python
"""Example module with colored logging."""
import logging
from src.logging_config import get_logger

# Get module logger
logger = get_logger(__name__)


def process_data(data):
    """Process data with comprehensive logging."""

    # DEBUG - Detailed diagnostic info (CYAN)
    logger.debug("Starting data processing with %d items", len(data))
    logger.debug("Configuration: batch_size=%d, timeout=%d", 100, 30)

    # INFO - Normal progress updates (GREEN)
    logger.info("Processing batch 1/10")
    logger.info("Found 45,231 articles across 87 languages")
    logger.info("Language 'es' complete: 156 editors found")

    # WARNING - Recoverable issues (YELLOW)
    logger.warning("Skipped bot account: ExampleBot")
    logger.warning("Skipped IP address: 192.168.1.1")
    logger.warning("Retrying connection (attempt 2/3)")

    # ERROR - Failures requiring attention (RED)
    logger.error("Failed to connect to dewiki_p: Connection timeout")
    logger.error("Query execution failed: %s", str(error), exc_info=True)

    # CRITICAL - Severe errors (RED on WHITE background)
    logger.critical("Could not load credentials file: ~/replica.my.cnf")
    logger.critical("Fatal error: Cannot continue execution")
```

---

## Color Patterns by Use Case

### Workflow Progress (INFO - Green)

```python
logger.info("=" * 60)
logger.info("Starting Step 1: Retrieving medicine titles from enwiki")
logger.info("=" * 60)

logger.info("Processing language: es (1,234 articles)")
logger.info("Completed 25/87 languages (28.7%%)")
logger.info("Total editors found: 12,456")

logger.info("✓ Step 1 complete")
```

### Debugging Information (DEBUG - Cyan)

```python
logger.debug("Executing query batch 1/13 (100 titles)")
logger.debug("Query: %s", query[:100])  # First 100 chars
logger.debug("Parameters: lang=%s, year=%s", lang, year)
logger.debug("Result count: %d rows", len(results))
logger.debug("Memory usage: %.2f MB", memory_mb)
```

### Warnings (WARNING - Yellow)

```python
# Skipped items
logger.warning("Skipped bot account: %s", username)
logger.warning("Skipped IP address: %s", ip_address)

# Retries
logger.warning("Connection timeout, retrying... (attempt %d/%d)", attempt, max_attempts)

# Partial failures
logger.warning("Could not process 3 titles due to encoding errors")

# Performance issues
logger.warning("Query took %.2f seconds (threshold: 5s)", duration)
```

### Errors (ERROR - Red)

```python
# Connection failures
logger.error("Failed to connect to %s: %s", dbname, str(e))

# Query errors
logger.error("Query execution failed for language '%s': %s", lang, str(e))
logger.error("SQL syntax error in query: %s", query, exc_info=True)

# Data errors
logger.error("Invalid data format in %s: %s", filename, str(e))

# With stack trace
try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed: %s", str(e), exc_info=True)
```

### Critical Errors (CRITICAL - Red/White)

```python
# Fatal errors that stop execution
logger.critical("Credentials file not found: %s", credential_file)
logger.critical("Cannot connect to any database - aborting")
logger.critical("Disk full - cannot write output files")
logger.critical("Fatal: Unrecoverable error in main workflow")
```

---

## Advanced Formatting

### With Extra Context (Colored)

```python
# Using secondary colors for specific info
console_formatter = colorlog.ColoredFormatter(
    fmt='%(log_color)s%(asctime)s%(reset)s - '
        '%(bold_blue)s%(name)s%(reset)s - '
        '%(log_color)s%(levelname)-8s%(reset)s - '
        '%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={
        'message': {
            'DEBUG':    'white',
            'INFO':     'white',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red'
        }
    }
)
```

### Progress Indicators with Colors

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

# Usage
log_progress(25, 87, "languages")
# Output (in green):
# INFO: Progress: [███████████░░░░░░░░░░░░░░░░░░░] 28.7% (25/87 languages)
```

### Structured Logging with Colors

```python
def log_statistics(stats: dict):
    """Log statistics in a formatted, colored way."""
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

# Usage
log_statistics({
    "Total Languages": 87,
    "Total Articles": 45231,
    "Total Editors": 12456,
    "Processing Time (seconds)": 342.56,
    "Average per Language": 3.94
})
```

---

## Example Output

### Console Output (with colors)

```
2025-01-28 14:30:15 - src.main - INFO     - ============================================================
2025-01-28 14:30:15 - src.main - INFO     - Starting Wikipedia Medicine Editor Analysis
2025-01-28 14:30:15 - src.main - INFO     - ============================================================
2025-01-28 14:30:16 - src.services.database - DEBUG    - Connecting to enwiki.analytics.db.svc.wikimedia.cloud
2025-01-28 14:30:17 - src.services.database - INFO     - Connected to enwiki_p successfully
2025-01-28 14:30:17 - src.main - INFO     - Step 1: Retrieving medicine titles from enwiki
2025-01-28 14:30:45 - src.main - INFO     - Found 45,231 articles across 87 languages
2025-01-28 14:30:45 - src.main - INFO     - Saved languages/en.json
2025-01-28 14:30:46 - src.services.processor - INFO     - Processing language: es (1,234 articles)
2025-01-28 14:30:47 - src.services.processor - DEBUG    - Executing query batch 1/13 (100 titles)
2025-01-28 14:30:48 - src.services.processor - WARNING  - Skipped bot account: SpanishBot
2025-01-28 14:30:49 - src.services.processor - WARNING  - Skipped IP address: 192.168.1.1
2025-01-28 14:31:15 - src.services.processor - INFO     - Language 'es' complete: 156 editors found
2025-01-28 14:31:16 - src.services.database - ERROR    - Failed to connect to dewiki_p: Connection timeout
2025-01-28 14:31:17 - src.services.database - WARNING  - Retrying connection (attempt 2/3)
2025-01-28 14:31:20 - src.services.database - INFO     - Connected to dewiki_p successfully
2025-01-28 14:45:30 - src.main - INFO     - ============================================================
2025-01-28 14:45:30 - src.main - INFO     - Processing Complete
2025-01-28 14:45:30 - src.main - INFO     - Total languages processed: 87
2025-01-28 14:45:30 - src.main - INFO     - Total editors found: 12,456
2025-01-28 14:45:30 - src.main - INFO     - Duration: 15:15
2025-01-28 14:45:30 - src.main - INFO     - ============================================================
```

**Visual in console:**
- `DEBUG` messages appear in **cyan**
- `INFO` messages appear in **green**
- `WARNING` messages appear in **yellow**
- `ERROR` messages appear in **red**

---

## File Output (no colors)

When logging to a file, colors are automatically stripped:

```
2025-01-28 14:30:15 - src.main - INFO     - Starting Wikipedia Medicine Editor Analysis
2025-01-28 14:30:17 - src.services.database - INFO     - Connected to enwiki_p successfully
2025-01-28 14:30:45 - src.main - INFO     - Found 45,231 articles across 87 languages
2025-01-28 14:31:16 - src.services.database - ERROR    - Failed to connect to dewiki_p: Connection timeout
```

---

## Integration with main.py

```python
"""Main application entry point."""
import argparse
from src.logging_config import setup_logging, get_logger

# Initialize logger for this module
logger = get_logger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Wikipedia Medicine Editor Analysis"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)"
    )
    parser.add_argument(
        "--log-file",
        default=None,
        help="Optional log file path"
    )
    return parser.parse_args()


def main():
    """Main application workflow."""
    # Parse arguments
    args = parse_arguments()

    # Setup colored logging
    setup_logging(level=args.log_level, log_file=args.log_file)

    # Log startup
    logger.info("=" * 60)
    logger.info("Starting Wikipedia Medicine Editor Analysis")
    logger.info("=" * 60)
    logger.debug("Log level: %s", args.log_level)
    logger.debug("Log file: %s", args.log_file or "console only")

    try:
        # Run workflow steps
        logger.info("Step 1: Retrieving medicine titles")
        # ... implementation ...

        logger.info("Step 2: Processing languages")
        # ... implementation ...

        logger.info("✓ All steps completed successfully")

    except Exception as e:
        logger.critical("Fatal error in main workflow: %s", str(e), exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
```

---

## Best Practices

### 1. Use Appropriate Levels

```python
# ✓ Good
logger.debug("Processing batch 5/10")           # Development info
logger.info("Language processing complete")     # User-relevant progress
logger.warning("Retrying connection")           # Recoverable issue
logger.error("Database query failed")           # Operation failed
logger.critical("Cannot access credentials")    # Fatal error

# ✗ Bad
logger.info("x=5, y=10, z=15")                 # Too detailed → use DEBUG
logger.error("Processing language es")          # Not an error → use INFO
logger.critical("Skipped bot account")          # Not critical → use WARNING
```

### 2. Include Context

```python
# ✓ Good
logger.error("Failed to connect to %s: %s", dbname, str(e))
logger.warning("Skipped bot account: %s (matched pattern: %s)", username, pattern)

# ✗ Bad
logger.error("Connection failed")              # What connection?
logger.warning("Skipped")                      # Skipped what?
```

### 3. Use String Formatting

```python
# ✓ Good - Lazy evaluation
logger.debug("Processing %s with %d items", name, len(items))

# ✗ Bad - Evaluated even if DEBUG is disabled
logger.debug(f"Processing {name} with {len(items)} items")
```

### 4. Structure Long Output

```python
# ✓ Good - Easy to read
logger.info("=" * 60)
logger.info("Processing Summary")
logger.info("-" * 60)
logger.info("Languages: %d", count)
logger.info("Editors: %d", editors)
logger.info("=" * 60)

# ✗ Bad - Hard to parse
logger.info("Processing Summary Languages: %d Editors: %d", count, editors)
```

### 5. Visual Separators

```python
# Section headers
logger.info("=" * 60)
logger.info("SECTION TITLE")
logger.info("=" * 60)

# Subsection headers
logger.info("-" * 60)
logger.info("Subsection")
logger.info("-" * 60)

# List items
logger.info("✓ Task completed")
logger.info("✗ Task failed")
logger.info("→ Processing next item")
```

---

## Testing Logging

### Test Log Output

```python
"""Test logging configuration."""
from src.logging_config import setup_logging, get_logger


def test_all_levels():
    """Test all logging levels with colors."""
    setup_logging(level="DEBUG")
    logger = get_logger("test")

    logger.debug("This is a DEBUG message (cyan)")
    logger.info("This is an INFO message (green)")
    logger.warning("This is a WARNING message (yellow)")
    logger.error("This is an ERROR message (red)")
    logger.critical("This is a CRITICAL message (red/white)")

    logger.info("=" * 60)
    logger.info("Color test complete - check console output")
    logger.info("=" * 60)


if __name__ == "__main__":
    test_all_levels()
```

---

## Troubleshooting

### Colors Not Showing

**Problem**: Colors not appearing in console

**Solutions**:

1. **Check terminal support**:
   ```bash
   # Test if terminal supports colors
   echo -e "\033[31mRed\033[0m \033[32mGreen\033[0m \033[33mYellow\033[0m"
   ```

2. **Force color output**:
   ```python
   import colorlog
   colorlog.basicConfig(force_color=True)
   ```

3. **Check if output is redirected**:
   - Colors are automatically disabled when output is piped
   - Use `--log-file` for file output without colors

### Performance Impact

**Q**: Does colorlog slow down logging?

**A**: Minimal impact (<1% in most cases)
- Colors only applied to console handler
- File handler uses plain format
- String formatting is lazy (only when level is enabled)

---

## CLI Usage Examples

```bash
# Default (INFO level, console only)
python -m src.main

# DEBUG level for detailed output
python -m src.main --log-level DEBUG

# Save logs to file (no colors in file)
python -m src.main --log-file wikipedia_medicine.log

# Both console (colored) and file (plain)
python -m src.main --log-level DEBUG --log-file debug.log

# Production (WARNING and above only)
python -m src.main --log-level WARNING
```

---

## Configuration in config.py

```python
"""Application configuration."""

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = None
LOG_FORMAT_CONSOLE = '%(log_color)s%(asctime)s - %(name)s - %(levelname)-8s%(reset)s %(message)s'
LOG_FORMAT_FILE = '%(asctime)s - %(name)s - %(levelname)-8s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

LOG_COLORS = {
    'DEBUG':    'cyan',
    'INFO':     'green',
    'WARNING':  'yellow',
    'ERROR':    'red',
    'CRITICAL': 'red,bg_white',
}
```

---

## Summary

✅ **colorlog** provides colored console output
✅ **Green** INFO for progress, **Red** ERROR for failures
✅ **Yellow** WARNING for recoverable issues
✅ **Cyan** DEBUG for development details
✅ File output automatically strips colors
✅ Minimal performance impact
✅ Easy to configure per environment

Use colors to make logs **readable**, **scannable**, and **actionable**!
