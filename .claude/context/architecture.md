# Project Architecture

## Overview

The Wikipedia Medicine project is designed as a modular data pipeline that retrieves, processes, and reports on editor contributions across Wikipedia's Medicine projects in multiple languages.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Entry Point (main.py)                     │
│  • CLI argument parsing                                          │
│  • Logging configuration                                         │
│  • Workflow orchestration                                        │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────────┐
│                    Configuration (config.py)                    │
│  • Years (LAST_YEAR, CURRENT_YEAR)                             │
│  • Batch size, connection limits                                │
│  • Output directories                                           │
└────────────────────────────────────────────────────────────────┘

                 ┌────────────────────┐
                 │   Data Flow        │
                 └────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Database    │  │   Queries    │  │  Processor   │
│  (database.py)│  │ (queries.py) │  │(processor.py)│
└──────────────┘  └──────────────┘  └──────────────┘
        │                 │                 │
        │  Connections    │  SQL Templates  │  Aggregation
        │  Credentials    │  Escaping       │  Filtering
        │  Context Mgmt   │  Parameterize   │  IP/Bot Detection
        │                 │                 │
        └─────────────────┴─────────────────┘
                          │
                          ▼
                 ┌──────────────┐
                 │   Reports    │
                 │ (reports.py) │
                 └──────────────┘
                          │
                          │  WikiText Generation
                          │  File Output
                          ▼
                 ┌──────────────┐
                 │  Output Files│
                 │ • languages/ │
                 │ • editors/   │
                 │ • reports/   │
                 └──────────────┘
```

## Component Details

### 1. Main Application (main.py)

**Responsibilities:**
- Parse command-line arguments
- Configure logging
- Initialize output directories
- Orchestrate workflow execution
- Handle top-level errors

**Key Functions:**
```python
def main() -> None
def setup_logging(level: str) -> None
def create_directories() -> None
def run_workflow(args: argparse.Namespace) -> None
```

**Dependencies:**
- config.py (configuration constants)
- database.py (database connections)
- processor.py (data processing)
- reports.py (report generation)

---

### 2. Database Manager (database.py)

**Responsibilities:**
- Manage database connections
- Load credentials from ~/replica.my.cnf
- Execute queries with proper error handling
- Implement connection pooling
- Provide context manager interface

**Key Classes:**
```python
class Database:
    def __init__(self, host: str, database: str, port: int = 3306)
    def __enter__(self) -> 'Database'
    def __exit__(self, exc_type, exc_val, exc_tb) -> None
    def execute(self, query: str, params: Optional[Dict] = None) -> List[Dict]
    def _load_credentials(self) -> Dict[str, str]
    def _connect(self) -> pymysql.connections.Connection
```

**Design Patterns:**
- **Context Manager**: Ensures connections are properly closed
- **Singleton-like**: Connection pooling prevents excessive connections
- **Retry Pattern**: Handles transient database errors

**Error Handling:**
- Catches `pymysql.err.OperationalError` for connection issues
- Implements exponential backoff for retries
- Logs all connection events

---

### 3. Query Builder (queries.py)

**Responsibilities:**
- Store SQL query templates
- Build language-specific queries
- Escape SQL inputs safely
- Parameterize queries

**Key Classes:**
```python
class QueryBuilder:
    @staticmethod
    def get_medicine_titles() -> str
    @staticmethod
    def get_database_mapping() -> str
    @staticmethod
    def get_editors_standard(titles: List[str], year: str) -> str
    @staticmethod
    def get_editors_arabic(year: str) -> str
    @staticmethod
    def get_editors_english(year: str) -> str
```

**SQL Templates:**
1. Medicine titles query (enwiki)
2. Database mapping query (meta_p)
3. Standard editor query (with titles)
4. Arabic editor query (project assessment)
5. English editor query (templatelinks)

**Security:**
- All user inputs escaped with `pymysql.converters.escape_string()`
- Parameterized queries where possible
- No string concatenation with user input

---

### 4. Data Processor (processor.py)

**Responsibilities:**
- Aggregate editor statistics
- Filter bot accounts
- Filter IP addresses
- Batch process large title lists
- Normalize data for reporting

**Key Classes:**
```python
class EditorProcessor:
    def __init__(self, batch_size: int = 100)
    def aggregate_editors(self, results: List[Dict]) -> Dict[str, int]
    def is_bot(self, username: str) -> bool
    def is_ip_address(self, username: str) -> bool
    def batch_titles(self, titles: List[str]) -> List[List[str]]
    def process_language(self, lang: str, titles: List[str], dbname: str, year: str) -> Dict[str, int]
```

**Processing Logic:**
```
For each result row:
  1. Check if username contains "bot" (case-insensitive) → skip
  2. Check if username matches IP pattern → skip
  3. Aggregate edit count: editors[username] += count
  4. Return aggregated dictionary
```

**Batch Processing:**
- Splits large title lists into batches of 100
- Processes each batch sequentially
- Aggregates results across batches
- Prevents query timeouts

---

### 5. Report Generator (reports.py)

**Responsibilities:**
- Format editor statistics as WikiText tables
- Generate per-language reports
- Generate global summary report
- Write reports to files

**Key Classes:**
```python
class ReportGenerator:
    def __init__(self, output_dir: str = "reports")
    def generate_language_report(self, lang: str, editors: Dict[str, int]) -> str
    def generate_global_report(self, all_editors: Dict[str, Dict[str, int]]) -> str
    def write_report(self, filename: str, content: str) -> None
    def _format_wikitable(self, data: List[Tuple], headers: List[str]) -> str
```

**WikiText Format:**
```wikitext
{| class="sortable wikitable"
!#
!User
!Count
|-
!1
|[[:w:es:user:Username|Username]]
|1,234
|}
```

**Formatting Rules:**
- Numbers with thousands separator (e.g., 1,234)
- Interwiki links to user pages
- Sortable tables
- Rank column (1-indexed)

---

### 6. Utilities (utils.py)

**Responsibilities:**
- Helper functions used across modules
- IP address detection
- SQL escaping
- Number formatting

**Key Functions:**
```python
def is_ip_address(text: str) -> bool
def escape_title(title: str) -> str
def format_number(num: int) -> str
def ensure_directory(path: str) -> None
```

**IP Detection:**
- IPv4: `^\d+\.\d+\.\d+\.\d+$`
- IPv6: Full regex pattern for valid IPv6 addresses

---

### 7. Configuration (config.py)

**Responsibilities:**
- Store application constants
- Define output directories
- Set processing parameters

**Key Constants:**
```python
LAST_YEAR: str = "2024"
CURRENT_YEAR: str = "2025"
BATCH_SIZE: int = 100
MAX_CONNECTIONS: int = 5
CREDENTIAL_FILE: str = "~/replica.my.cnf"

OUTPUT_DIRS: Dict[str, str] = {
    "languages": "languages",
    "editors": "editors",
    "reports": "reports"
}

DATABASE_CONFIG: Dict[str, Any] = {
    "port": 3306,
    "charset": "utf8mb4",
    "connect_timeout": 30,
    "read_timeout": 60,
}
```

## Data Flow

### Step 1: Retrieve Medicine Titles

```
main.py
  → Database(enwiki.analytics.db.svc.wikimedia.cloud, enwiki_p)
  → QueryBuilder.get_medicine_titles()
  → Execute query
  → Process results into dictionary: {lang: [titles]}
  → Write to languages/{lang}.json
```

**Output Format:**
```json
{
  "Article_Title_1": "Title 1",
  "Article_Title_2": "Title 2"
}
```

### Step 2: Get Database Mapping

```
main.py
  → Database(meta.analytics.db.svc.wikimedia.cloud, meta_p)
  → QueryBuilder.get_database_mapping()
  → Execute query
  → Create dictionary: {lang: dbname}
  → Store in memory
```

### Step 3: Process Each Language

```
For each language:
  main.py
    → Load titles from languages/{lang}.json
    → Database({dbname}.analytics.db.svc.wikimedia.cloud, {dbname}_p)
    → EditorProcessor.process_language(lang, titles, dbname, year)
      → Batch titles (100 per batch)
      → For each batch:
        → QueryBuilder.get_editors_standard(batch, year)
        → Execute query
        → Filter bots and IPs
        → Aggregate counts
      → Combine batch results
    → Write to editors/{lang}.json
```

**Special Cases:**
- **Arabic (ar)**: Use `get_editors_arabic()` query
- **English (en)**: Use `get_editors_english()` query

**Output Format:**
```json
{
  "Username1": 1234,
  "Username2": 856
}
```

### Step 4: Generate Reports

```
main.py
  → For each language:
    → Load editors from editors/{lang}.json
    → ReportGenerator.generate_language_report(lang, editors)
    → Write to reports/{lang}.wiki

  → Combine all editor data
  → ReportGenerator.generate_global_report(all_editors)
  → Write to reports/total_report.wiki
```

## Error Handling Strategy

### Connection Errors

```python
try:
    with Database(host, db) as database:
        results = database.execute(query)
except pymysql.err.OperationalError as e:
    logger.error("Connection failed: %s", e)
    # Retry with exponential backoff
    # After 3 attempts, skip this language
```

### Query Errors

```python
try:
    results = database.execute(query)
except pymysql.err.ProgrammingError as e:
    logger.error("Query error: %s\nQuery: %s", e, query)
    # Log and continue with next batch
```

### Data Processing Errors

```python
try:
    processed = processor.aggregate_editors(results)
except Exception as e:
    logger.error("Processing error: %s", e, exc_info=True)
    # Return partial results or empty dict
```

## Concurrency & Performance

### Connection Management

- **Maximum Connections**: 5 concurrent database connections
- **Context Managers**: All connections use `with` statements
- **Connection Pooling**: Reuse connections where possible

### Batch Processing

- **Batch Size**: 100 titles per query
- **Sequential Processing**: Process batches one at a time
- **Memory Efficiency**: Stream results, don't load all into memory

### Query Optimization

- **Indexed Columns**: Use indexed columns in WHERE clauses
- **LIMIT Clauses**: Apply limits where appropriate
- **Read Replicas**: Use analytics.db.svc.wikimedia.cloud hosts

## Testing Strategy

### Unit Tests

- Test each module in isolation
- Mock database connections
- Test edge cases (empty lists, invalid input)
- Use pytest fixtures for common test data

### Integration Tests

- Test module interactions
- Mock database with realistic responses
- Test error handling and recovery
- Verify data flow through pipeline

### Test Coverage

- Aim for >80% code coverage
- Focus on critical paths
- Test error conditions
- Verify SQL escaping

## Scalability Considerations

### Current Limitations

- Sequential processing (one language at a time)
- Single-threaded execution
- Connection limit of 5

### Future Improvements

1. **Parallel Processing**: Use multiprocessing for independent languages
2. **Async I/O**: Use asyncio for concurrent database queries
3. **Caching**: Cache database mappings and common queries
4. **Progressive Reports**: Generate reports as data becomes available

## Security Considerations

### SQL Injection Prevention

- All titles escaped with `pymysql.converters.escape_string()`
- No string concatenation with user input
- Parameterized queries where possible

### Credential Management

- Credentials stored in `~/replica.my.cnf`
- Never logged or printed
- File permissions: 600 (user read/write only)

### Data Privacy

- No personally identifiable information stored
- Public usernames only
- No email addresses or IP addresses in reports

## Monitoring & Logging

### Log Levels

- **DEBUG**: Query details, batch numbers, detailed flow
- **INFO**: Progress updates, completion milestones
- **WARNING**: Skipped items (bots, IPs), recoverable errors
- **ERROR**: Database errors, connection failures, critical issues

### Key Metrics

- Total languages processed
- Total articles analyzed
- Total editors found
- Processing time per language
- Database query count
- Error count by type

## Deployment

### Prerequisites

- Python 3.9+
- Access to Wikimedia Toolforge
- `~/replica.my.cnf` configured
- Required packages installed

### Installation

```bash
git clone https://github.com/user/wikipedia-medicine.git
cd wikipedia-medicine
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Execution

```bash
# Full analysis
python -m src.main

# Specific languages
python -m src.main --languages es,fr,de

# Custom year
python -m src.main --year 2023
```

## Maintenance

### Regular Updates

- Update year parameters in config.py
- Review and update database mappings
- Check for API/schema changes
- Update dependencies

### Monitoring

- Check log files for errors
- Verify output file integrity
- Monitor query performance
- Review coverage reports

## Architecture Decisions

### Why Modular Design?

- **Testability**: Each module can be tested independently
- **Maintainability**: Changes isolated to specific modules
- **Reusability**: Components can be used in other projects
- **Clarity**: Clear separation of concerns

### Why Context Managers for Databases?

- **Reliability**: Ensures connections always closed
- **Simplicity**: Clean syntax with `with` statements
- **Error Handling**: Automatic cleanup on exceptions

### Why Batch Processing?

- **Prevent Timeouts**: Large queries can timeout
- **Memory Efficiency**: Don't load all data at once
- **Connection Limits**: Respect database connection limits

### Why WikiText Output?

- **Native Format**: Directly usable on Wikipedia
- **Sortable Tables**: Interactive sorting in wiki
- **Interwiki Links**: Direct links to user pages

---

*This architecture document should be updated as the project evolves.*
