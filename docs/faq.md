# FAQ

## Installation

### Requirements?
- Python 3.7+
- Django 3.2+
- All Django-supported databases (PostgreSQL, MySQL, SQLite, Oracle)

### Uninstall?
```bash
python manage.py dumpdata django_app_parameter > backup.json  # Optional
python manage.py migrate django_app_parameter zero
pip uninstall django-app-parameter
```
Remove from `INSTALLED_APPS`.

## Basic Usage

### Create parameter?

**Admin**: `/admin/django_app_parameter/parameter/` → Add Parameter

**Code**:
```python
Parameter.objects.create(name="Site Title", value="My Site", value_type=Parameter.TYPES.STR)
```

**Command**:
```bash
python manage.py load_param --json '[{"name": "Site Title", "value": "My Site"}]'
```

### Access parameter?
```python
from django_app_parameter import app_parameter
title = app_parameter.SITE_TITLE
```

### `app_parameter.SLUG` vs `Parameter.objects.str("SLUG")`?

- `app_parameter.SLUG`: Auto-converts based on `value_type`
- `Parameter.objects.str()`: Explicit type

Use `app_parameter` for simplicity, `Manager` for control.

### Check if exists?
```python
try:
    value = app_parameter.MAYBE_EXISTS
except ImproperlyConfigured:
    value = "default"
```

### Modify parameter?
```python
param = Parameter.objects.get(slug="TAX_RATE")
param.set(Decimal("19.6"))  # Type-safe, validates, saves
```

Or use direct setters:
```python
param.set_int(42)
param.set_date(date(2024, 12, 31))
```

## Data Types

### Supported types?

**Basic (5)**: INT, STR, FLT, DCL, BOO

**Date/Time (4)**: DATE, DATETIME, TIME, DURATION

**Validated (3)**: URL, EMAIL, PERCENTAGE

**Structured (4)**: JSN, LIST, DICT, PATH

**Total**: 15 types

### FLT vs DCL?
- **FLT**: Approximate, for scientific calculations
- **DCL**: Exact, for financial calculations

Use **DCL** for money, prices, tax rates.

### JSN vs DICT vs LIST?
- **JSN**: Any JSON structure (dict, list, etc.)
- **DICT**: JSON dictionary only (validates type)
- **LIST**: Comma-separated strings (no JSON)

### DATE vs DATETIME vs TIME?
- **DATE**: Date only (YYYY-MM-DD) → `date` object
- **DATETIME**: Date + time (ISO 8601) → `datetime` object
- **TIME**: Time only (HH:MM:SS) → `time` object

### DURATION type?
Stores duration in seconds, returns `timedelta`:
```python
Parameter.objects.create(
    name="Timeout",
    value="3600",  # 1 hour in seconds
    value_type=Parameter.TYPES.DURATION
)
timeout = app_parameter.TIMEOUT  # timedelta(seconds=3600)
```

### PERCENTAGE type?
Float validated 0-100:
```python
discount = app_parameter.DISCOUNT  # 15.5
```

### PATH type?
File path as `pathlib.Path`:
```python
log_dir = app_parameter.LOG_DIR  # Path("/var/log/myapp")
```

## Validators

### What are validators?
Automatic validation rules attached to parameters. Validate on:
- Admin save
- `param.set()` call
- Import via `load_param`

### Add validator?
```python
param.validators.create(
    validator_type="MinValueValidator",
    validator_params={"limit_value": 0}
)
```

### Built-in validators?
- MinValueValidator, MaxValueValidator
- MinLengthValidator, MaxLengthValidator
- RegexValidator
- EmailValidator, URLValidator
- validate_slug, validate_ipv4_address, validate_ipv6_address
- FileExtensionValidator

See [utils.py](../django_app_parameter/utils.py).

### Custom validators?
Define in settings:
```python
DJANGO_APP_PARAMETER = {
    'validators': {
        'even_number': 'myapp.validators.validate_even_number',
    }
}
```

Use:
```python
param.validators.create(
    validator_type="even_number",
    validator_params={}
)
```

### Validators in JSON?
```json
{
    "name": "Tax Rate",
    "value": "20.0",
    "validators": [
        {
            "validator_type": "MinValueValidator",
            "validator_params": {"limit_value": 0}
        }
    ]
}
```

### Remove validators?
```python
param.validators.all().delete()
```

Or specific:
```python
param.validators.filter(validator_type="MinValueValidator").delete()
```

## Slug System

### What's a slug?
Auto-generated identifier from `name`:
- `"Blog Title"` → `"BLOG_TITLE"`
- `"Sender E-mail"` → `"SENDER_E_MAIL"`

Used for code access: `app_parameter.BLOG_TITLE`

### Custom slug?
```python
Parameter.objects.create(
    name="Tax Rate",
    slug="MY_CUSTOM_SLUG"
)
value = app_parameter.MY_CUSTOM_SLUG
```

### Slug collision?
Error raised. Change `name` or set custom `slug`.

### Modify slug after creation?
No. `slug` is readonly after creation. Delete and recreate if needed.

## Templates

### Access in templates?
Add context processor:
```python
# settings.py
TEMPLATES = [{
    'OPTIONS': {
        'context_processors': [
            'django_app_parameter.context_processors.add_global_parameter_context',
        ],
    },
}]
```

Set `is_global=True` on parameter:
```html
<title>{{ SITE_TITLE }}</title>
```

**Note**: Parameters are passed in their declared format (int, bool, date, etc.).

### Why `is_global`?
Security: Prevents exposing sensitive params to templates.

## Management Commands

### Import many parameters?
```bash
python manage.py load_param --file parameters.json
```

See [management-commands.md](management-commands.md).

### Avoid overwriting?
```bash
python manage.py load_param --no-update --file defaults.json
```
Creates new only, skips existing.

### Export parameters?
```bash
python manage.py dump_param backup.json
```

Exports all parameters with validators.

## Performance

### DB query per access?
Yes. Use caching for frequent access:
```python
from django.core.cache import cache

def get_cached(slug, timeout=3600):
    key = f"param_{slug}"
    value = cache.get(key)
    if value is None:
        value = getattr(app_parameter, slug)
        cache.set(key, value, timeout)
    return value
```

### How many params recommended?
No hard limit. Hundreds work fine. Cache if performance issues.

## Security

### Store passwords?
**NO**. No encryption. Use environment variables for secrets.

### Store API keys?
**NO**. Use Django settings or env vars.

### What's safe to store?
- Business config (tax rates, limits)
- Branding (titles, messages)
- Feature flags
- Non-sensitive URLs
- Dates, durations
- Public emails

## Admin

### Change parameter type?
No. `value_type` is readonly after creation. Delete and recreate if needed.

### Validators in admin?
Yes. Edit parameter → Validators section (inline).

### Admin validation?
Validators run automatically on save. Invalid values rejected.

## Advanced

### Modify in code?
```python
param = Parameter.objects.get(slug="SITE_TITLE")
param.set("New Title")  # Type-safe, validates, saves
```

### Delete parameter?
**Admin**: Select and delete.

**Code**:
```python
Parameter.objects.get(slug="SITE_TITLE").delete()
```

### Default value on missing?
```python
def get_or_default(slug, default):
    try:
        return getattr(app_parameter, slug)
    except ImproperlyConfigured:
        return default

title = get_or_default("SITE_TITLE", "Default")
```

### Type conversion errors?
```python
try:
    value = app_parameter.SOME_PARAM
except (ValueError, TypeError) as e:
    # Handle conversion error
    value = default
```

### Multi-tenant?
Not built-in. Options:
- Separate databases per tenant
- Add tenant field to model (requires fork)
- Prefix slugs: `TENANT1_SITE_TITLE`

## Troubleshooting

### `ImproperlyConfigured: SLUG parameters need to be set`
Parameter doesn't exist. Create it or use try/except.

### `ValueError: invalid literal for int()`
Wrong `value_type` or invalid value. Check parameter.

### `ValidationError` on save
Validator failed. Check validator params or value.

### Template variable not found
- Check `is_global=True`
- Verify context processor added
- Parameter might not exist

### Migration errors
```bash
python manage.py migrate django_app_parameter --fake-initial
```

### Admin doesn't show
- Check `django_app_parameter` in `INSTALLED_APPS`
- Run `python manage.py migrate`
- Clear browser cache

### Validator not found
Check `DJANGO_APP_PARAMETER['validators']` setting. Ensure path is correct.

## vs. Alternatives

### vs. django-constance?
- **constance**: More features (Redis, validation, admin UI)
- **app_parameter**: 15 types, validators, setters, dump/load

Both mature. Use constance for Redis caching, app_parameter for type variety.

### vs. settings.py?
- **settings.py**: Static, requires redeployment
- **app_parameter**: Dynamic, runtime-modifiable

Use settings for structure (DATABASES, MIDDLEWARE), app_parameter for business config.

### vs. Environment variables?
- **Env vars**: Secrets, per-environment
- **app_parameter**: Business config, per-database

Use env vars for secrets, app_parameter for business params.

## Next

- [Installation](installation.md)
- [Usage Guide](usage-guide.md)
- [Management Commands](management-commands.md)
- [Tests](../tests/test_django_app_parameter.py)
