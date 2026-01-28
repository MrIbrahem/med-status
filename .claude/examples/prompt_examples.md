# Examples: Good vs Bad Prompts

This document provides examples of effective and ineffective prompts when working with Claude on the Wikipedia Medicine project.

---

## Example 1: Debugging a Connection Error

### ❌ Bad Prompt

```
my code is broken fix it
```

**Problems:**
- No context about what's broken
- No error message
- No code shown
- No indication of what was attempted

### ✅ Good Prompt

``` ```
I'm getting a "max_user_connections exceeded" error when processing multiple 
languages in the main workflow. This happens after successfully processing 
about 5 languages.

Error message:
```
pymysql.err.OperationalError: (1040, 'Too many connections')
```

Current code in database.py:
```python
class Database:
    def __init__(self, host, database, port=3306):
        self.connection = pymysql.connect(
            host=host,
            database=database,
            port=port,
            read_default_file="~/replica.my.cnf"
        )
    
    def execute(self, query):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query)
        return cursor.fetchall()
```

I'm calling this from main.py like:
```python
for lang in languages:
    db = Database(f"{dbname}.analytics.db.svc.wikimedia.cloud", f"{dbname}_p")
    results = db.execute(query)
    # process results
```

I think the issue is that connections aren't being closed, but I'm not sure how 
to implement proper connection management. Can you help me refactor this to use 
context managers as recommended in the project conventions?
``` ```

**Why it's good:**
- Provides full error message
- Shows relevant code
- Explains when the error occurs
- States what they think the issue is
- Asks for specific solution (context managers)
- References project conventions

---

## Example 2: Implementing a New Feature

### ❌ Bad Prompt

```
add csv export
```

**Problems:**
- Unclear what needs CSV export
- No specifications
- No context about where it fits
- No details on format

### ✅ Good Prompt

``` ```
I need to add a feature to export editor statistics to CSV format in addition 
to the existing WikiText format.

Requirements:
- CSV should have columns: Rank, Username, EditCount, Wiki
- Should mirror the data in the global WikiText report
- Should be saved as reports/global_summary.csv
- Should use standard Python csv module
- Numbers should NOT have thousands separators in CSV (use raw integers)

Current code in reports.py:
```python
class ReportGenerator:
    def generate_global_report(self, all_editors: Dict[str, Dict[str, int]]) -> str:
        # Current implementation generates WikiText
        pass
```

Questions:
1. Should I add a new method `generate_global_csv()` or modify the existing one 
   to accept a format parameter?
2. Should this be a separate file or combined with WikiText in the same function?
3. Do I need to update main.py to call this, or should it be automatic?

Following project conventions:
- Type hints for all parameters
- Google-style docstrings
- Proper error handling
- Logging at INFO level

Can you help me design and implement this feature?
``` ```

**Why it's good:**
- Clear requirements
- Shows current code
- Asks specific design questions
- References project conventions
- Considers integration points

---

## Example 3: Code Review Request

### ❌ Bad Prompt

```
is this good?

[pastes 500 lines of code with no context]
```

**Problems:**
- No indication of what to look for
- Too much code at once
- No context about what it does
- No specific concerns

### ✅ Good Prompt

``` ```
Please review this implementation of the batch query processor in processor.py. 
I'm specifically concerned about:
1. Error handling completeness
2. SQL injection prevention
3. Memory efficiency with large result sets

Code to review:
```python
class EditorProcessor:
    def process_language(self, lang: str, titles: List[str], 
                        dbname: str, year: str) -> Dict[str, int]:
        """Process editor statistics for a language."""
        editors = {}
        
        # Batch titles to prevent query timeouts
        for batch in self._batch_titles(titles):
            # Escape titles for SQL
            escaped = [pymysql.converters.escape_string(t) for t in batch]
            titles_str = "', '".join(escaped)
            
            query = f"""
                SELECT actor_name, COUNT(*) as count
                FROM revision
                JOIN actor ON rev_actor = actor_id
                JOIN page ON rev_page = page_id
                WHERE page_title IN ('{titles_str}')
                  AND rev_timestamp LIKE '{year}%'
                  AND LOWER(CAST(actor_name AS CHAR)) NOT LIKE '%bot%'
                GROUP BY actor_id
            """
            
            try:
                with Database(f"{dbname}.analytics.db.svc.wikimedia.cloud", 
                            f"{dbname}_p") as db:
                    results = db.execute(query)
                    
                for row in results:
                    username = row['actor_name']
                    if not self._is_ip_address(username):
                        editors[username] = editors.get(username, 0) + row['count']
                        
            except pymysql.err.OperationalError as e:
                logger.error("Query failed for %s: %s", lang, e)
                continue
        
        return editors
```

Context:
- This is called once per language (60+ languages total)
- Each language can have 100-10,000 titles
- Batch size is currently 100 titles
- This is part of Step 3 in the workflow

Does this look correct? Any improvements you'd suggest?
``` ```

**Why it's good:**
- Specific concerns listed
- Reasonable amount of code
- Context provided (how it's used)
- Asks for suggestions
- Shows they've considered the issues

---

## Example 4: Understanding an Error

### ❌ Bad Prompt

```
what does this mean

UnicodeDecodeError: 'utf-8' codec can't decode byte 0x84
```

**Problems:**
- No context about what operation caused it
- No code shown
- No indication of what file/function
- No additional error details

### ✅ Good Prompt

``` ```
I'm getting a UnicodeDecodeError when writing WikiText reports to files.

Full error:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x84 in position 152: 
invalid start byte
```

Stack trace:
```
File "src/reports.py", line 45, in write_report
    f.write(content)
```

Code in reports.py:
```python
def write_report(self, filename: str, content: str) -> None:
    """Write report content to file."""
    filepath = os.path.join(self.output_dir, filename)
    with open(filepath, 'w') as f:  # Line 45
        f.write(content)
    logger.info("Report written: %s", filepath)
```

Context:
- This happens when writing reports for Russian Wikipedia (lang='ru')
- The content string contains Cyrillic characters
- Same code works fine for English and Spanish
- Python version: 3.11
- OS: Ubuntu 22.04

Questions:
1. Why does this only happen with certain languages?
2. How should I handle non-ASCII characters properly?
3. Do I need to specify encoding in the open() call?

I looked at the conventions document but couldn't find specific guidance on 
Unicode handling.
``` ```

**Why it's good:**
- Full error with stack trace
- Shows exact code where error occurs
- Provides context (which language)
- States what works and what doesn't
- Asks specific questions
- Shows they tried to find the answer first

---

## Example 5: Refactoring Request

### ❌ Bad Prompt

```
make this better

def process(x):
    # big function with lots of code
```

**Problems:**
- Unclear what "better" means
- No indication of current problems
- No refactoring goals
- Code not fully shown

### ✅ Good Prompt

``` ```
The main.py file has grown to over 400 lines and has multiple responsibilities. 
I'd like to refactor it to follow better separation of concerns.

Current structure:
```python
def main():
    # 1. Parse arguments (30 lines)
    # 2. Setup logging (20 lines)
    # 3. Create directories (15 lines)
    # 4. Step 1: Get titles (80 lines)
    # 5. Step 2: Get DB mapping (40 lines)
    # 6. Step 3: Process languages (150 lines)
    # 7. Step 4: Generate reports (50 lines)
    # 8. Error handling (20 lines)
```

Problems:
- Too many responsibilities in one function
- Hard to test individual steps
- Difficult to reuse components
- No clear module boundaries

Proposed refactoring:
1. Move CLI parsing to separate function
2. Move each workflow step to its own function
3. Maybe create a WorkflowOrchestrator class?

Requirements:
- Must maintain current behavior
- Must not break existing tests
- Should make testing easier
- Must follow project conventions

Questions:
1. Should I create a new module like workflow.py?
2. Is a class-based or function-based approach better here?
3. How should I handle the data passing between steps?

Can you suggest a good architecture and help me plan the refactoring?
``` ```

**Why it's good:**
- Explains current problems clearly
- Shows current structure
- Proposes specific ideas
- Lists requirements and constraints
- Asks for architectural guidance
- Considers testing implications

---

## Example 6: SQL Query Help

### ❌ Bad Prompt

```
my query doesn't work

SELECT * FROM page WHERE page_title IN (...)
```

**Problems:**
- Unclear what "doesn't work" means
- No context about database or expected results
- No error message
- Ellipsis instead of actual query

### ✅ Good Prompt

``` ```
I'm trying to optimize the editor statistics query for large title lists 
(5000+ titles), but it's timing out after 60 seconds.

Current query:
```sql
SELECT actor_name, COUNT(*) as count
FROM revision
JOIN actor ON rev_actor = actor_id
JOIN page ON rev_page = page_id
WHERE page_title IN ('Title_1', 'Title_2', ... 5000 more titles)
  AND page_namespace = 0
  AND rev_timestamp LIKE '2024%'
  AND LOWER(CAST(actor_name AS CHAR)) NOT LIKE '%bot%'
GROUP BY actor_id
ORDER BY count DESC
```

Database: eswiki_p (Spanish Wikipedia)
Timeout error: "Query execution exceeded 60 seconds"

Current approach:
- Batching titles into groups of 100
- Running 50 separate queries
- Taking ~5 minutes total per language

Questions:
1. Is there a better way to structure this query?
2. Should I be using different indexes?
3. Would using a temporary table help?
4. Is 100 the right batch size or should I adjust?

I checked EXPLAIN and see it's doing a full table scan on revision. The page 
table has an index on (page_namespace, page_title) which should be used.

Can you help optimize this query while maintaining the same results?
``` ```

**Why it's good:**
- Shows full query
- Describes the problem (timeout)
- Provides database context
- Shows what they've tried
- Includes EXPLAIN analysis
- Asks specific optimization questions

---

## Example 7: Testing Help

### ❌ Bad Prompt

```
write tests for my function
```

**Problems:**
- No function shown
- No indication of what to test
- No context about current tests
- No specific testing challenges mentioned

### ✅ Good Prompt

``` ```
I need help writing tests for the EditorProcessor.aggregate_editors() method. 
I'm struggling with how to mock the database results properly.

Function to test:
```python
def aggregate_editors(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Aggregate editor counts from query results.
    
    Args:
        results: List of dicts with 'actor_name' and 'count' keys
    
    Returns:
        Dict mapping usernames to total edit counts
    """
    editors = {}
    for row in results:
        username = row['actor_name']
        
        # Skip bots
        if self.is_bot(username):
            logger.warning("Skipped bot: %s", username)
            continue
        
        # Skip IPs
        if self.is_ip_address(username):
            logger.warning("Skipped IP: %s", username)
            continue
        
        # Aggregate counts
        editors[username] = editors.get(username, 0) + row['count']
    
    return editors
```

Test scenarios I need to cover:
1. Normal case: aggregate counts for multiple users
2. Bot filtering: ensure bots are excluded
3. IP filtering: ensure IPs are excluded
4. Duplicate users: ensure counts are summed correctly
5. Empty input: handle empty list gracefully

Current test attempt:
```python
@pytest.mark.unit
def test_aggregate_editors():
    processor = EditorProcessor()
    results = [
        {'actor_name': 'User1', 'count': 10},
        {'actor_name': 'User2', 'count': 5},
    ]
    
    aggregated = processor.aggregate_editors(results)
    
    assert aggregated == {'User1': 10, 'User2': 5}
```

Questions:
1. How do I test that bots are filtered without calling the actual is_bot() method?
2. Should I mock is_bot() and is_ip_address()?
3. How do I verify that warnings are logged?
4. Is there a better way to structure these tests?

Following pytest conventions from .claude/context/conventions.md
``` ```

**Why it's good:**
- Shows function to test
- Lists specific test scenarios
- Shows current test attempt
- Asks specific questions about mocking
- References project conventions
- Explains what they're struggling with

---

## Example 8: Architecture Decision

### ❌ Bad Prompt

```
should I use a class or functions?
```

**Problems:**
- No context about what needs to be implemented
- No pros/cons considered
- No indication of project requirements
- Too vague

### ✅ Good Prompt

``` ```
I need to decide on the architecture for the report generation component. 
Should I use a class-based or function-based approach?

Current implementation (function-based):
```python
def generate_language_report(lang: str, editors: Dict[str, int], 
                            output_dir: str) -> None:
    """Generate WikiText report for a language."""
    # Implementation...

def generate_global_report(all_editors: Dict[str, Dict[str, int]], 
                          output_dir: str) -> None:
    """Generate global summary report."""
    # Implementation...

def format_wikitable(data: List[Tuple], headers: List[str]) -> str:
    """Format data as WikiText table."""
    # Implementation...
```

Proposed alternative (class-based):
```python
class ReportGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        
    def generate_language_report(self, lang: str, 
                                editors: Dict[str, int]) -> None:
        """Generate WikiText report for a language."""
        # Implementation...
        
    def generate_global_report(self, 
                              all_editors: Dict[str, Dict[str, int]]) -> None:
        """Generate global summary report."""
        # Implementation...
```

Considerations:

Class approach pros:
- Encapsulates output_dir configuration
- Easier to add state (like formatting options)
- Could support multiple output formats (WikiText, CSV, HTML)
- Follows OOP patterns used in Database and EditorProcessor

Function approach pros:
- Simpler, less boilerplate
- No state to manage
- Easier to test in isolation
- More functional programming style

Project context:
- Database and EditorProcessor are classes
- Report generation has minimal state (just output directory)
- May want to add CSV/HTML export later
- Need to be testable with mocks

Questions:
1. Which approach better fits the existing architecture?
2. Does the potential for future formats justify a class?
3. Is there a hybrid approach that works better?

What would you recommend and why?
``` ```

**Why it's good:**
- Shows both options clearly
- Lists pros and cons
- Provides project context
- Considers future requirements
- Asks for recommendation with reasoning
- Shows they've thought through the decision

---

## Key Patterns in Good Prompts

### Always Include:

1. **Context**: What you're working on, where in the codebase
2. **Problem**: Specific issue or question
3. **Code**: Relevant snippets (not entire files)
4. **Error Messages**: Full error text and stack traces
5. **What You've Tried**: Show your attempts
6. **Specific Questions**: What exactly do you need help with

### Avoid:

1. **Vague requests**: "fix this", "make it better"
2. **Too much code**: Entire files when only a function is relevant
3. **No context**: Just code or error with no explanation
4. **No specifics**: "doesn't work" without details
5. **Expecting mind reading**: Assuming Claude knows your setup

### Structure Template:

```
1. Brief description of what you're trying to do
2. Show relevant code
3. Describe the problem (with error messages if applicable)
4. Explain what you've tried
5. Ask specific questions
6. Reference project conventions/docs if relevant
```

---

*These examples should help you craft effective prompts that get better results from Claude.*
