# Prompt for GitHub Copilot

I'm building a Wikipedia Medicine Editor Analysis tool in Python. Follow the implementation plan in `plans/wikipedia_medicine_project_plan_v2.md`.

## Project Overview
- **Purpose**: Analyze editor contributions across Wikipedia Medicine projects in multiple languages
- **Tech Stack**: Python 3.9+, PyMySQL, colorlog, pytest
- **Database**: Wikimedia Toolforge read replicas

## Key Requirements

### Code Standards
- **Style**: Black (120 char), PEP 8, type hints, Google docstrings
- **Logging**: Use colorlog (DEBUG=cyan, INFO=green, WARNING=yellow, ERROR=red)
- **Testing**: pytest with >80% coverage, use markers (@pytest.mark.unit)
- **Error Handling**: Specific exceptions, always log with context
- **Database**: Always use context managers (`with` statements)

### Reference Documentation
- **Architecture**: `.claude/context/architecture.md`
- **Database Schema**: `.claude/context/database_schema.md`
- **Conventions**: `.claude/context/conventions.md`
- **Logging Guide**: `.claude/context/color_logging_guide.md`

## Implementation Order

### Phase 1: Core Infrastructure (Start Here)

1. **`src/logging_config.py`** - Color logging setup with colorlog
   ```python
   def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None
   def get_logger(name: str) -> logging.Logger
   ```

2. **`src/config.py`** - Configuration constants
   ```python
   from datetime import datetime
   LAST_YEAR = str(datetime.now().year - 1)
   BATCH_SIZE = 100
   DATABASE_CONFIG = {...}
   ```

3. **`src/utils.py`** - Helper functions
   ```python
   def is_ip_address(text: str) -> bool
   def escape_title(title: str) -> str
   def format_number(num: int) -> str
   ```

4. **`src/database.py`** - Database connection manager
   ```python
   class Database:
       def __enter__(self) -> 'Database'
       def __exit__(self, exc_type, exc_val, exc_tb) -> None
       def execute(self, query: str) -> List[Dict[str, Any]]
   ```

5. **`src/queries.py`** - SQL query builders
   ```python
   class QueryBuilder:
       @staticmethod
       def get_medicine_titles() -> str
       @staticmethod
       def get_editors_standard(titles: List[str], year: str) -> str
   ```

6. **`src/processor.py`** - Data processing
   ```python
   class EditorProcessor:
       def process_language(self, lang: str, titles: List[str], dbname: str, year: str) -> Dict[str, int]
   ```

7. **`src/reports.py`** - Report generation
   ```python
   class ReportGenerator:
       def generate_language_report(self, lang: str, editors: Dict[str, int]) -> None
       def generate_global_report(self, all_editors: Dict[str, Dict[str, int]]) -> None
   ```

8. **`src/main.py`** - Entry point
   ```python
   def main() -> int
   ```

### Phase 2: Testing
- Create corresponding test files in `tests/unit/` for each module
- Use pytest fixtures, mocking, and parametrize

## Important Patterns

### Logging (Every Module)
```python
from src.logging_config import get_logger
logger = get_logger(__name__)

logger.info("✓ Step complete: %d items processed", count)  # Green
logger.debug("Query batch %d/%d", i, total)                # Cyan
logger.warning("Skipped bot: %s", username)                # Yellow
logger.error("Failed to connect: %s", str(e))              # Red
```

### Database Access
```python
with Database(host, database) as db:
    results = db.execute(query)
# Connection auto-closed
```

### SQL Injection Prevention
```python
from src.utils import escape_title
escaped = escape_title(title)
query = f"WHERE page_title = '{escaped}'"
```

### Error Handling
```python
try:
    result = operation()
except pymysql.err.OperationalError as e:
    logger.error("Database error: %s", str(e), exc_info=True)
    raise
```

## Workflow Steps

1. **Step 1**: Query enwiki_p for Medicine articles + langlinks → `languages/{lang}.json`
2. **Step 2**: Query meta_p for database mapping (lang → dbname)
3. **Step 3**: For each language, query editor statistics → `editors/{lang}.json`
   - **Special**: Arabic uses project assessment query
   - **Special**: English uses templatelinks query
4. **Step 4**: Generate per-language WikiText reports → `reports/{lang}.wiki`
5. **Step 5**: Generate global summary report → `reports/total_report.wiki`

## Quick Commands

```bash
# Setup
pip install -r requirements.txt

# Run
python -m src.main --log-level DEBUG

# Test
pytest tests/unit -v
```

## Next Action
Start by implementing `src/logging_config.py` following the example in `plans/wikipedia_medicine_project_plan_v2.md` section "1. Logging Configuration".
