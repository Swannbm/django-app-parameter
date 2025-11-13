# Contributing Guide

Thank you for your interest in contributing to Django App Parameter!

## Prerequisites

- Python 3.10 or higher
- Poetry
- Git

## Development Environment Setup

See the [QUICK_START_DEV.md](QUICK_START_DEV.md) guide for initial setup and essential commands.

## Checklist Before Submitting a PR

- [ ] Code formatted and checked with Ruff (`poetry run ruff format` and `poetry run ruff check`)
- [ ] Code fully typed with type hints (`poetry run pyright django_app_parameter/`)
- [ ] All tests pass (`poetry run pytest`)
- [ ] Code coverage is 100% (`poetry run pytest --cov=django_app_parameter --cov-fail-under=100`)
- [ ] Tests pass with tox (at least one version, ideally all)
- [ ] Documentation is up to date
- [ ] CHANGELOG is updated
- [ ] Commit messages are clear

**Tip**: Run `make check` to automatically verify Ruff, Pyright, and tests.

### Use Tox for complete testing

Before submitting your PR, test with different versions of Python and Django using Tox.

Tox configuration is in [tox.ini](tox.ini).

```bash
tox                       # All environments
tox -e py310-django42     # Specific version
tox -e ruff               # Format and check with Ruff
tox -e pyright            # Type check with Pyright
tox -e coverage           # Check 100% coverage
```

**Available environments**: `py{37,38,39,310,311}-django{32,40,41,42}`, `ruff`, `pyright`, `coverage`, `dev`

## Code Standards

### Code Style

- **Formatting and linting**: Use Ruff with configured settings (88 characters per line)
- **Imports**: Ruff automatically organizes imports in order: stdlib, third-party packages, local imports
- **Type hints**: Add type annotations to improve verification with Pyright

### Tests

- **Coverage**: 100% code coverage is mandatory
- **Isolation**: Each test must be independent
- **Clarity**: Test names should describe what is being tested
- **Fixtures**: Use pytest fixtures for reusable test data

### Testing Configuration

Configuration is in [pyproject.toml](pyproject.toml):

**pytest** (`[tool.pytest.ini_options]`):
- Searches for tests in `tests/`
- Options: `--strict-markers`, `--verbose`, `--reuse-db`
- [tests/settings.py](tests/settings.py) configures:
  - SQLite in-memory database
  - Minimal Django applications
  - Context processor for tests

### Documentation

- **Docstrings**: Add docstrings for new functions/classes
- **README**: Update README if adding new features
- **CHANGELOG**: Add an entry in CHANGELOG.md

## Project Structure

```
django-app-parameter/
├── django_app_parameter/       # Source code
│   ├── __init__.py
│   ├── models.py              # Parameter model
│   ├── admin.py               # Admin interface
│   ├── apps.py
│   ├── context_processors.py  # Context processor for templates
│   ├── management/
│   │   └── commands/
│   │       └── load_param.py  # Management command
│   └── migrations/
├── tests/                      # Tests
│   ├── __init__.py
│   ├── settings.py            # Django configuration for tests
│   └── test_django_app_parameter.py
├── docs/                       # Documentation
├── pyproject.toml             # Poetry and tools configuration (Ruff, pytest, coverage, Pyright)
├── tox.ini                    # Tox configuration
├── Makefile                   # Complex commands shortcuts
├── README.md
├── CHANGELOG.md
└── CONTRIBUTING.md
```

## Types of Accepted Contributions

- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation improvements
- ✅ Test additions
- ♻️ Refactoring
- 🎨 Interface improvements (admin)

## Resources

- Test code: [tests/test_django_app_parameter.py](tests/test_django_app_parameter.py)
- [pytest documentation](https://docs.pytest.org/)
- [pytest-django documentation](https://pytest-django.readthedocs.io/)
- [coverage.py documentation](https://coverage.readthedocs.io/)
- [tox documentation](https://tox.wiki/)
- [Ruff documentation](https://docs.astral.sh/ruff/)
- [Pyright documentation](https://microsoft.github.io/pyright/)

## Questions?

If you have questions, feel free to:
- Open an issue on GitHub
- Consult the [documentation](docs/)
- Look at existing PRs for examples

## License

By contributing to this project, you agree that your contributions will be licensed under the CC0 1.0 Universal license.
