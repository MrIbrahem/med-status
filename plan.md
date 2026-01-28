# Wikipedia Medicine Project - Editor Analysis

## Project Overview
A Python application to retrieve and analyze editor contributions across Wikipedia's Medicine projects in multiple languages. The project queries Wikimedia databases, processes editor statistics, and generates formatted reports.

## Architecture

### Core Components

1. **Database Manager** (`database.py`)
   - `Database` class for connection management
   - Context manager support (`with` statement)
   - Connection pooling to prevent max connection errors
   - Uses `~/replica.my.cnf` for Toolforge credentials

2. **Query Builder** (`queries.py`)
   - SQL query templates
   - Language-specific query variations
   - Title escaping utilities

3. **Data Processor** (`processor.py`)
   - Editor statistics aggregation
   - IP address filtering
   - Data normalization

4. **Report Generator** (`reports.py`)
   - WikiText table formatting
   - Per-language reports
   - Global summary report

5. **Main Application** (`main.py`)
   - Orchestrates workflow
   - Logging configuration
   - Error handling

## Workflow

### Step 1: Retrieve Medicine Titles by Language

**Database**: `enwiki_p`  
**Host**: `enwiki.analytics.db.svc.wikimedia.cloud`

```sql
SELECT page_title, ll_lang, ll_title
FROM page, langlinks, page_assessments, page_assessments_projects
WHERE pap_project_title = "Medicine"
  AND pa_project_id = pap_project_id
  AND pa_page_id = page_id
  AND page_id = ll_from
  AND page_is_redirect = 0
  AND page_namespace = 0
```

**Processing**:
- Create dictionary: `titles = {"en": []}`
- Aggregate: `titles.setdefault(row["ll_lang"], []).append(row["ll_title"])`
- Log: Total languages found, articles per language

**Output**: `languages/{lang}.json`

### Step 2: Get Language Database Names

**Database**: `meta_p`  
**Host**: `meta.analytics.db.svc.wikimedia.cloud`

```sql
SELECT dbname, family, lang, url 
FROM wiki 
WHERE is_closed = 0 
  AND family = "wikipedia"
```

**Processing**:
- Create mapping: `lang -> dbname`
- Connection format:
  - Host: `{dbname}.analytics.db.svc.wikimedia.cloud`
  - Database: `{dbname}_p`
  - Port: 3306

### Step 3: Retrieve Editor Statistics

Process each language (except English and Arabic handle separately):

#### 3A. Standard Languages Query

```sql
SELECT actor_name, count(*) as count 
FROM revision
JOIN actor ON rev_actor = actor_id
JOIN page ON rev_page = page_id
WHERE lower(cast(actor_name as CHAR)) NOT LIKE '%bot%' 
  AND page_namespace = 0 
  AND rev_timestamp LIKE '{last_year}%'
  AND page_id IN (
    SELECT page_id
    FROM page
    WHERE page_title IN ({escaped_titles})
  )
GROUP BY actor_id
ORDER BY count(*) DESC
```

**Implementation Details**:
- Split titles into batches of 100
- Escape titles: `pymysql.converters.escape_string(title)`
- Aggregate: `editors[actor_name] += row["count"]`
- Filter: Skip if `actor_name` is IP address (regex: `^\d+\.\d+\.\d+\.\d+$` or IPv6 pattern)
- Year parameter: `{last_year}` = "2024" (or configurable)

#### 3B. Arabic Wikipedia (ar)

```sql
SELECT actor_name, count(*) as count 
FROM revision
JOIN actor ON rev_actor = actor_id
JOIN page ON rev_page = page_id
WHERE lower(cast(actor_name as CHAR)) NOT LIKE '%bot%' 
  AND page_namespace = 0 
  AND rev_timestamp LIKE '{last_year}%'
  AND page_id IN (
    SELECT DISTINCT pa_page_id
    FROM page_assessments, page_assessments_projects
    WHERE pa_project_id = pap_project_id
      AND pap_project_title = "طب"
  )
GROUP BY actor_id
ORDER BY count(*) DESC
LIMIT 100
```

#### 3C. English Wikipedia (en)

```sql
SELECT actor_name, count(*) 
FROM revision 
JOIN actor ON rev_actor = actor_id 
JOIN page ON rev_page = page_id
WHERE lower(cast(actor_name as CHAR)) NOT LIKE '%bot%' 
  AND page_namespace = 0 
  AND rev_timestamp LIKE '2025%'
  AND page_title IN (
    SELECT page_title 
    FROM (
      SELECT tl_from, rd_from
      FROM templatelinks
      LEFT JOIN redirect
        ON ((rd_from = tl_from) 
            AND rd_title = 'WikiProject_Medicine' 
            AND (rd_interwiki = '' OR rd_interwiki IS NULL) 
            AND rd_namespace = '10')
      INNER JOIN page
        ON ((tl_from = page_id))
      JOIN linktarget
        ON ((tl_target_id = lt_id))
      WHERE lt_namespace = '10' 
        AND lt_title = 'WikiProject_Medicine'
      ORDER BY tl_from
    ) temp_backlink_range 
    INNER JOIN page ON ((tl_from = page_id)) 
    WHERE page_namespace = '1'
  )
GROUP BY actor_id 
ORDER BY count(*) DESC 
LIMIT 100
```

**Output**: `editors/{lang}.json`

### Step 4: Generate Per-Language Reports

**Format**: WikiText table  
**Output**: `reports/{lang}.wiki`

```wikitext
{| class="sortable wikitable"
!#
!User
!Count
|-
!1
|[[:w:{lang}:user:{username}|{username}]]
|{count:,}
|-
!2
|[[:w:{lang}:user:{username2}|{username2}]]
|{count2:,}
|-
|}
```

**Formatting**:
- Numbers with thousands separator (e.g., `1,234`)
- Sorted by count (descending)
- Interwiki user links

### Step 5: Generate Global Summary Report

**Output**: `reports/total_report.wiki`

```wikitext
{| class="sortable wikitable"
!#
!User
!Count
!Wiki
|-
!1
|[[:w:{wiki}:user:{username}|{username}]]
|{count:,}
|{wiki}
|-
|}
```

**Processing**:
- Combine all editor data
- Sort by count (descending globally)
- Include wiki code for maximum contribution site
- Maintain interwiki links

## File Structure

```
project/
├── main.py                 # Entry point
├── database.py             # Database connection management
├── queries.py              # SQL query templates
├── processor.py            # Data processing logic
├── reports.py              # Report generation
├── config.py               # Configuration (years, paths, etc.)
├── utils.py                # Helper functions (IP detection, escaping)
├── requirements.txt        # Dependencies
├── languages/              # Article titles per language
│   ├── en.json
│   ├── es.json
│   └── ...
├── editors/                # Editor statistics per language
│   ├── en.json
│   ├── es.json
│   └── ...
└── reports/                # Generated reports
    ├── en.wiki
    ├── es.wiki
    ├── ...
    └── total_report.wiki
```

## Dependencies

```
pymysql>=1.1.0
python-dotenv>=1.0.0  # Optional for config
```

## Logging Strategy

Use Python's `logging` module with the following levels:

- **INFO**: Step completion, counts, progress
- **DEBUG**: Query details, batch processing
- **WARNING**: Skipped items (bots, IPs)
- **ERROR**: Database errors, connection issues

**Example Log Messages**:
```
INFO: Starting Step 1: Retrieving medicine titles from enwiki
INFO: Found 45,231 articles across 87 languages
INFO: Processing language: es (1,234 articles)
DEBUG: Executing query batch 1/13 (100 titles)
WARNING: Skipped IP address: 192.168.1.1
INFO: Language 'es' complete: 156 editors found
INFO: Saved editors/es.json
ERROR: Failed to connect to dewiki_p: Connection timeout
```

## Database Connection Management

```python
class Database:
    def __init__(self, host, database, port=3306):
        self.host = host
        self.database = database
        self.port = port
        self.connection = None
    
    def __enter__(self):
        # Read credentials from ~/replica.my.cnf
        # Establish connection
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close connection
        pass
    
    def execute(self, query, params=None):
        # Execute query with cursor
        pass
```

## Error Handling

1. **Connection Errors**: Retry with exponential backoff (max 3 attempts)
2. **Query Timeouts**: Log and skip problematic queries
3. **File I/O Errors**: Ensure directories exist, handle permissions
4. **Data Validation**: Check for empty results, malformed data

## Configuration Parameters

```python
# config.py
LAST_YEAR = "2024"
CURRENT_YEAR = "2025"
BATCH_SIZE = 100
MAX_CONNECTIONS = 5
OUTPUT_DIRS = {
    "languages": "languages",
    "editors": "editors", 
    "reports": "reports"
}
CREDENTIAL_FILE = "~/replica.my.cnf"
```

## Execution Flow

1. **Initialize**: Create output directories, configure logging
2. **Step 1**: Retrieve titles → `languages/*.json`
3. **Step 2**: Get database mapping from meta_p
4. **Step 3**: Process each language:
   - Connect to language-specific database
   - Execute queries (batched for standard languages)
   - Aggregate editor statistics
   - Save to `editors/{lang}.json`
5. **Step 4**: Generate per-language reports → `reports/{lang}.wiki`
6. **Step 5**: Generate global summary → `reports/total_report.wiki`
7. **Cleanup**: Close connections, log summary statistics

## Testing Considerations

- Test with subset of languages first
- Validate SQL escaping with special characters
- Test IP address detection (IPv4 and IPv6)
- Verify WikiText formatting
- Check connection pooling under load

## Performance Optimizations

1. **Batch Processing**: Process titles in chunks of 100
2. **Connection Reuse**: Use context managers, limit concurrent connections
3. **Parallel Processing**: Consider multiprocessing for independent languages
4. **Caching**: Cache database name mappings
5. **Query Optimization**: Use indexes, limit result sets

## Sample Command Line Interface

```bash
# Run full analysis
python main.py

# Process specific languages only
python main.py --languages es,fr,de

# Set custom year
python main.py --year 2023

# Skip title retrieval (use existing data)
python main.py --skip-titles

# Generate reports only
python main.py --reports-only
```

## Expected Output Example

**editors/es.json**:
```json
{
  "Usuario1": 1234,
  "Usuario2": 856,
  "Usuario3": 421
}
```

**reports/es.wiki**:
```wikitext
{| class="sortable wikitable"
!#
!User
!Count
|-
!1
|[[:w:es:user:Usuario1|Usuario1]]
|1,234
|-
!2
|[[:w:es:user:Usuario2|Usuario2]]
|856
|-
|}
```

## Notes

- All database queries use read replicas (`.analytics.db.svc.wikimedia.cloud`)
- Credentials managed via Toolforge standard `~/replica.my.cnf`
- Bot filtering: case-insensitive check for 'bot' in username
- IP filtering: regex patterns for IPv4 (`\d+\.\d+\.\d+\.\d+`) and IPv6
- Year timestamps: Use `LIKE '{year}%'` for flexibility
- Connection limits: Use `with` statements to ensure proper cleanup

## Future Enhancements

- Add command-line progress bars
- Export to additional formats (CSV, HTML)
- Generate visualization graphs
- Add editor activity timeline analysis
- Compare year-over-year trends
- Email notification on completion
