# Contributing Guide

Thank you for your interest in contributing to Django App Parameter!

## Prerequisites

- Python 3.10 or higher (3.10, 3.11, 3.12, or 3.13 recommended)
- Poetry
- Git

## Tested Versions

This project is tested against the following Python and Django versions:

| Python  | Django 4.2 LTS | Django 5.2 LTS |
|---------|----------------|----------------|
| 3.10    | ✅             | ✅             |
| 3.11    | ✅             | ✅             |
| 3.12    | ✅             | ✅             |
| 3.13    | ✅             | ✅             |

**Support Policy**:
- We support **LTS versions of Django only** (currently 4.2 and 5.2)
- We support **Python versions that are not EOL** (currently 3.10+)
- When a version reaches EOL, it will be removed from our test matrix

**End of Life (EOL) dates**:
- Python 3.10: October 2026
- Python 3.11: October 2027
- Python 3.12: October 2028
- Python 3.13: October 2029
- Django 4.2 LTS: April 2026
- Django 5.2 LTS: April 2028

**Recently dropped support** (for reference):
- Python 3.9 (EOL: October 2025)
- Django 3.2 LTS (EOL: April 2024)
- Django 4.0 (EOL: April 2023)
- Django 4.1 (EOL: December 2023)

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
tox                       # All environments (8 Python/Django + 3 linters)
tox -e py310-django42     # Python 3.10 + Django 4.2 LTS
tox -e py313-django52     # Python 3.13 + Django 5.2 LTS
tox -e ruff               # Format and check with Ruff
tox -e pyright            # Type check with Pyright
tox -e coverage           # Check 100% coverage
```

**Available environments**:
- **Python/Django matrix**: `py{310,311,312,313}-django{42,52}` (8 combinations)
- **Quality checks**: `ruff`, `pyright`, `coverage`
- **Development**: `dev`

**Total**: 11 test environments covering all supported Python and Django LTS versions

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

## Manual Testing with Demo Project

The `demo_project/` directory contains a complete Django application for manual testing of `django-app-parameter`. This is useful for:
- Testing new features interactively
- Reproducing bugs in a real Django environment
- Validating admin interface changes
- Testing parameter access in templates and views

### Quick Start

From the root of the repository:

```bash
./demo_project/run_demo.sh
```

This will automatically set up a fresh database and start the development server at http://127.0.0.1:8000/.

### Important Notes

**Fresh Setup Every Time**: The demo project is designed to be recreated from scratch each time:
- The setup script (`setup_demo.sh`) removes the old database
- A new SQLite database is created with migrations
- A superuser is created (username: `admin`, password: `admin`)
- Sample parameters are loaded from fixtures

**Testing Workflow**:
1. Make changes to the `django_app_parameter/` source code
2. Run `./demo_project/run_demo.sh` to test your changes
3. The demo loads your local version of the package (not the installed one)
4. Test features via:
   - Homepage: http://127.0.0.1:8000/ (global parameters in templates)
   - Admin: http://127.0.0.1:8000/admin/ (CRUD operations)
   - Django shell: `python manage.py shell` (programmatic access)

**Fixtures**: Sample parameters are in [demo_project/fixtures/sample_parameters.json](demo_project/fixtures/sample_parameters.json). You can modify this file to test different parameter configurations.

For more details, see [demo_project/README.md](demo_project/README.md).

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
