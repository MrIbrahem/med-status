# Wikipedia Medicine Project - Editor Analysis

[![Tests](https://github.com/MrIbrahem/med-status/actions/workflows/pytest.yml/badge.svg)](https://github.com/MrIbrahem/med-status/actions/workflows/pytest.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

A Python application to retrieve and analyze editor contributions across Wikipedia's Medicine projects in multiple languages.

## Features

- 🌍 Multi-language support for Wikipedia projects
- 📊 Editor statistics aggregation and analysis
- 📝 WikiText report generation
- 🔄 Batch processing for large datasets
- 🔐 Secure database connections via Toolforge
- 📈 Comprehensive logging and error handling

## Prerequisites

- Python 3.9 or higher
- Access to Wikimedia Toolforge
- `~/replica.my.cnf` credential file configured

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/MrIbrahem/med-status.git
cd med-status
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure credentials

Ensure your `~/replica.my.cnf` file exists with the following format:

```ini
[client]
user=your_username
password=your_password
```

## Usage

### Basic Usage

Run the complete analysis:

```bash
python start.py
```

### Advanced Options

```bash
# Process specific languages only
python start.py --languages es,fr,de

# Set custom year
python start.py --year 2024

# Skip title retrieval (use existing data)
python start.py --skip-titles

# Generate reports only
python start.py --reports-only

# Enable debug logging
python start.py --log-level DEBUG
```

## Project Structure

```
med-status/
├── start.py                 # Entry point
├── src/
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── database.py      # Database connection management
│   │   ├── processor.py     # Data processing logic
│   │   ├── queries.py       # SQL query templates
│   │   └── reports.py       # Report generation
│   ├── workflow/
│   │   ├── __init__.py
│   │   ├── step1_retrieve_titles.py
│   │   ├── step2_process_languages.py
│   │   └── step3_generate_reports.py
│   ├── config.py            # Configuration
│   └── utils.py             # Helper functions
├── tests/
│   ├── unit/
│   │   ├── test_database.py
│   │   ├── test_processor.py
│   │   └── test_utils.py
│   └── integration/
│       ├── test_queries.py
│       └── test_workflow.py
├── languages/               # Article titles per language
├── editors/                 # Editor statistics per language
├── reports/                 # Generated WikiText reports
├── .github/
│   └── workflows/
│       ├── pytest.yml
│       └── lint.yml
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── LICENSE
└── .gitignore
```

## Output Files

### 1. Language Data (`languages/{lang}.json`)

```json
{
  "Article_Title_1": "Article Title 1",
  "Article_Title_2": "Article Title 2"
}
```

### 2. Editor Statistics (`editors/{lang}.json`)

```json
{
  "Username1": 1234,
  "Username2": 856,
  "Username3": 421
}
```

### 3. Per-Language Reports (`reports/{lang}.wiki`)

```wikitext
{| class="sortable wikitable"
!#
!User
!Count
|-
!1
|[[:w:es:user:Username1|Username1]]
|1,234
|-
!2
|[[:w:es:user:Username2|Username2]]
|856
|}
```

### 4. Global Summary Report (`reports/total_report.wiki`)

```wikitext
{| class="sortable wikitable"
!#
!User
!Count
!Wiki
|-
!1
|[[:w:es:user:Username1|Username1]]
|1,234
|es
|}
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit -m unit

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_database.py -v
```

### Code Quality

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Lint code
flake8 src tests
pylint src

# Type checking
mypy src
```

### Pre-commit Hooks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

## Configuration

Edit `src/config.py` to customize:

- Target years for analysis
- Batch size for processing
- Output directories
- Database connection parameters
- Logging settings

```python
# Example config.py
LAST_YEAR = "2024"
BATCH_SIZE = 100
MAX_CONNECTIONS = 5
```

## Workflow

1. **Retrieve Medicine titles** from English Wikipedia
2. **Get database mappings** from meta_p
3. **Query editor statistics** for each language
4. **Generate per-language reports** in WikiText format
5. **Create global summary report** across all languages

## Troubleshooting

### Connection Errors

```
Error: max_user_connections exceeded
```

**Solution**: Use context managers (`with` statements) to ensure connections are properly closed.

### Query Timeouts

```
Error: Query execution timeout
```

**Solution**: Reduce batch size in `config.py` or increase timeout settings.

### Permission Denied

```
Error: Access denied for user
```

**Solution**: Verify `~/replica.my.cnf` credentials and permissions.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines

- Write tests for new features
- Follow PEP 8 style guidelines
- Update documentation as needed
- Ensure all tests pass before submitting PR

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Wikimedia Foundation for providing database access
- Wikipedia Medicine project contributors
- Toolforge infrastructure team

## Support

For issues and questions:

- Open an issue on [GitHub](https://github.com/MrIbrahem/med-status/issues)
- Contact the maintainers

## Roadmap

- [ ] Add command-line progress bars
- [ ] Export to CSV and HTML formats
- [ ] Generate visualization graphs
- [ ] Add editor activity timeline analysis
- [ ] Compare year-over-year trends
- [ ] Email notification on completion
- [ ] Web dashboard for results

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{wikipedia_medicine_2025,
  author = {Your Name},
  title = {Wikipedia Medicine Editor Analysis},
  year = {2025},
  url = {https://github.com/MrIbrahem/med-status}
}
```
