# .claude Directory

This directory contains configuration files, documentation, and best practices for working with Claude AI assistant on the Wikipedia Medicine project.

## 📁 Directory Structure

```
.claude/
├── README.md                      # This file
├── CLAUDE.md                      # Main guide for working with Claude
├── settings.json                  # Project configuration for Claude
├── prompts/
│   └── templates.md               # Reusable prompt templates
├── context/
│   ├── architecture.md            # Project architecture documentation
│   ├── database_schema.md         # Database schema reference
│   ├── conventions.md             # Coding standards and conventions
│   └── color_logging_guide.md     # Color logging implementation guide
└── examples/
    └── prompt_examples.md         # Examples of good vs bad prompts
```

## 🚀 Quick Start

### For Developers

1. **Read CLAUDE.md first** - Main guide for working with Claude on this project
2. **Review settings.json** - Understand project structure and conventions
3. **Check prompt templates** - Use templates for common tasks
4. **Reference context docs** - Architecture, database schema, conventions

### For Claude

When assisting with this project:

1. **Check settings.json** for project-specific configuration
2. **Reference context/** for technical details
3. **Follow conventions.md** for code style
4. **Use prompt templates** to guide user interactions

## 📚 File Descriptions

### CLAUDE.md

**Primary documentation for human-Claude collaboration**

Contains:
- Project overview and purpose
- Core principles for Claude assistance
- Code style and conventions to follow
- Testing requirements
- Common tasks and example prompts
- Project-specific context (database schema, workflow)
- Troubleshooting guide
- Effective communication guidelines

**When to read**: Before starting any work on the project

### settings.json

**Machine-readable project configuration**

Contains:
- Project metadata (name, version, language)
- Code style settings (Black, isort, flake8)
- Module descriptions and responsibilities
- Workflow steps
- Naming conventions
- Special cases (Arabic, English Wikipedia)
- Dependencies
- Claude preferences

**When to reference**: When Claude needs structured project information

### prompts/templates.md

**Reusable prompt templates for common tasks**

Templates for:
- Code review
- Debugging
- Refactoring
- Testing
- Feature implementation
- Performance optimization
- SQL query help
- Documentation updates
- Architecture decisions
- Error interpretation
- Integration help

**When to use**: Starting a conversation with Claude about a specific task

### context/architecture.md

**Detailed project architecture documentation**

Contains:
- Component diagram and data flow
- Module responsibilities and APIs
- Design patterns used
- Error handling strategy
- Performance considerations
- Testing strategy
- Security considerations
- Deployment information

**When to reference**: Understanding how components work together

### context/database_schema.md

**Wikimedia database schema reference**

Contains:
- Table schemas and relationships
- Column descriptions
- Query patterns
- Indexes and performance tips
- Common pitfalls
- Examples for each table

**When to reference**: Writing or debugging SQL queries

### context/conventions.md

**Coding standards and best practices**

Contains:
- Python style guide (PEP 8 + Black)
- Naming conventions
- Type hints requirements
- Docstring format (Google style)
- Error handling patterns
- Logging guidelines
- Testing standards
- Git commit message format
- Security best practices
- Performance tips

**When to reference**: Writing or reviewing code

### examples/prompt_examples.md

**Examples of effective vs ineffective prompts**

Contains:
- Good and bad prompt examples
- Analysis of what makes prompts effective
- Common scenarios (debugging, refactoring, testing)
- Key patterns to follow
- Template structure

**When to reference**: Learning how to ask Claude for help effectively

## 🎯 Usage Scenarios

### Scenario 1: Debugging a Database Connection Issue

1. **Read**: CLAUDE.md → "Troubleshooting Guide" section
2. **Check**: context/database_schema.md for connection details
3. **Use**: prompts/templates.md → "Debugging Template"
4. **Reference**: context/conventions.md → "Database Code" section

### Scenario 2: Adding a New Feature

1. **Read**: CLAUDE.md → "Adding Features" section
2. **Check**: context/architecture.md to understand where feature fits
3. **Use**: prompts/templates.md → "Feature Implementation Template"
4. **Follow**: context/conventions.md for code style

### Scenario 3: Writing Tests

1. **Read**: CLAUDE.md → "Testing Requirements"
2. **Check**: context/conventions.md → "Testing" section
3. **Use**: prompts/templates.md → "Testing Template"
4. **Reference**: examples/prompt_examples.md → Testing example

### Scenario 4: Optimizing a SQL Query

1. **Check**: context/database_schema.md for table structure and indexes
2. **Use**: prompts/templates.md → "SQL Query Help Template"
3. **Reference**: context/conventions.md → "Database Code" section
4. **Follow**: CLAUDE.md → "SQL Query Guidelines"

### Scenario 5: Understanding Project Structure

1. **Read**: settings.json for high-level overview
2. **Check**: context/architecture.md for detailed design
3. **Reference**: CLAUDE.md → "Project-Specific Context"

## 💡 Tips for Effective Collaboration

### For Developers

**Do:**
- ✅ Read CLAUDE.md before starting
- ✅ Use prompt templates for consistency
- ✅ Provide full context in questions
- ✅ Reference specific documentation
- ✅ Include error messages and code snippets
- ✅ Ask specific questions
- ✅ Follow up with clarifications

**Don't:**
- ❌ Paste entire files without context
- ❌ Ask vague questions ("fix this")
- ❌ Expect Claude to remember previous conversations
- ❌ Ignore project conventions
- ❌ Skip reading relevant documentation

### For Claude

**Do:**
- ✅ Reference settings.json for project config
- ✅ Follow conventions.md strictly
- ✅ Check database_schema.md for SQL queries
- ✅ Provide code examples following project style
- ✅ Explain reasoning and alternatives
- ✅ Remind about testing requirements
- ✅ Highlight potential security issues

**Don't:**
- ❌ Suggest code that violates conventions
- ❌ Ignore project-specific patterns
- ❌ Provide generic solutions without context
- ❌ Forget to mention error handling
- ❌ Skip type hints or docstrings

## 🔄 Maintenance

This directory should be updated when:

- **Architecture changes**: Update context/architecture.md
- **New conventions adopted**: Update context/conventions.md
- **Database schema changes**: Update context/database_schema.md
- **New common tasks emerge**: Add to prompts/templates.md
- **Project configuration changes**: Update settings.json
- **New patterns identified**: Update CLAUDE.md

### Update Frequency

- **Weekly**: Review and update if needed
- **After major changes**: Immediate update
- **Version releases**: Full review and update

## 📖 Reading Order for New Contributors

1. **Start**: README.md (this file) - Overview
2. **Read**: CLAUDE.md - How to work with Claude
3. **Skim**: settings.json - Project structure
4. **Reference as needed**:
   - context/architecture.md - When understanding design
   - context/database_schema.md - When writing queries
   - context/conventions.md - When writing code
   - prompts/templates.md - When asking for help
   - examples/prompt_examples.md - When learning to prompt

## 🔗 Related Documentation

- **Project root**: `README.md` - Project overview and usage
- **Contributing**: `CONTRIBUTING.md` - Contribution guidelines
- **Tests**: `pytest.ini` - Test configuration
- **CI/CD**: `.github/workflows/` - GitHub Actions

## 🆘 Getting Help

When stuck:

1. **Check relevant context docs** in this directory
2. **Use appropriate prompt template** from prompts/templates.md
3. **Look at examples** in examples/prompt_examples.md
4. **Ask specific questions** with full context
5. **Reference project conventions** in your questions

## 📝 Example Workflow

```
1. Developer has a question about SQL query optimization
   ↓
2. Opens .claude/prompts/templates.md
   ↓
3. Copies "SQL Query Help Template"
   ↓
4. Fills in template with:
   - Current query from their code
   - Error message or performance issue
   - Database context from .claude/context/database_schema.md
   - What they've tried
   ↓
5. Asks Claude using the filled template
   ↓
6. Claude responds with:
   - Reference to database_schema.md for index info
   - Optimized query following conventions.md
   - Explanation of changes
   - Performance considerations from architecture.md
   ↓
7. Developer implements solution
   ↓
8. Developer tests and verifies
```

## 🎓 Learning Resources

### For Understanding the Codebase

- Start with: context/architecture.md
- Then read: context/conventions.md
- Reference: context/database_schema.md (when needed)

### For Working with Claude

- Start with: CLAUDE.md
- Use: prompts/templates.md (for structured questions)
- Learn from: examples/prompt_examples.md

### For Contributing

- Read: context/conventions.md (coding standards)
- Check: CLAUDE.md (project-specific patterns)
- Use: prompts/templates.md (for code review requests)

## 🔐 Security Note

This directory contains project documentation and best practices. It does NOT contain:

- ❌ Credentials or API keys
- ❌ Sensitive data
- ❌ Private information
- ❌ Production secrets

All credentials should be in:
- `~/replica.my.cnf` (database credentials)
- `.env` (environment variables)
- `.gitignore`d files

## 🤝 Contributing to .claude/

When adding or updating documentation in this directory:

1. **Maintain consistency** with existing format
2. **Include examples** where helpful
3. **Keep it practical** and actionable
4. **Update the index** (this README) if adding new files
5. **Review for accuracy** with current codebase
6. **Test the guidance** by following it yourself

## 📊 Metrics

Good documentation in .claude/ leads to:

- ✅ Faster onboarding for new developers
- ✅ More consistent code quality
- ✅ Fewer repetitive questions
- ✅ Better Claude assistance
- ✅ Reduced debugging time
- ✅ Improved code review quality

Track effectiveness by monitoring:
- Time to first contribution (new developers)
- Code review comments about conventions
- Claude interaction quality
- Bug frequency related to conventions

## 🎯 Goals

This directory aims to:

1. **Reduce cognitive load** - One place for all project knowledge
2. **Improve consistency** - Clear standards and patterns
3. **Accelerate development** - Templates and examples
4. **Enhance collaboration** - Both human-human and human-AI
5. **Maintain quality** - Documented best practices

## 📅 Version History

- **v1.0.0** (2025-01-28) - Initial creation
  - CLAUDE.md: Comprehensive working guide
  - settings.json: Project configuration
  - context/: Architecture, schema, conventions
  - prompts/: Reusable templates
  - examples/: Good vs bad prompts

---

*This directory is living documentation. Keep it updated as the project evolves.*

**Last updated**: 2025-01-28  
**Maintained by**: Project Team  
**Questions?**: Open an issue or discussion
