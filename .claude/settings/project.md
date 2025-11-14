# Project Configuration

## Documentation Standards

**Target Audience**: Senior developers with deep Django/Python expertise.

**Writing Philosophy**: Straight to the point. Less is more.

### Core Rules

1. **No code duplication** - Reference files, never copy code
2. **Code is documentation** - Don't explain what code already shows
3. **Single path** - Document Poetry only, no alternatives (pip/conda/virtualenv)
4. **Trust the reader** - Assume senior developer knowledge, skip basic explanations

### Documentation Requirements

- **Examples**: Maximum 1 concrete example per concept
- **Optional fields**: Mark with bullets only, no lengthy explanations
- **Redundancy**: Zero tolerance between chapters - each piece of info lives in ONE place only
- **Language**: English only

### What NOT to Document

- ❌ Basic prerequisite setup (git, pyenv, virtualenv)
- ❌ Alternative tools (pip, conda)
- ❌ Tool installation guides (Poetry, pyenv)
- ❌ Syntax explanations (TOML, YAML, JSON)
- ❌ Individual test descriptions
- ❌ Code snippets already in source files

### What TO Document

- ✅ How to run commands
- ✅ Coverage numbers
- ✅ File references with links
- ✅ Essential commands only

### Writing Style

**Good**:
```markdown
Config: [pyproject.toml](../pyproject.toml) (`[tool.pytest.ini_options]`)
```

**Bad**:
```markdown
The pytest configuration can be found in the pyproject.toml file,
which contains the following settings...
[50 lines of copied config]
```

See [.claude/documentation-guidelines.md](.claude/documentation-guidelines.md) for complete guidelines.

## Tooling Standards

- **Dependency management**: Poetry via `poetry run <command>`
- **Makefile**: Complex multi-step commands only (`make check`, `make clean`)
- **No simple aliases**: Use `poetry run pytest` directly, not `make test`

## Golden Rule

> **Less is more.** Reference, don't duplicate. Trust senior developers.
