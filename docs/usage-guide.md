# Usage Guide

## Access Patterns

### Proxy (Recommended)

```python
from django_app_parameter import app_parameter

title = app_parameter.BLOG_TITLE        # → str
year = app_parameter.BIRTH_YEAR         # → int
rate = app_parameter.TAX_RATE           # → Decimal
config = app_parameter.API_CONFIG       # → dict
enabled = app_parameter.FEATURE_FLAG    # → bool
launch = app_parameter.LAUNCH_DATE      # → date
timeout = app_parameter.TIMEOUT         # → timedelta
```

Pros: Concise, auto-conversion. Cons: Raises exception if missing.

### Manager (Explicit)

```python
from django_app_parameter.models import Parameter

# Basic types
title = Parameter.objects.str("BLOG_TITLE")
year = Parameter.objects.int("BIRTH_YEAR")
rate = Parameter.objects.decimal("TAX_RATE")
enabled = Parameter.objects.bool("FEATURE_FLAG")

# Date/time types
launch = Parameter.objects.date("LAUNCH_DATE")
event = Parameter.objects.datetime("EVENT_DATETIME")
opening = Parameter.objects.time("OPENING_TIME")
timeout = Parameter.objects.duration("TIMEOUT")

# Validated types
site_url = Parameter.objects.url("SITE_URL")
contact = Parameter.objects.email("CONTACT_EMAIL")
discount = Parameter.objects.percentage("DISCOUNT")

# Structured types
tags = Parameter.objects.list("TAGS")
settings = Parameter.objects.dict("SETTINGS")
log_path = Parameter.objects.path("LOG_PATH")
```

Pros: Explicit types, better IDE support.

### Parameter Object

```python
param = Parameter.objects.get(slug="BLOG_TITLE")

print(param.name)         # "Blog Title"
print(param.slug)         # "BLOG_TITLE"
print(param.value_type)   # "STR"
print(param.is_global)    # True/False

value = param.get()       # Auto-converted
```

## Type Usage

### STR (String)
```python
Parameter.objects.create(
    name="Site Title",
    value="My Site",
    value_type=Parameter.TYPES.STR
)
title = app_parameter.SITE_TITLE  # "My Site"
```

### INT (Integer)
```python
Parameter.objects.create(
    name="Max Upload Size",
    value="5242880",
    value_type=Parameter.TYPES.INT
)
max_size = app_parameter.MAX_UPLOAD_SIZE  # 5242880
```

### FLT (Float)
```python
Parameter.objects.create(
    name="PI Value",
    value="3.14159",
    value_type=Parameter.TYPES.FLT
)
pi = app_parameter.PI_VALUE  # 3.14159
```

**Warning**: Use DCL for money.

### DCL (Decimal)
```python
from decimal import Decimal

Parameter.objects.create(
    name="Tax Rate",
    value="20.00",
    value_type=Parameter.TYPES.DCL
)
tax_rate = app_parameter.TAX_RATE  # Decimal('20.00')
```

### BOO (Boolean)
```python
Parameter.objects.create(
    name="Maintenance Mode",
    value="false",
    value_type=Parameter.TYPES.BOO
)
if app_parameter.MAINTENANCE_MODE:
    return HttpResponse("Under maintenance")
```

Values: `"true"/"false"`, `"1"/"0"`, `"yes"/"no"` (case-insensitive).

### DATE (Date)
```python
from datetime import date

Parameter.objects.create(
    name="Launch Date",
    value="2024-12-31",
    value_type=Parameter.TYPES.DATE
)
launch = app_parameter.LAUNCH_DATE  # date(2024, 12, 31)
```

Format: YYYY-MM-DD (ISO 8601).

### DATETIME (Date and Time)
```python
from datetime import datetime

Parameter.objects.create(
    name="Event Start",
    value="2024-12-31T23:59:59",
    value_type=Parameter.TYPES.DATETIME
)
event = app_parameter.EVENT_START  # datetime(2024, 12, 31, 23, 59, 59)
```

Format: ISO 8601 (`YYYY-MM-DDTHH:MM:SS`).

### TIME (Time)
```python
from datetime import time

Parameter.objects.create(
    name="Opening Time",
    value="09:00:00",
    value_type=Parameter.TYPES.TIME
)
opening = app_parameter.OPENING_TIME  # time(9, 0, 0)
```

Format: HH:MM:SS.

### DURATION (Timedelta)
```python
from datetime import timedelta

Parameter.objects.create(
    name="Session Timeout",
    value="3600",  # seconds
    value_type=Parameter.TYPES.DURATION
)
timeout = app_parameter.SESSION_TIMEOUT  # timedelta(seconds=3600)
```

Stored as seconds, returned as `timedelta`.

### URL (Validated URL)
```python
Parameter.objects.create(
    name="API Endpoint",
    value="https://api.example.com",
    value_type=Parameter.TYPES.URL
)
api_url = app_parameter.API_ENDPOINT  # "https://api.example.com"
```

Validates URL format. Raises `ValueError` if invalid.

### EMAIL (Validated Email)
```python
Parameter.objects.create(
    name="Contact Email",
    value="contact@example.com",
    value_type=Parameter.TYPES.EMAIL
)
email = app_parameter.CONTACT_EMAIL  # "contact@example.com"
```

Validates email format. Raises `ValueError` if invalid.

### PERCENTAGE (0-100 Float)
```python
Parameter.objects.create(
    name="Discount",
    value="15.5",
    value_type=Parameter.TYPES.PERCENTAGE
)
discount = app_parameter.DISCOUNT  # 15.5
```

Validates 0-100 range. Raises `ValueError` if out of range.

### LIST (Comma-separated)
```python
Parameter.objects.create(
    name="Allowed Tags",
    value="python, django, web",
    value_type=Parameter.TYPES.LIST
)
tags = app_parameter.ALLOWED_TAGS  # ["python", "django", "web"]
```

Splits by comma, strips whitespace.

### DICT (JSON Dictionary)
```python
Parameter.objects.create(
    name="API Settings",
    value='{"host": "api.example.com", "port": 443}',
    value_type=Parameter.TYPES.DICT
)
settings = app_parameter.API_SETTINGS  # {"host": "api.example.com", "port": 443}
```

Must be valid JSON object. Raises `ValueError` if not dict.

### JSN (Any JSON)
```python
Parameter.objects.create(
    name="Feature Flags",
    value='["feature1", "feature2"]',
    value_type=Parameter.TYPES.JSN
)
flags = app_parameter.FEATURE_FLAGS  # ["feature1", "feature2"]
```

Any valid JSON (dict, list, etc.).

### PATH (File Path)
```python
from pathlib import Path

Parameter.objects.create(
    name="Log Directory",
    value="/var/log/myapp",
    value_type=Parameter.TYPES.PATH
)
log_dir = app_parameter.LOG_DIRECTORY  # Path("/var/log/myapp")
```

Returns `pathlib.Path` object.

## Modifying Parameters

### Using `set()`

```python
param = Parameter.objects.get(slug="TAX_RATE")
param.set(Decimal("19.6"))  # Type-safe, validates, saves
```

Validators run automatically before saving.

### Direct Setters

```python
param.set_int(42)
param.set_str("new value")
param.set_date(date(2024, 12, 31))
param.set_list(["a", "b", "c"])
```

Type-safe: raises `TypeError` if wrong type.

### In Admin

Changes take effect immediately. Validators run on save.

## Validators

### Adding Validators

```python
param = Parameter.objects.get(slug="EMAIL")

# Add validator
param.validators.create(
    validator_type="EmailValidator",
    validator_params={}
)

# With parameters
param.validators.create(
    validator_type="MinValueValidator",
    validator_params={"limit_value": 0}
)
```

### Built-in Validators

**Value Validators:**
- `MinValueValidator`: `{"limit_value": 0}`
- `MaxValueValidator`: `{"limit_value": 100}`

**Length Validators:**
- `MinLengthValidator`: `{"limit_value": 3}`
- `MaxLengthValidator`: `{"limit_value": 255}`

**Pattern Validators:**
- `RegexValidator`: `{"regex": "^[A-Z]+$"}`
- `validate_slug`: No params

**Format Validators:**
- `EmailValidator`: No params
- `URLValidator`: No params
- `validate_ipv4_address`: No params
- `validate_ipv6_address`: No params

**File Validators:**
- `FileExtensionValidator`: `{"allowed_extensions": ["pdf", "jpg"]}`

### Custom Validators

Define in settings:

```python
# settings.py
DJANGO_APP_PARAMETER = {
    'validators': {
        'even_number': 'myapp.validators.validate_even_number',
        'french_phone': 'myapp.validators.validate_french_phone',
    }
}
```

```python
# myapp/validators.py
from django.core.exceptions import ValidationError

def validate_even_number(value):
    if value % 2 != 0:
        raise ValidationError(f"{value} is not even")
```

Use:
```python
param.validators.create(
    validator_type="even_number",
    validator_params={}
)
```

### Validator JSON Format

For `load_param` command:

```json
{
    "name": "Tax Rate",
    "value": "20.0",
    "value_type": "DCL",
    "validators": [
        {
            "validator_type": "MinValueValidator",
            "validator_params": {"limit_value": 0}
        },
        {
            "validator_type": "MaxValueValidator",
            "validator_params": {"limit_value": 100}
        }
    ]
}
```

See [management-commands.md](management-commands.md).

## In Views

```python
from django.shortcuts import render
from django_app_parameter import app_parameter
from datetime import date

def home(request):
    if app_parameter.MAINTENANCE_MODE:
        return HttpResponse("Under maintenance", status=503)

    launch_date = app_parameter.LAUNCH_DATE
    if date.today() < launch_date:
        return HttpResponse("Coming soon!")

    context = {
        'title': app_parameter.SITE_TITLE,
        'contact': app_parameter.CONTACT_EMAIL,
        'discount': app_parameter.DISCOUNT,
    }
    return render(request, 'home.html', context)
```

## In Templates

Setup in [settings.py](../tests/settings.py):

```python
TEMPLATES = [{
    'OPTIONS': {
        'context_processors': [
            'django_app_parameter.context_processors.add_global_parameter_context',
        ],
    },
}]
```

Usage:

```html
<title>{{ SITE_TITLE }}</title>
<a href="mailto:{{ CONTACT_EMAIL }}">Contact</a>

{% if MAINTENANCE_MODE %}
    <div class="alert">Maintenance scheduled</div>
{% endif %}
```

**Note**: Only `is_global=True` parameters are available in templates. Parameters are passed in their declared format (int, bool, etc.).

## Advanced Patterns

### Caching

```python
from django.core.cache import cache

def get_cached_param(slug, timeout=3600):
    key = f"param_{slug}"
    value = cache.get(key)
    if value is None:
        value = getattr(app_parameter, slug)
        cache.set(key, value, timeout)
    return value
```

### Default Values

```python
def get_param_or_default(slug, default):
    try:
        return getattr(app_parameter, slug)
    except ImproperlyConfigured:
        return default
```

### Dynamic Feature Flags

```python
def feature_enabled(feature_name):
    try:
        return getattr(app_parameter, f"ENABLE_{feature_name.upper()}")
    except ImproperlyConfigured:
        return False
```

## Best Practices

1. **Use appropriate types**: DATE for dates, DCL for money, PERCENTAGE for percentages
2. **Add validators**: Ensure data integrity
3. **Cache frequently accessed params**: Reduce DB queries
4. **Don't store secrets**: No encryption
5. **Use descriptive names**: Help admins understand purpose
6. **Set is_global carefully**: Only for template-needed params
7. **Document in description**: Explain purpose and format

## Next

- [Management Commands](management-commands.md)
- [FAQ](faq.md)
- [Models](../django_app_parameter/models.py)
