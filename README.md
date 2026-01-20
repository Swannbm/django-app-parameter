# Django-app-parameter

![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13%20|%203.14-yellow)
![Django](https://img.shields.io/badge/django-4.2%20LTS%20|%205.2%20LTS%20|%206.0-green)
![coverage](https://img.shields.io/badge/coverage-100%25-green)
![version](https://img.shields.io/badge/version-3.0.0-blue)
![ruff](https://img.shields.io/badge/code%20style-ruff-000000)
![pyright](https://img.shields.io/badge/type%20checker-pyright-2A6DB2)
![licence](https://img.shields.io/badge/licence-CC0%201.0%20Universal-purple)

Django-app-parameter lets you store application settings in the database and update them at runtime through Django admin - no deployment or restart needed. Perfect for things like site titles, email addresses, feature flags, or any configuration that business users should control.

## ⚠️ Migration from v2.x to v3.0

Version 3.0 introduces a simplified API. Type-specific methods have been replaced with unified `get()` and `set()`:

```python
# Before (v2.x)
value = param.int()
param.set_int(42)
title = Parameter.objects.str("BLOG_TITLE")

# After (v3.0)
value = param.get()
param.set(42)
param = Parameter.objects.get(slug="BLOG_TITLE")
title = param.get()
```

**New feature:** `auto_cast` parameter to convert string input to native type:

```python
param.set("42", auto_cast=True)  # Converts "42" to int for INT parameters
```

See [CHANGELOG.md](CHANGELOG.md) for full details.

📚 **[Full Documentation](https://django-app-parameter.readthedocs.io/)**

## Quick Start

### Installation

```bash
pip install django-app-parameter
```

For encryption support (optional):

```bash
pip install django-app-parameter[cryptography]
```

**Requirements:** Python 3.10+ • Django 4.2+

### Compatibility Matrix

| Python | Django 4.2 LTS | Django 5.2 LTS | Django 6.0 |
|--------|----------------|----------------|------------|
| 3.10   | ✅ | ✅ | ❌ |
| 3.11   | ✅ | ✅ | ❌ |
| 3.12   | ✅ | ✅ | ✅ |
| 3.13   | ✅ | ✅ | ✅ |
| 3.14   | ❌ | ✅ | ✅ |

### Configuration

1. Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "django_app_parameter",
]
```

2. Optional - make global parameters available in all templates:

```python
TEMPLATES = [
    {
        ...
        "OPTIONS": {
            "context_processors": [
                ...
                "django_app_parameter.context_processors.add_global_parameter_context",
            ],
        },
    },
]
```

3. Run migrations:

```bash
python manage.py migrate
```

4. Access Django admin to create your first parameters!

## Basic Usage

### Reading Parameters

In Python code:

```python
from django_app_parameter import app_parameter

# Read parameter value
title = app_parameter.BLOG_TITLE
email = app_parameter.CONTACT_EMAIL
```

In templates (for global parameters):

```html
<title>{{ BLOG_TITLE }}</title>
```

### Writing Parameters

```python
# Update parameter value programmatically
app_parameter.BLOG_TITLE = "My New Title"
```

### Parameter Names → Slugs

Parameters are accessed via auto-generated slugs:

```
"Blog Title"     → BLOG_TITLE
"sender e-mail"  → SENDER_E_MAIL
"##weird@Na_me"  → WEIRDNA_ME
```

## Features

### Supported Types
String • Integer • Float • Boolean • URL • Email • JSON List • JSON Dict • File Path • Duration • Percentage • DateTime • Date • Time

### Bulk Import/Export

Load parameters from JSON:

```bash
python manage.py dap_load --file parameters.json
```

Export all parameters:

```bash
python manage.py dap_dump --file backup.json
```

Example JSON format:

```json
[
    {"name": "Site Title", "value": "My Site", "is_global": true},
    {"name": "Max Upload Size", "value": "10485760", "value_type": "INT"}
]
```

Use `--no-update` to only create new parameters without overwriting existing ones (useful in deployment scripts).

### Validation

Attach validators to parameters (min/max value, length, regex, choices, etc.) - configured through Django admin or custom validators.

### Encryption

Enable encryption for sensitive parameters (requires `cryptography` extra). Manage encryption keys with the `dap_rotate_key` command.

### History Tracking

Enable `enable_history` to track all value changes with timestamps - viewable in Django admin.

---

📖 **[Read the full documentation](https://django-app-parameter.readthedocs.io/)** for detailed information on all features.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

**Requirements for contributions:**
- Format code with Ruff
- Add type hints (validated with Pyright)
- Maintain 100% test coverage

## Links

- 📚 [Documentation](https://django-app-parameter.readthedocs.io/)
- 🐛 [Issue Tracker](https://github.com/Swannbm/django-app-parameter/issues)
- 📦 [PyPI Package](https://pypi.org/project/django-app-parameter/)
- 🔄 [Release Process](.github/RELEASE.md)

## License

CC0 1.0 Universal - Public Domain