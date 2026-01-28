# Prompt Templates for Common Tasks

## Code Review Template

```
Please review this code from [MODULE_NAME]:

[PASTE CODE HERE]

Review for:
1. Code style compliance (Black, isort, flake8)
2. Error handling completeness
3. SQL injection prevention
4. Connection management (proper use of context managers)
5. Logging completeness
6. Test coverage implications
7. Performance considerations
8. Documentation quality

Current context:
- This code is part of [WORKFLOW_STEP]
- It interacts with [DATABASE/MODULE]
- Expected input: [DESCRIBE]
- Expected output: [DESCRIBE]

Specific concerns:
- [YOUR CONCERN 1]
- [YOUR CONCERN 2]
```

---

## Debugging Template

```
I'm encountering [ERROR_TYPE] in [MODULE_NAME].

Error message:
```
[PASTE FULL ERROR MESSAGE AND STACK TRACE]
```

Context:
- When it occurs: [DESCRIBE SCENARIO]
- What I was trying to do: [DESCRIBE TASK]
- What I expected: [EXPECTED BEHAVIOR]
- What actually happened: [ACTUAL BEHAVIOR]

Current code:
```python
[PASTE RELEVANT CODE]
```

What I've tried:
1. [ATTEMPT 1 - RESULT]
2. [ATTEMPT 2 - RESULT]

Database/environment info:
- Database: [DATABASE_NAME]
- Connection: [HOST:PORT]
- Python version: [VERSION]
- PyMySQL version: [VERSION]

Please help me:
1. Understand why this error is occurring
2. Suggest a fix that follows project conventions
3. Recommend how to prevent this in the future
```

---

## Refactoring Template

```
I need to refactor [MODULE/FUNCTION] because:
- [REASON 1: e.g., too long, complex, duplicate code]
- [REASON 2: e.g., hard to test, unclear responsibilities]

Current code:
```python
[PASTE CODE TO REFACTOR]
```

Current behavior:
- Input: [DESCRIBE]
- Output: [DESCRIBE]
- Side effects: [DESCRIBE]

Requirements:
- Must maintain current behavior
- Must follow project conventions (see .claude/settings.json)
- Must improve [TESTABILITY/READABILITY/PERFORMANCE]
- Must not break existing tests

Please suggest:
1. How to restructure this code
2. What new functions/classes to create
3. How to maintain backward compatibility
4. What tests need updating
```

---

## Testing Template

```
I need help writing tests for [MODULE/FUNCTION].

Code to test:
```python
[PASTE CODE]
```

Current test coverage:
- Existing tests: [DESCRIBE OR "None"]
- Coverage %: [NUMBER]

I need tests for:
1. [SCENARIO 1: e.g., happy path with valid input]
2. [SCENARIO 2: e.g., error handling for invalid input]
3. [SCENARIO 3: e.g., edge cases like empty lists]
4. [SCENARIO 4: e.g., database connection failures]

Test requirements:
- Use pytest framework
- Mock database connections (use pytest-mock)
- Use appropriate markers (@pytest.mark.unit, etc.)
- Follow existing test patterns in tests/[unit|integration]/
- Aim for >80% coverage

Specific challenges:
- [CHALLENGE 1: e.g., how to mock the database context manager]
- [CHALLENGE 2: e.g., how to test batch processing]

Please provide:
1. Test file structure
2. Test cases with assertions
3. Fixtures if needed
4. Mocking strategy
```

---

## Feature Implementation Template

```
I want to add a new feature: [FEATURE_NAME]

Description:
[DETAILED DESCRIPTION OF FEATURE]

Use case:
[WHY THIS FEATURE IS NEEDED]

Requirements:
- Input: [DESCRIBE]
- Output: [DESCRIBE]
- Performance: [CONSTRAINTS]
- Integration: [WHERE IT FITS IN WORKFLOW]

Current architecture:
- Related modules: [LIST MODULES]
- Workflow step: [STEP NUMBER OR "new step"]
- Database impact: [YES/NO, WHICH TABLES]

Please help me:
1. Determine where this fits in the architecture
2. Design the function/class signatures
3. Identify what needs to be modified
4. Write the implementation following project conventions
5. Suggest tests to write
6. Identify documentation to update

Constraints:
- Must follow conventions in .claude/settings.json
- Must not break existing functionality
- Must include logging
- Must handle errors gracefully
```

---

## Performance Optimization Template

```
I need to optimize [FUNCTION/QUERY] because [REASON: slow, memory intensive, etc.]

Current implementation:
```python
[PASTE CODE]
```

Performance metrics:
- Current execution time: [TIME]
- Memory usage: [MEMORY]
- Database query count: [COUNT]
- Batch size: [SIZE]

Bottleneck analysis:
- [IDENTIFY SLOW PARTS]

Requirements:
- Must maintain correctness
- Target execution time: [TIME]
- Target memory usage: [MEMORY]
- Cannot change database schema

Please suggest:
1. Optimization strategies
2. Algorithm improvements
3. Query optimizations
4. Caching opportunities
5. Batch processing improvements

Constraints:
- Read-only database access
- Connection limit: 5
- Must handle large datasets (100K+ records)
```

---

## SQL Query Help Template

```
I need help with a SQL query for [PURPOSE].

Current query:
```sql
[PASTE QUERY]
```

Database: [DATABASE_NAME]
Tables involved:
- [TABLE1]: [DESCRIPTION]
- [TABLE2]: [DESCRIPTION]

Current issue:
- [DESCRIBE PROBLEM: slow, incorrect results, syntax error, etc.]

Requirements:
- Return: [DESCRIBE EXPECTED OUTPUT]
- Filter by: [CRITERIA]
- Join on: [RELATIONSHIPS]
- Performance: [CONSTRAINTS]

Sample data:
[IF AVAILABLE, PASTE SAMPLE]

Please help me:
1. Fix/optimize the query
2. Explain the query logic
3. Add appropriate comments
4. Ensure proper indexing is considered
5. Handle edge cases

Special considerations:
- Read replica only (no writes)
- Large result sets expected
- Need to batch if possible
```

---

## Documentation Update Template

```
I need to update documentation for [CHANGE_TYPE: new feature, bug fix, refactor]

Changes made:
1. [CHANGE 1]
2. [CHANGE 2]

Files modified:
- [FILE 1]
- [FILE 2]

Documentation to update:
- [ ] README.md
- [ ] CHANGELOG.md
- [ ] Docstrings
- [ ] .claude/CLAUDE.md
- [ ] Other: [SPECIFY]

Please help me:
1. Write clear documentation for the changes
2. Update examples if needed
3. Ensure consistency with existing docs
4. Identify what else needs updating

Target audience:
- [DEVELOPERS/USERS/BOTH]

Style:
- Follow existing documentation patterns
- Include code examples where helpful
- Be concise but complete
```

---

## Architecture Decision Template

```
I need to make an architecture decision about [TOPIC].

Context:
[DESCRIBE CURRENT SITUATION]

Problem:
[WHAT NEEDS TO BE DECIDED]

Options:
1. [OPTION 1]
   - Pros: [LIST]
   - Cons: [LIST]

2. [OPTION 2]
   - Pros: [LIST]
   - Cons: [LIST]

3. [OPTION 3]
   - Pros: [LIST]
   - Cons: [LIST]

Constraints:
- [CONSTRAINT 1: e.g., must work with current architecture]
- [CONSTRAINT 2: e.g., cannot require new dependencies]

Project priorities:
- Maintainability
- Performance
- Testability
- [OTHER]

Please help me:
1. Evaluate each option
2. Recommend the best approach
3. Identify potential issues
4. Suggest implementation strategy

Consider:
- Current project structure (.claude/settings.json)
- Existing conventions
- Long-term maintenance
- Impact on other modules
```

---

## Error Message Interpretation Template

```
I'm getting an error message I don't understand:

```
[PASTE FULL ERROR]
```

Context:
- File: [FILE_NAME]
- Function: [FUNCTION_NAME]
- Line: [LINE_NUMBER]

Code around error:
```python
[PASTE CODE]
```

What I was doing:
[DESCRIBE ACTION]

Please explain:
1. What this error means
2. What likely caused it
3. How to fix it
4. How to prevent it in the future

Additional context:
- [ANY OTHER RELEVANT INFO]
```

---

## Integration Help Template

```
I need to integrate [NEW_COMPONENT] with [EXISTING_COMPONENT].

New component:
[DESCRIBE NEW CODE]

Existing component:
[DESCRIBE EXISTING CODE]

Integration points:
- [POINT 1]
- [POINT 2]

Requirements:
- Must maintain existing functionality
- Must follow project patterns
- Must be testable
- Must handle errors gracefully

Challenges:
- [CHALLENGE 1]
- [CHALLENGE 2]

Please help me:
1. Design the integration
2. Identify what needs modification
3. Suggest interface/API design
4. Provide implementation guidance
5. Recommend testing strategy

Reference:
- See .claude/context/architecture.md for current structure
```

---

## Quick Question Template

```
Quick question about [TOPIC]:

[YOUR QUESTION]

Context: [BRIEF CONTEXT IF NEEDED]

This relates to: [MODULE/FILE]
```

---

## Best Practices Check Template

```
I want to verify my code follows best practices:

```python
[PASTE CODE]
```

Check against:
- [ ] PEP 8 / Black formatting
- [ ] Type hints
- [ ] Docstrings
- [ ] Error handling
- [ ] Logging
- [ ] SQL injection prevention
- [ ] Connection management
- [ ] Performance
- [ ] Testability
- [ ] Security

Project-specific:
- [ ] Follows .claude/settings.json conventions
- [ ] Uses appropriate batch size
- [ ] Proper use of context managers
- [ ] Filters bots and IPs

Please:
1. Identify any issues
2. Suggest improvements
3. Confirm compliance with project standards
```

---

## Usage Notes

1. **Copy the appropriate template** when starting a conversation with Claude
2. **Fill in all bracketed placeholders** [LIKE_THIS]
3. **Remove irrelevant sections** if not applicable
4. **Add context** specific to your situation
5. **Be specific** about what help you need
6. **Include code/errors** when relevant

These templates ensure Claude has the context needed to provide targeted, project-specific assistance.
