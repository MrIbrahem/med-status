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
