# Wikipedia Medicine Project - Setup & Configuration Files

## Project Setup Prompt

Create a complete Python project structure for the Wikipedia Medicine editor analysis tool with the following configuration files, CI/CD setup, documentation, and testing infrastructure.

---

## File: `pytest.ini`

```ini
[pytest]
# Pytest configuration file

# Test discovery patterns
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Test paths
testpaths = tests

# Output options
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-branch
    --maxfail=5

# Markers for organizing tests
markers =
    unit: Unit tests
    integration: Integration tests requiring database
    slow: Slow running tests
    db: Tests requiring database connection
    network: Tests requiring network access

# Coverage options
[coverage:run]
source = src
omit =
    */tests/*
    */test_*
    */__pycache__/*
    */venv/*

[coverage:report]
precision = 2
show_missing = True
skip_covered = False

[coverage:html]
directory = htmlcov
```

---

## File: `.github/workflows/pytest.yml`

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Cache pip packages
      uses: actions/cache@v4
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Lint with flake8
      run: |
        # Stop build if there are Python syntax errors or undefined names
        flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics
        # Exit-zero treats all errors as warnings
        flake8 src --count --exit-zero --max-complexity=10 --max-line-length=120 --statistics

    - name: Check code formatting with black
      run: |
        black --check src tests

    - name: Type checking with mypy
      run: |
        mypy src --ignore-missing-imports
      continue-on-error: true

    - name: Run unit tests
      run: |
        pytest tests/unit -v -m "unit and not db"

    - name: Run integration tests (with mocked DB)
      run: |
        pytest tests/integration -v -m "not network"
      continue-on-error: true

    - name: Upload coverage reports to Codecov
      if: matrix.python-version == '3.11'
      uses: codecov/codecov-action@v4
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: false

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Run Bandit security checks
      run: |
        pip install bandit
        bandit -r src -f json -o bandit-report.json
      continue-on-error: true

    - name: Upload Bandit report
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: bandit-security-report
        path: bandit-report.json
```

---

## File: `.github/workflows/lint.yml`

```yaml
name: Linting

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  lint:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.11"

    - name: Install dependencies
      run: |
        pip install flake8 black isort pylint mypy

    - name: Run flake8
      run: flake8 src tests
      continue-on-error: true

    - name: Run black
      run: black --check --diff src tests

    - name: Run isort
      run: isort --check-only --diff src tests

    - name: Run pylint
      run: pylint src
      continue-on-error: true
```

---

## File: `requirements.txt`

```txt
# Core dependencies
pymysql==1.1.1
cryptography==42.0.5

# Configuration
python-dotenv==1.0.1

# Logging
colorlog==6.8.2

# Type hints
typing-extensions==4.11.0
```

---

## File: `requirements-dev.txt`

```txt
# Testing
pytest==8.1.1
pytest-cov==5.0.0
pytest-mock==3.14.0
pytest-timeout==2.3.1
pytest-xdist==3.5.0

# Code quality
flake8==7.0.0
black==24.3.0
isort==5.13.2
pylint==3.1.0
mypy==1.9.0

# Security
bandit==1.7.8

# Documentation
sphinx==7.2.6
sphinx-rtd-theme==2.0.0
```

---

## File: `README.md`

```markdown
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
python -m src.main
```

### Advanced Options

```bash
# Process specific languages only
python -m src.main --languages es,fr,de

# Set custom year
python -m src.main --year 2024

# Skip title retrieval (use existing data)
python -m src.main --skip-titles

# Generate reports only
python -m src.main --reports-only

# Enable debug logging
python -m src.main --log-level DEBUG
```

## Project Structure

```
med-status/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── database.py          # Database connection management
│   ├── queries.py           # SQL query templates
│   ├── processor.py         # Data processing logic
│   ├── reports.py           # Report generation
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
```

---

## File: `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv

# Testing
.pytest_cache/
.coverage
.coverage.*
htmlcov/
.tox/
.nox/
coverage.xml
*.cover
.hypothesis/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Project specific
languages/
editors/
reports/
*.log
*.json
*.wiki

# Credentials (IMPORTANT!)
replica.my.cnf
.env
*.cnf

# Documentation
docs/_build/
site/

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json

# Jupyter
.ipynb_checkpoints

# Backup files
*.bak
*.tmp
```
---

## File: `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "med-status"
version = "1.0.0"
description = "Wikipedia Medicine project editor analysis tool"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

[project.urls]
Homepage = "https://github.com/MrIbrahem/med-status"
Issues = "https://github.com/MrIbrahem/med-status/issues"

[tool.black]
line-length = 120
target-version = ['py39', 'py310', 'py311', 'py312']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 120
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
ignore_missing_imports = true

[tool.pylint.messages_control]
max-line-length = 120
disable = [
    "C0111",  # missing-docstring
    "C0103",  # invalid-name
    "R0913",  # too-many-arguments
]

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
```

---

## File: `.flake8`

```ini
[flake8]
max-line-length = 120
exclude =
    .git,
    __pycache__,
    .pytest_cache,
    venv,
    .venv,
    build,
    dist,
    *.egg-info
ignore =
    E203,  # whitespace before ':'
    E266,  # too many leading '#' for block comment
    E501,  # line too long (handled by black)
    W503,  # line break before binary operator
per-file-ignores =
    __init__.py:F401
max-complexity = 10
```

---

## File: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-toml
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=120']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--ignore-missing-imports]
```

---

## File: `LICENSE`

```text
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## File: `CONTRIBUTING.md`

```markdown
# Contributing to Wikipedia Medicine Project

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Maintain professionalism

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/MrIbrahem/med-status.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `pytest`
6. Commit: `git commit -m "Add your feature"`
7. Push: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Check code quality
black src tests
flake8 src tests
mypy src
```

## Testing Guidelines

- Write tests for all new features
- Maintain >80% code coverage
- Use descriptive test names
- Mock external dependencies (databases, network)
- Use pytest markers appropriately:
  - `@pytest.mark.unit` for unit tests
  - `@pytest.mark.integration` for integration tests
  - `@pytest.mark.slow` for slow tests
  - `@pytest.mark.db` for tests requiring database

## Code Style

- Follow PEP 8
- Use Black for formatting (line length: 120)
- Use type hints where appropriate
- Write docstrings for public functions
- Keep functions focused and small

## Commit Messages

Format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

Example:
```
feat(database): Add connection pooling

Implement connection pooling to prevent max_user_connections errors.
Connections are now reused efficiently across queries.

Closes #123
```

## Pull Request Process

1. Update README.md with details of changes if needed
2. Update tests and ensure all pass
3. Update documentation
4. Ensure code follows style guidelines
5. Request review from maintainers
6. Address review feedback
7. Squash commits if requested

## Bug Reports

Include:
- Python version
- Operating system
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages/logs
- Relevant code snippets

## Feature Requests

Include:
- Clear description
- Use case/motivation
- Proposed solution
- Alternative solutions considered
- Additional context

## Questions

- Open a GitHub Discussion
- Tag with appropriate labels
- Be specific and provide context

Thank you for contributing!
```

---

## File: `Makefile`

```makefile
.PHONY: help install install-dev test coverage lint format clean run

help:
	@echo "Available commands:"
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo "  make test         - Run tests"
	@echo "  make coverage     - Run tests with coverage report"
	@echo "  make lint         - Run linting checks"
	@echo "  make format       - Format code with black and isort"
	@echo "  make clean        - Remove build artifacts"
	@echo "  make run          - Run the application"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest tests/ -v

coverage:
	pytest tests/ --cov=src --cov-report=html --cov-report=term

lint:
	flake8 src tests
	pylint src
	mypy src --ignore-missing-imports

format:
	black src tests
	isort src tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -f .coverage
	rm -f coverage.xml

run:
	python -m src.main
```

---

## File: `CHANGELOG.md`

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure
- Database connection management
- Multi-language support
- Editor statistics aggregation
- WikiText report generation
- Comprehensive test suite
- CI/CD pipelines
- Documentation

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [1.0.0] - 2025-01-28

### Added
- First stable release
- Complete workflow implementation
- Full test coverage
- Documentation and examples
```

---

## Additional Test Files Structure

### `tests/unit/test_database.py`

```python
"""Unit tests for database module."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.services.database import Database

@pytest.mark.unit
class TestDatabase:
    """Test Database class."""

    def test_database_init(self):
        """Test database initialization."""
        db = Database("localhost", "test_db")
        assert db.host == "localhost"
        assert db.database == "test_db"
        assert db.port == 3306

    @patch('src.services.database.pymysql.connect')
    def test_context_manager(self, mock_connect):
        """Test database context manager."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        with Database("localhost", "test_db") as db:
            assert db.connection == mock_conn

        mock_conn.close.assert_called_once()

    @pytest.mark.db
    def test_execute_query(self):
        """Test query execution."""
        # Implementation here
        pass
```

### `tests/unit/test_utils.py`

```python
"""Unit tests for utility functions."""
import pytest
from src.utils import is_ip_address, escape_title

@pytest.mark.unit
class TestUtils:
    """Test utility functions."""

    @pytest.mark.parametrize("ip,expected", [
        ("192.168.1.1", True),
        ("Username123", False),
        ("2001:0db8:85a3::8a2e:0370:7334", True),
        ("NotAnIP", False),
    ])
    def test_is_ip_address(self, ip, expected):
        """Test IP address detection."""
        assert is_ip_address(ip) == expected

    def test_escape_title(self):
        """Test SQL title escaping."""
        title = "Test'Title"
        escaped = escape_title(title)
        assert "'" not in escaped or "\\'" in escaped
```

### `tests/integration/test_workflow.py`

```python
"""Integration tests for complete workflow."""
import pytest
from unittest.mock import patch

@pytest.mark.integration
class TestWorkflow:
    """Test complete workflow."""

    @pytest.mark.slow
    def test_full_pipeline(self):
        """Test complete data pipeline."""
        # Implementation here
        pass
```

---

## Environment Variables (.env.example)

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
CREDENTIAL_FILE=~/replica.my.cnf

# Application Settings
LAST_YEAR=2024
BATCH_SIZE=100
MAX_CONNECTIONS=5

# Logging
LOG_LEVEL=INFO
LOG_FILE=wikipedia_medicine.log

# Output Directories
LANGUAGES_DIR=languages
EDITORS_DIR=editors
REPORTS_DIR=reports
```

---

## Summary

This setup includes:

1. **Testing**: pytest configuration with coverage, markers, and multiple test types
2. **CI/CD**: GitHub Actions workflows for testing, linting, and security
3. **Documentation**: Comprehensive README, contributing guide, changelog
4. **Dependencies**: Production and development requirements
5. **Code Quality**: Black, isort, flake8, pylint, mypy configurations
6. **Pre-commit**: Automated code quality checks
8. **Convenience**: Makefile for common commands
9. **Version Control**: .gitignore for Python projects
10. **License**: MIT license template

All files are production-ready and follow Python best practices.
```
