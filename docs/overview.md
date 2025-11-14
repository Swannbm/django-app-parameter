# Overview

Store application parameters in database. Modify via Django admin without code changes or restart.

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
- **Bulk loading** via `load_param` command
- **Export** via `dump_param` command
- **Zero dependencies** (Django 3.2+ only)
- **100% test coverage**

## Access Patterns

**Proxy (recommended):**
```python
from django_app_parameter import app_parameter
title = app_parameter.BLOG_TITLE  # Auto-converted
```

**Manager:**
```python
from django_app_parameter.models import Parameter
title = Parameter.objects.str("BLOG_TITLE")
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
```

Validators run automatically on `set()`.

## Data Model

See [models.py](../django_app_parameter/models.py):

**Parameter:**
| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField(100) | Human-readable |
| `slug` | SlugField(40) | Auto-generated ID |
| `value_type` | CharField(3) | Type (readonly after creation) |
| `value` | CharField(250) | Stored as string |
| `description` | TextField | Optional |
| `is_global` | BooleanField | Template access |

**ParameterValidator:**
| Field | Type | Description |
|-------|------|-------------|
| `parameter` | ForeignKey | Parameter |
| `validator_type` | CharField(400) | Validator name |
| `validator_params` | JSONField | Validator params |

## Use Cases

- **Config**: API endpoints, max sizes, pagination
- **Branding**: Site title, footer, contact
- **Feature flags**: Maintenance mode, beta features
- **Business rules**: Tax rates, shipping costs
- **Dates**: Launch dates, expiration dates
- **Durations**: Timeouts, session durations

## vs. Alternatives

### vs. settings.py
Static vs. Dynamic. Use settings for structure (DATABASES, MIDDLEWARE), app_parameter for business config.

### vs. Env vars
Use env vars for secrets (API keys, passwords), app_parameter for business params.

### vs. django-constance
More features vs. Simpler. Use constance for advanced needs, app_parameter for simplicity.

## Limits

1. **250 char limit**
2. **DB query per access** (consider caching)
3. **No encryption** (don't store secrets)
4. **Templates: strings only**

## Next

- [Installation](installation.md)
- [Usage Guide](usage-guide.md)
- [Management Commands](management-commands.md)
