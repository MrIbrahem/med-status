# Claude AI Assistant Configuration & Best Practices

This directory contains configuration files and guidelines for using Claude AI assistant effectively with this project.

## Directory Structure

```
.claude/
├── README.md
├── CLAUDE.md                      # Main guide for working with Claude
├── settings.json                  # Project configuration for Claude
├── prompts/
│   ├── code_review.md
│   ├── debugging.md
│   ├── refactoring.md
│   ├── testing.md
│   └── templates.md               # Reusable prompt templates
├── context/
│   ├── architecture.md            # Project architecture documentation
│   ├── database_schema.md         # Database schema reference
│   ├── conventions.md             # Coding standards and conventions
│   └── color_logging_guide.md     # Color logging implementation guide
└── examples/
    └── prompt_examples.md         # Examples of good vs bad prompts
```

---

## File: `.claude/CLAUDE.md`

# Working with Claude on Wikipedia Medicine Project

## Project Overview

This is a Python application for analyzing Wikipedia Medicine project editors across multiple languages. Claude should understand:

- **Purpose**: Retrieve and analyze editor contributions from Wikipedia databases
- **Tech Stack**: Python 3.9+, PyMySQL, Wikimedia Toolforge
- **Architecture**: Modular design with Database, Processor, and Report Generator components
- **Data Flow**: Query → Process → Aggregate → Report

## Core Principles for Claude

### 1. Context Awareness

When working with Claude on this project, always provide:

- **What module** you're working on (database.py, queries.py, etc.)
- **What you're trying to achieve** (fix bug, add feature, optimize query)
- **Relevant error messages** (full stack traces when debugging)
- **Current code snippet** (the specific function/class in question)

### 2. Code Style & Conventions

Claude should follow these project-specific conventions:

#### Python Style
- **Line length**: 120 characters (Black formatter)
- **Type hints**: Use for function signatures
- **Docstrings**: Google style for all public functions
- **Imports**: Sorted with isort (stdlib → third-party → local)

#### Database Conventions
- **Always use context managers** (`with` statements) for connections
- **Escape SQL inputs** with `pymysql.converters.escape_string()`
- **Batch queries** in groups of 100 for large datasets
- **Log all database operations** at INFO level

#### Error Handling
- **Catch specific exceptions** (no bare `except:`)
- **Log errors** with full context
- **Graceful degradation** (continue processing other languages on failure)
- **Retry logic** for transient database errors (max 3 attempts)

#### Naming Conventions
- **Functions**: `snake_case` (e.g., `get_editor_stats`)
- **Classes**: `PascalCase` (e.g., `DatabaseManager`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `BATCH_SIZE`)
- **Private methods**: Prefix with `_` (e.g., `_execute_query`)

### 3. Testing Requirements

When Claude writes or modifies code:

- **Write tests first** for new features (TDD preferred)
- **Update existing tests** when changing behavior
- **Use pytest markers** appropriately:
  - `@pytest.mark.unit` for isolated tests
  - `@pytest.mark.integration` for database tests
  - `@pytest.mark.slow` for long-running tests
- **Mock external dependencies** (databases, network calls)
- **Aim for >80% coverage** on new code

### 4. Documentation Standards

Claude should:

- **Update docstrings** when changing function signatures
- **Add inline comments** for complex logic (especially SQL queries)
- **Update README.md** for user-facing changes
- **Add CHANGELOG.md entries** for notable changes
- **Include examples** in docstrings for non-obvious functions

### 5. SQL Query Guidelines

When writing SQL queries, Claude should:

- **Use parameterized queries** (prevent SQL injection)
- **Add comments** explaining complex joins
- **Optimize for read replicas** (assume read-only access)
- **Include LIMIT clauses** for safety in development
- **Use EXPLAIN** for performance analysis when needed

Example:
```python
def get_editors(self, titles: List[str], year: str) -> Dict[str, int]:
    """
    Retrieve editor statistics for given titles.

    Args:
        titles: List of article titles to query
        year: Year to filter revisions (e.g., "2024")

    Returns:
        Dictionary mapping editor names to edit counts

    Note:
        Filters out bot accounts and IP addresses automatically.
    """
    # Escape titles to prevent SQL injection
    escaped_titles = [pymysql.converters.escape_string(t) for t in titles]

    query = """
        SELECT actor_name, COUNT(*) as count
        FROM revision
        JOIN actor ON rev_actor = actor_id
        JOIN page ON rev_page = page_id
        WHERE page_title IN (%s)
          AND YEAR(rev_timestamp) = %s
          AND LOWER(CAST(actor_name AS CHAR)) NOT LIKE '%%bot%%'
        GROUP BY actor_id
    """
    # Implementation...
```

### 6. Logging Best Practices

Claude should implement consistent logging:

```python
import logging

logger = logging.getLogger(__name__)

# INFO: Progress and milestones
logger.info("Processing language: %s (%d articles)", lang, len(titles))

# DEBUG: Detailed execution flow
logger.debug("Executing query batch %d/%d", batch_num, total_batches)

# WARNING: Recoverable issues
logger.warning("Skipped IP address: %s", actor_name)

# ERROR: Failures requiring attention
logger.error("Failed to connect to %s: %s", dbname, str(e), exc_info=True)
```

---

## Common Tasks & Prompts

### Debugging

**Good Prompt:**
```
I'm getting a "max_user_connections" error in database.py when processing
multiple languages. Here's the current code [paste code]. The error occurs
after processing about 5 languages. How can I ensure connections are properly
closed?
```

**What Claude needs:**
- Error message
- When it occurs
- Relevant code
- What you've tried

### Adding Features

**Good Prompt:**
```
I need to add a feature to export editor statistics to CSV format in addition
to WikiText. The CSV should have columns: Rank, Username, EditCount, Wiki.
Where should this go in the current architecture, and can you help implement it
following our existing patterns in reports.py?
```

**What Claude needs:**
- Feature description
- Expected output format
- Where it fits in architecture
- Existing patterns to follow

### Code Review

**Good Prompt:**
```
Please review this implementation of the batch query processor in processor.py
[paste code]. Check for:
1. Proper error handling
2. SQL injection prevention
3. Performance issues
4. Code style compliance
```

**What Claude needs:**
- Code to review
- Specific concerns
- Context (which module, what it does)

### Refactoring

**Good Prompt:**
```
The main.py file is getting too long (500+ lines). Can you help refactor it
into smaller modules while maintaining the current workflow? Suggest a new
structure that follows our separation of concerns.
```

**What Claude needs:**
- What's wrong
- Current structure
- Desired outcome
- Constraints

---

## Project-Specific Context

### Database Schema Understanding

Claude should know these key tables:

**enwiki_p database:**
- `page`: Article metadata (page_id, page_title, page_namespace)
- `langlinks`: Cross-wiki language links (ll_from, ll_lang, ll_title)
- `page_assessments`: Article quality ratings (pa_page_id, pa_project_id)
- `page_assessments_projects`: Project definitions (pap_project_id, pap_project_title)
- `revision`: Edit history (rev_id, rev_page, rev_actor, rev_timestamp)
- `actor`: Editor information (actor_id, actor_name)

**meta_p database:**
- `wiki`: Wikimedia project metadata (dbname, family, lang, url, is_closed)

### Workflow Steps

Claude should understand the complete workflow:

1. **Title Retrieval**: Query enwiki for Medicine project articles + langlinks
2. **Database Mapping**: Get language → database mapping from meta_p
3. **Editor Queries**: For each language, query editor statistics
   - Standard languages: Filter by titles (batched)
   - Arabic: Use project assessment directly
   - English: Use templatelinks for WikiProject Medicine
4. **Aggregation**: Combine editor counts, filter bots/IPs
5. **Report Generation**: Create WikiText tables per language + global summary

### Special Cases

Claude should remember these edge cases:

1. **Arabic Wikipedia**: Uses different query (project assessment)
2. **English Wikipedia**: Uses templatelinks instead of langlinks
3. **IP Addresses**: Must be filtered out (IPv4 and IPv6)
4. **Bot Accounts**: Filter by checking username contains "bot" (case-insensitive)
5. **Connection Limits**: Max 5 concurrent connections to prevent errors
6. **Batch Size**: 100 titles per query to prevent timeouts

---

## Anti-Patterns to Avoid

Claude should NOT:

❌ **Suggest bare except clauses**
```python
try:
    # some code
except:  # Too broad!
    pass
```

✅ **Use specific exceptions**
```python
try:
    # some code
except pymysql.err.OperationalError as e:
    logger.error("Database connection failed: %s", e)
    raise
```

❌ **Forget to close connections**
```python
conn = pymysql.connect(...)
cursor = conn.cursor()
# ... query code ...
# Forgot to close!
```

✅ **Use context managers**
```python
with Database(host, db) as db:
    results = db.execute(query)
# Automatically closed
```

❌ **Build SQL with string concatenation**
```python
query = f"SELECT * FROM page WHERE page_title = '{title}'"  # SQL injection risk!
```

✅ **Use parameterization or proper escaping**
```python
escaped_title = pymysql.converters.escape_string(title)
query = f"SELECT * FROM page WHERE page_title = '{escaped_title}'"
```

❌ **Ignore logging**
```python
# Silent failure
if not results:
    return {}
```

✅ **Log important events**
```python
if not results:
    logger.warning("No results found for language: %s", lang)
    return {}
```

---

## Troubleshooting Guide

### Common Issues Claude Can Help With

#### 1. Connection Errors

**Symptom**: `max_user_connections exceeded`
**Solution**: Ensure `with` statements are used, reduce MAX_CONNECTIONS in config

**Prompt for Claude:**
```
I'm hitting max_user_connections. Can you audit all database connection code
in [module] and ensure proper connection management?
```

#### 2. Query Timeouts

**Symptom**: `pymysql.err.OperationalError: (1205, 'Lock wait timeout')`
**Solution**: Reduce batch size, add query timeouts, optimize query

**Prompt for Claude:**
```
This query is timing out [paste query]. Can you optimize it or suggest
breaking it into smaller chunks?
```

#### 3. Memory Issues

**Symptom**: `MemoryError` when processing large result sets
**Solution**: Use cursor iteration instead of fetchall(), process in batches

**Prompt for Claude:**
```
I'm running out of memory when fetching all results. Can you refactor this
to use cursor iteration?
```

#### 4. Unicode Errors

**Symptom**: `UnicodeEncodeError` when writing reports
**Solution**: Ensure UTF-8 encoding for all file operations

**Prompt for Claude:**
```
Getting Unicode errors when writing WikiText files. Here's the current code
[paste]. How should I handle non-ASCII characters?
```

---

## Version-Specific Notes

### Python 3.9+
- Use type hints with `from __future__ import annotations` for forward references
- Prefer `dict` over `Dict` for type hints (PEP 585)
- Use `list[str]` instead of `List[str]` when possible

### PyMySQL
- Always use `charset='utf8mb4'` for connections
- Enable `autocommit=True` for read-only queries
- Set `read_timeout` and `write_timeout` for long queries

### Toolforge Environment
- Credentials in `~/replica.my.cnf`
- Read replicas only (no writes)
- Connection format: `{dbname}.analytics.db.svc.wikimedia.cloud`
- Database naming: `{dbname}_p`

---

## Integration with Development Tools

### With VS Code
- Claude can help interpret pytest output in terminal
- Review code changes in diff view
- Explain linter warnings from Problems panel

### With Git
- Claude can help write commit messages following conventions
- Review PR diffs
- Suggest refactoring before committing

### With pytest
- Claude can help interpret test failures
- Suggest test cases for new features
- Debug mocking issues

---

## Effective Communication with Claude

### Do's ✅

1. **Provide full context**: Share error messages, stack traces, relevant code
2. **Be specific**: "Fix the connection leak in database.py" vs "Fix the bug"
3. **Ask for explanations**: "Why does this query timeout?" helps learning
4. **Request alternatives**: "What are other ways to implement this?"
5. **Verify understanding**: "Does this approach make sense for our architecture?"

### Don'ts ❌

1. **Don't paste entire files**: Share only relevant functions/classes
2. **Don't assume Claude remembers**: Provide context each time
3. **Don't skip error details**: Full stack traces are helpful
4. **Don't ask multiple unrelated questions**: One topic per conversation
5. **Don't expect Claude to run code**: Provide test results/outputs

---

## Learning Resources

When Claude suggests unfamiliar concepts, ask for:

- **Explanation**: "Can you explain what a context manager is?"
- **Examples**: "Show me an example of using pytest fixtures"
- **Documentation**: "Where can I learn more about PyMySQL cursors?"
- **Best practices**: "What's the recommended way to handle this in Python?"

---

## Project Evolution

As the project grows, update this document with:

- New modules and their purposes
- Additional conventions adopted
- Common issues encountered
- Lessons learned
- Architecture changes

Keep Claude informed of these updates for better assistance.

---

## Quick Reference Card

```
PROJECT: Wikipedia Medicine Editor Analysis
LANGUAGE: Python 3.9+
STYLE: Black (120 chars), isort, flake8
TESTS: pytest with >80% coverage
DOCS: Google-style docstrings
DB: PyMySQL → Wikimedia Toolforge
LOGGING: Python logging module
STRUCTURE: src/ (code), tests/ (tests), reports/ (output)

KEY FILES:
- database.py: DB connection management
- queries.py: SQL query templates
- processor.py: Data processing logic
- reports.py: WikiText generation
- main.py: Orchestration

SPECIAL HANDLING:
- Arabic (ar): Project assessment query
- English (en): Templatelinks query
- Others: Standard langlinks query
```

---

## Contact & Support

For questions about:
- **Architecture decisions**: Review `context/architecture.md`
- **Database schema**: Review `context/database_schema.md`
- **Code conventions**: Review `context/conventions.md`
- **Prompt templates**: Check `prompts/` directory
- **Example interactions**: See `examples/` directory

---

*Last updated: 2025-01-28*
*Maintained by: Project Team*
*Version: 1.0.0*
