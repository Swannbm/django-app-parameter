# Documentation Guidelines

**Audience**: Senior developers. Straight to the point. Less is more.

## Core Principles

### 1. No code duplication
Reference files, don't copy them.

```markdown
# ❌ Bad
[50 lines of pytest config copied from pyproject.toml]

# ✅ Good
Config: [pyproject.toml](../pyproject.toml) (`[tool.pytest.ini_options]`)
```

### 2. Code is documentation
Don't explain what code already shows.

```markdown
# ❌ Bad
19 individual test descriptions with code snippets

# ✅ Good
19 tests across 5 categories. See [tests/test_django_app_parameter.py](../tests/test_django_app_parameter.py)
```

### 3. Single path
Project uses Poetry → document Poetry only. No alternatives.

### 4. Trust the reader
Assume senior developer knowledge. No basic explanations (git, pyenv, virtualenv, etc.).

## Specific Rules

### Testing docs
- ✅ How to run
- ✅ Coverage number
- ❌ No code duplication
- ❌ No individual test descriptions

### Configuration docs
- ✅ File references only
- ✅ Essential commands only
- ❌ No content duplication
- ❌ No syntax explanations (TOML/YAML/etc.)

### Tooling
- ✅ Poetry via `poetry run <command>`
- ✅ Makefile for **complex multi-step commands only** (`make check`, `make clean`)
- ❌ No pip/virtualenv/conda alternatives
- ❌ No Poetry/pyenv installation guides
- ❌ No `poetry shell` (unavailable in Poetry 2.0+)
- ❌ No Makefile aliases for single commands

### Makefile guidelines

```makefile
# ✅ Good: Multi-step with feedback
check:
	@echo "Running ruff..."
	poetry run ruff check django_app_parameter/
	@echo "Running pyright..."
	poetry run pyright
	@echo "Running tests..."
	poetry run pytest --cov=django_app_parameter --cov-fail-under=100

# ✅ Good: Complex logic
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# ❌ Bad: Single command alias
test:
	poetry run pytest
```

Use direct commands (`poetry run pytest`) over aliases (`make test`).

## Documentation Structure

Keep it minimal. Example for testing docs:

```markdown
# Testing

- Coverage: 100%
- Run: `poetry run pytest`
- Full check: `make check`
- Source: [tests/test_django_app_parameter.py](../tests/test_django_app_parameter.py)
- Config: [pyproject.toml](../pyproject.toml) (`[tool.pytest.ini_options]`)
```

## Writing Style

### Good references
✅ `Config: [pyproject.toml](../pyproject.toml) (\`[tool.pytest.ini_options]\`)`
✅ `See [tests/settings.py](../tests/settings.py)`

### Commands
Use inline comments for options:

```bash
pytest              # All tests
pytest -v           # Verbose
pytest --cov        # With coverage
```

### No redundancy between chapters
If installation.md covers setup, don't repeat in usage-guide.md or README.md.

## Optional Fields

Mark with bullets:
- `description` (optional)
- `is_global` (optional, default: false)

No need for lengthy explanations.

## Examples

One concrete example per concept. Maximum.

## Pre-publish Checklist

- [ ] No code duplication
- [ ] No basic prerequisite explanations
- [ ] File references only
- [ ] No cross-chapter redundancy
- [ ] Concise examples (1 max per concept)
- [ ] Optional fields marked with bullets

## Golden Rule

> **Less is more.** Reference, don't duplicate. Trust senior developers.
