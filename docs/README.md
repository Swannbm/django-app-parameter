# Django App Parameter

Store configurable application parameters in database. Modify them via Django admin without redeployment.

## Quick Start

```bash
pip install django-app-parameter

# Or with encryption support (optional)
pip install django-app-parameter[cryptography]
```

```python
# settings.py
INSTALLED_APPS += ['django_app_parameter']
```

```bash
python manage.py migrate
```

```python
from django_app_parameter import app_parameter
title = app_parameter.BLOG_TITLE
```

## Problem

- **`settings.py`**: Static, requires redeployment
- **Env vars**: Hard to change in production
- **Custom DB**: Need custom development

Solution: **Runtime-modifiable parameters** for administrators.

## Features

- **Database storage** via Django ORM
- **Admin interface** for CRUD operations
- **15 types**: INT, STR, FLT, DCL, JSN, BOO, DATE, DATETIME, TIME, URL, EMAIL, LIST, DICT, PATH, DURATION, PERCENTAGE
- **Validators**: Built-in Django validators + custom validators
- **Type-safe setters**: `param.set()` with automatic validation
- **Auto slug generation**: `"blog title"` → `"BLOG_TITLE"`
- **Bulk loading** via `dap_load` command
- **Export** via `dap_dump` command
- **Encryption support** for sensitive data
- **Zero dependencies** (Django 4.2+ only, cryptography optional for encryption)
- **100% test coverage**

## Access Patterns

**Proxy (recommended):**
```python
from django_app_parameter import app_parameter
title = app_parameter.BLOG_TITLE  # Auto-converted
```

**Direct:**
```python
from django_app_parameter.models import Parameter
param = Parameter.objects.get(slug="BLOG_TITLE")
title = param.get()  # Auto-converted to proper type
```

**Templates:**
```html
<title>{{ BLOG_TITLE }}</title>  {# is_global=True only #}
```

## Data Types

### Basic Types
- **INT**: Integers
- **STR**: Strings (default)
- **FLT**: Floats
- **DCL**: Decimals (exact precision for money)
- **BOO**: Booleans

### Date/Time Types
- **DATE**: Date (YYYY-MM-DD)
- **DATETIME**: Date and time (ISO 8601)
- **TIME**: Time (HH:MM:SS)
- **DURATION**: Duration in seconds (as timedelta)

### Validated Types
- **URL**: Validated URL
- **EMAIL**: Validated email
- **PERCENTAGE**: Float validated 0-100

### Structured Types
- **JSN**: JSON (any JSON structure)
- **LIST**: Comma-separated list
- **DICT**: JSON dictionary
- **PATH**: File path (as Path object)

## Validators

Add validators to parameters for automatic validation:

```python
param.validators.create(
    validator_type="MinValueValidator",
    validator_params={"limit_value": 0}
)
```

**Built-in validators:**
- MinValueValidator, MaxValueValidator
- MinLengthValidator, MaxLengthValidator
- RegexValidator
- EmailValidator, URLValidator
- validate_slug, validate_ipv4_address, validate_ipv6_address
- FileExtensionValidator

**Custom validators** via `DJANGO_APP_PARAMETER['validators']` setting.

See [models.py](../django_app_parameter/models.py) and [utils.py](../django_app_parameter/utils.py).

## Setters

Modify parameters with type-safe setters:

```python
param = Parameter.objects.get(slug="TAX_RATE")
param.set(Decimal("19.6"))  # Validates + saves

# Or with auto_cast to convert from string:
param.set("19.6", auto_cast=True)  # Converts string to Decimal, validates + saves
```

Validators run automatically on `set()`. The `auto_cast` parameter converts string input to the parameter's native type before validation.

## Use Cases

- **Config**: API endpoints, max sizes, pagination
- **Branding**: Site title, footer, contact
- **Feature flags**: Maintenance mode, beta features
- **Business rules**: Tax rates, shipping costs
- **Dates**: Launch dates, expiration dates
- **Durations**: Timeouts, session durations


## Encryption

Store sensitive parameter values encrypted in database.

### Setup

**Install with encryption support**:

```bash
pip install django-app-parameter[cryptography]
```

**Configure encryption key**:

```python
# settings.py
from cryptography.fernet import Fernet

DJANGO_APP_PARAMETER = {
    'encryption_key': Fernet.generate_key().decode('utf-8'),  # Generate once, store securely
}
```

### Usage

```python
# Enable encryption for a parameter
param = Parameter.objects.create(
    name="API Secret",
    value_type=TYPES.STR,
    value="initial_value",
    enable_cypher=True  # Enable encryption
)

# Set/get works transparently
param.set("secret_api_key")  # Automatically encrypted
value = param.get()  # Automatically decrypted
```

### Notes

- Value encrypted on `set()`, decrypted on `get()`
- Export/import (`to_dict`/`from_dict`) uses plaintext
- Max encrypted value: ~190 chars (Fernet overhead: ~60 bytes)
- Admin shows encrypted field as checkbox

For key rotation and advanced usage, see [Management Commands](management-commands.md#dap_rotate_key).

## vs. Alternatives

### vs. settings.py
Static vs. Dynamic. Use settings for structure (DATABASES, MIDDLEWARE), app_parameter for business config.

### vs. Env vars
Use env vars for secrets (API keys, passwords), app_parameter for business params.

## Limits

1. **DB query per access** (consider caching)
2. **Encryption available** (see [Encryption](#encryption) section above)
3. **Templates: strings only**

## Documentation

- [Usage Guide](usage-guide.md) - Examples
- [Management Commands](management-commands.md) - CLI tools (load, dump, key rotation)
- [FAQ](faq.md)

For encryption setup, see [Encryption](#encryption) section above.

## Info

- **Version:** 3.1.0
- **License:** CC0 1.0 Universal
- **Python:** 3.10+
- **Django:** 4.2 - 6.0
- **Test Coverage:** 100%
- **Repository:** [github.com/Swannbm/django-app-parameter](https://github.com/Swannbm/django-app-parameter)
