# Database Schema Reference

## Overview

This document describes the Wikimedia database schema tables used by the Wikipedia Medicine project. All databases are accessed via read replicas at `*.analytics.db.svc.wikimedia.cloud`.

## Database Naming Convention

- **Pattern**: `{dbname}_p`
- **Examples**: `enwiki_p`, `eswiki_p`, `meta_p`
- **Host**: `{dbname}.analytics.db.svc.wikimedia.cloud`
- **Port**: 3306

## Key Databases

### 1. enwiki_p (English Wikipedia)

Main database for retrieving Medicine project articles and cross-language links.

### 2. meta_p (Meta Wiki)

Contains metadata about all Wikimedia projects, used for database mapping.

### 3. {lang}wiki_p (Language-specific Wikipedias)

Individual language Wikipedia databases for querying editor statistics.

---

## Table Schemas

### page

Stores article and page metadata.

```sql
CREATE TABLE page (
  page_id INT UNSIGNED NOT NULL PRIMARY KEY,
  page_namespace INT NOT NULL,
  page_title VARBINARY(255) NOT NULL,
  page_is_redirect TINYINT UNSIGNED NOT NULL DEFAULT 0,
  page_latest INT UNSIGNED NOT NULL,
  page_len INT UNSIGNED NOT NULL,
  -- other columns...
  KEY page_namespace_title (page_namespace, page_title)
);
```

**Key Columns:**
- `page_id`: Unique identifier for each page
- `page_namespace`: Namespace (0 = articles, 1 = talk pages, etc.)
- `page_title`: Page title (URL-encoded, underscores instead of spaces)
- `page_is_redirect`: 1 if redirect, 0 if regular page

**Usage in Project:**
- Filter by `page_namespace = 0` (main article namespace)
- Filter by `page_is_redirect = 0` (exclude redirects)
- Join with other tables on `page_id`

**Example Query:**
```sql
SELECT page_title, page_id 
FROM page 
WHERE page_namespace = 0 
  AND page_is_redirect = 0 
LIMIT 10;
```

---

### langlinks

Stores cross-wiki language links between articles.

```sql
CREATE TABLE langlinks (
  ll_from INT UNSIGNED NOT NULL,
  ll_lang VARBINARY(35) NOT NULL,
  ll_title VARBINARY(255) NOT NULL,
  PRIMARY KEY (ll_from, ll_lang),
  KEY ll_lang_title (ll_lang, ll_title)
);
```

**Key Columns:**
- `ll_from`: page_id of source article
- `ll_lang`: Target language code (e.g., 'es', 'fr', 'de')
- `ll_title`: Title in target language

**Usage in Project:**
- Join with `page` table on `ll_from = page_id`
- Extract titles for each language
- Build cross-language article mapping

**Example Query:**
```sql
SELECT page_title AS en_title, ll_lang, ll_title
FROM page
JOIN langlinks ON page_id = ll_from
WHERE page_namespace = 0
  AND page_is_redirect = 0
LIMIT 10;
```

---

### page_assessments

Stores article quality assessments.

```sql
CREATE TABLE page_assessments (
  pa_page_id INT UNSIGNED NOT NULL,
  pa_project_id INT UNSIGNED NOT NULL,
  pa_class VARCHAR(255),
  pa_importance VARCHAR(255),
  PRIMARY KEY (pa_page_id, pa_project_id),
  KEY pa_project_id (pa_project_id)
);
```

**Key Columns:**
- `pa_page_id`: Article page_id
- `pa_project_id`: WikiProject identifier
- `pa_class`: Quality class (FA, GA, B, Start, Stub, etc.)
- `pa_importance`: Importance rating (Top, High, Mid, Low)

**Usage in Project:**
- Filter articles by WikiProject membership
- Join with `page_assessments_projects` for project names

---

### page_assessments_projects

Stores WikiProject definitions.

```sql
CREATE TABLE page_assessments_projects (
  pap_project_id INT UNSIGNED NOT NULL PRIMARY KEY,
  pap_project_title VARCHAR(255) NOT NULL UNIQUE
);
```

**Key Columns:**
- `pap_project_id`: Unique project identifier
- `pap_project_title`: Project name (e.g., "Medicine", "طب")

**Usage in Project:**
- Filter by `pap_project_title = "Medicine"` (English)
- Filter by `pap_project_title = "طب"` (Arabic)
- Join with `page_assessments` on `pap_project_id = pa_project_id`

**Example Query:**
```sql
SELECT page_title
FROM page
JOIN page_assessments ON pa_page_id = page_id
JOIN page_assessments_projects ON pa_project_id = pap_project_id
WHERE pap_project_title = "Medicine"
  AND page_namespace = 0
LIMIT 10;
```

---

### revision

Stores all page revisions (edits).

```sql
CREATE TABLE revision (
  rev_id INT UNSIGNED NOT NULL PRIMARY KEY,
  rev_page INT UNSIGNED NOT NULL,
  rev_actor BIGINT UNSIGNED NOT NULL,
  rev_timestamp BINARY(14) NOT NULL,
  rev_minor_edit TINYINT UNSIGNED NOT NULL DEFAULT 0,
  rev_deleted TINYINT UNSIGNED NOT NULL DEFAULT 0,
  rev_len INT UNSIGNED,
  rev_parent_id INT UNSIGNED,
  KEY rev_page_timestamp (rev_page, rev_timestamp),
  KEY rev_actor_timestamp (rev_actor, rev_timestamp)
);
```

**Key Columns:**
- `rev_id`: Unique revision identifier
- `rev_page`: page_id of edited article
- `rev_actor`: actor_id of editor
- `rev_timestamp`: Timestamp (format: YYYYMMDDHHmmss)

**Usage in Project:**
- Count edits per editor
- Filter by year: `rev_timestamp LIKE '2024%'`
- Join with `page` on `rev_page = page_id`
- Join with `actor` on `rev_actor = actor_id`

**Example Query:**
```sql
SELECT COUNT(*) as edit_count
FROM revision
WHERE rev_page = 12345
  AND rev_timestamp LIKE '2024%';
```

---

### actor

Stores editor information (replacing old user table).

```sql
CREATE TABLE actor (
  actor_id BIGINT UNSIGNED NOT NULL PRIMARY KEY,
  actor_user INT UNSIGNED,
  actor_name VARBINARY(255) NOT NULL UNIQUE
);
```

**Key Columns:**
- `actor_id`: Unique actor identifier
- `actor_user`: User ID (NULL for IPs/external)
- `actor_name`: Username or IP address

**Usage in Project:**
- Join with `revision` on `actor_id = rev_actor`
- Filter bots: `LOWER(CAST(actor_name AS CHAR)) NOT LIKE '%bot%'`
- Identify IPs: actor_name matches IP pattern

**Example Query:**
```sql
SELECT actor_name, COUNT(*) as edits
FROM revision
JOIN actor ON rev_actor = actor_id
WHERE LOWER(CAST(actor_name AS CHAR)) NOT LIKE '%bot%'
GROUP BY actor_id;
```

---

### templatelinks

Stores transclusions of templates in pages.

```sql
CREATE TABLE templatelinks (
  tl_from INT UNSIGNED NOT NULL,
  tl_target_id BIGINT UNSIGNED NOT NULL,
  tl_from_namespace INT NOT NULL DEFAULT 0,
  PRIMARY KEY (tl_from, tl_target_id),
  KEY tl_target_id (tl_target_id, tl_from)
);
```

**Key Columns:**
- `tl_from`: page_id that transcludes the template
- `tl_target_id`: linktarget_id of transcluded template
- `tl_from_namespace`: Namespace of source page

**Usage in Project:**
- Find pages using {{WikiProject Medicine}} template
- Join with `linktarget` for template names
- Used specifically for English Wikipedia

---

### linktarget

Stores normalized link targets.

```sql
CREATE TABLE linktarget (
  lt_id BIGINT UNSIGNED NOT NULL PRIMARY KEY,
  lt_namespace INT NOT NULL,
  lt_title VARBINARY(255) NOT NULL,
  UNIQUE KEY lt_namespace_title (lt_namespace, lt_title)
);
```

**Key Columns:**
- `lt_id`: Unique link target identifier
- `lt_namespace`: Target namespace (10 = Template)
- `lt_title`: Target title

**Usage in Project:**
- Join with `templatelinks` on `lt_id = tl_target_id`
- Filter by `lt_namespace = 10` AND `lt_title = 'WikiProject_Medicine'`

---

### redirect

Stores page redirects.

```sql
CREATE TABLE redirect (
  rd_from INT UNSIGNED NOT NULL PRIMARY KEY,
  rd_namespace INT NOT NULL,
  rd_title VARBINARY(255) NOT NULL,
  rd_interwiki VARBINARY(32),
  rd_fragment VARBINARY(255),
  KEY rd_namespace_title (rd_namespace, rd_title)
);
```

**Key Columns:**
- `rd_from`: page_id of redirect page
- `rd_namespace`: Target namespace
- `rd_title`: Target title
- `rd_interwiki`: Interwiki prefix (empty for local)

**Usage in Project:**
- Used in English Wikipedia query to handle redirects
- LEFT JOIN to include pages even without redirects

---

### wiki (meta_p database)

Stores information about all Wikimedia wikis.

```sql
CREATE TABLE wiki (
  dbname VARCHAR(255) NOT NULL PRIMARY KEY,
  lang VARCHAR(255),
  family VARCHAR(255),
  url VARCHAR(255),
  is_closed TINYINT NOT NULL DEFAULT 0,
  -- other columns...
);
```

**Key Columns:**
- `dbname`: Database name (e.g., 'enwiki', 'eswiki')
- `lang`: Language code (e.g., 'en', 'es')
- `family`: Wiki family ('wikipedia', 'wiktionary', etc.)
- `url`: Full URL to the wiki
- `is_closed`: 1 if closed, 0 if active

**Usage in Project:**
- Map language codes to database names
- Filter by `family = 'wikipedia'` AND `is_closed = 0`
- Build connection strings

**Example Query:**
```sql
SELECT dbname, lang, url
FROM wiki
WHERE family = 'wikipedia'
  AND is_closed = 0
  AND lang IN ('es', 'fr', 'de');
```

---

## Query Patterns

### Pattern 1: Get Medicine Articles with Language Links

```sql
SELECT page_title, ll_lang, ll_title
FROM page
JOIN langlinks ON page_id = ll_from
JOIN page_assessments ON pa_page_id = page_id
JOIN page_assessments_projects ON pa_project_id = pap_project_id
WHERE pap_project_title = "Medicine"
  AND page_namespace = 0
  AND page_is_redirect = 0;
```

**Purpose**: Retrieve all Medicine project articles and their translations

**Returns**: English title, language code, translated title

---

### Pattern 2: Get Editor Statistics (Standard)

```sql
SELECT actor_name, COUNT(*) as count
FROM revision
JOIN actor ON rev_actor = actor_id
JOIN page ON rev_page = page_id
WHERE page_title IN ('Title1', 'Title2', ...)
  AND page_namespace = 0
  AND rev_timestamp LIKE '2024%'
  AND LOWER(CAST(actor_name AS CHAR)) NOT LIKE '%bot%'
GROUP BY actor_id
ORDER BY count DESC;
```

**Purpose**: Count edits per editor for specific articles in a given year

**Returns**: Editor name, edit count

**Notes**: 
- Batch titles (100 at a time)
- Escape titles with `pymysql.converters.escape_string()`

---

### Pattern 3: Get Editor Statistics (Arabic)

```sql
SELECT actor_name, COUNT(*) as count
FROM revision
JOIN actor ON rev_actor = actor_id
JOIN page ON rev_page = page_id
WHERE page_id IN (
    SELECT DISTINCT pa_page_id
    FROM page_assessments
    JOIN page_assessments_projects ON pa_project_id = pap_project_id
    WHERE pap_project_title = "طب"
  )
  AND page_namespace = 0
  AND rev_timestamp LIKE '2024%'
  AND LOWER(CAST(actor_name AS CHAR)) NOT LIKE '%bot%'
GROUP BY actor_id
ORDER BY count DESC
LIMIT 100;
```

**Purpose**: Get top 100 Medicine editors in Arabic Wikipedia

**Returns**: Editor name, edit count

**Notes**: Uses project assessment directly, no title filtering needed

---

### Pattern 4: Get Editor Statistics (English)

```sql
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
    WHERE page_namespace = 1  -- Talk pages
  )
  AND page_namespace = 0
  AND rev_timestamp LIKE '2025%'
  AND LOWER(CAST(actor_name AS CHAR)) NOT LIKE '%bot%'
GROUP BY actor_id
ORDER BY count DESC
LIMIT 100;
```

**Purpose**: Get top 100 Medicine editors in English Wikipedia

**Returns**: Editor name, edit count

**Notes**: Uses WikiProject Medicine templatelinks on talk pages

---

## Data Types & Encoding

### Text Fields
- **Encoding**: UTF-8 (use `charset='utf8mb4'` for connections)
- **Binary Fields**: VARBINARY (page_title, actor_name)
- **Storage**: URL-encoded with underscores

### Timestamps
- **Format**: BINARY(14) - YYYYMMDDHHmmss
- **Example**: '20240115120000' = 2024-01-15 12:00:00
- **Usage**: `rev_timestamp LIKE '2024%'` for year filtering

### Namespaces
- **0**: Main articles
- **1**: Talk pages
- **2**: User pages
- **3**: User talk pages
- **4**: Project pages
- **10**: Templates
- **Full list**: https://www.mediawiki.org/wiki/Manual:Namespace

---

## Indexes & Performance

### Important Indexes

**page table:**
- `PRIMARY KEY (page_id)`
- `KEY page_namespace_title (page_namespace, page_title)`

**revision table:**
- `PRIMARY KEY (rev_id)`
- `KEY rev_page_timestamp (rev_page, rev_timestamp)`
- `KEY rev_actor_timestamp (rev_actor, rev_timestamp)`

**langlinks table:**
- `PRIMARY KEY (ll_from, ll_lang)`
- `KEY ll_lang_title (ll_lang, ll_title)`

### Query Optimization Tips

1. **Use Indexed Columns**: Always filter on indexed columns first
2. **Limit Results**: Use LIMIT for development/testing
3. **Batch Processing**: Split large IN() lists into batches
4. **Avoid SELECT ***: Select only needed columns
5. **Use EXPLAIN**: Check query execution plans

---

## Common Pitfalls

### 1. Title Encoding

❌ **Wrong**: Using raw titles with spaces
```sql
WHERE page_title = 'Barack Obama'
```

✅ **Correct**: Using underscores
```sql
WHERE page_title = 'Barack_Obama'
```

### 2. Bot Filtering

❌ **Wrong**: Case-sensitive check
```sql
WHERE actor_name NOT LIKE '%bot%'
```

✅ **Correct**: Case-insensitive check
```sql
WHERE LOWER(CAST(actor_name AS CHAR)) NOT LIKE '%bot%'
```

### 3. SQL Injection

❌ **Wrong**: String concatenation
```sql
query = f"WHERE page_title = '{title}'"
```

✅ **Correct**: Proper escaping
```sql
escaped = pymysql.converters.escape_string(title)
query = f"WHERE page_title = '{escaped}'"
```

### 4. Year Filtering

❌ **Wrong**: Using date functions (slow)
```sql
WHERE YEAR(rev_timestamp) = 2024
```

✅ **Correct**: Using LIKE (fast)
```sql
WHERE rev_timestamp LIKE '2024%'
```

---

## Schema Changes & Maintenance

### Actor Migration
- Old: `user` table with `user_id`, `user_name`
- New: `actor` table with `actor_id`, `actor_name`
- Migration completed across all wikis

### Checking Schema
```sql
DESCRIBE table_name;
SHOW CREATE TABLE table_name;
SHOW INDEX FROM table_name;
```

### Table Sizes
Use `SHOW TABLE STATUS` to check table sizes and update times.

---

## References

- [MediaWiki Database Schema](https://www.mediawiki.org/wiki/Manual:Database_layout)
- [Toolforge Documentation](https://wikitech.wikimedia.org/wiki/Help:Toolforge)
- [WikiReplicas](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Database)

---

*Last updated: 2025-01-28*
