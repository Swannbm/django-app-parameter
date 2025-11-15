# Management Commands

## dap_load

Import parameters from JSON file or string.

### Syntax

```bash
python manage.py dap_load --file <path>
python manage.py dap_load --json '<json>'
python manage.py dap_load --no-update --file <path>
```

### Options

- `--file <path>`: Load from JSON file
- `--json '<string>'`: Load from JSON string
- `--no-update`: Create only, skip existing parameters

### Examples

```bash
# Import from file
python manage.py dap_load --file parameters.json

# Import without overwriting existing
python manage.py dap_load --no-update --file defaults.json

# Import from JSON string
python manage.py dap_load --json '[{"name": "Site Title", "value": "My Site"}]'
```

### JSON Format

```json
[
    {
        "name": "Site Title",
        "value": "My Blog",
        "value_type": "STR",
        "description": "Main site title",
        "is_global": true,
        "slug": "SITE_TITLE",
        "validators": [
            {
                "validator_type": "MaxLengthValidator",
                "validator_params": {"limit_value": 100}
            }
        ]
    }
]
```

### Fields

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `name` | Yes | - | Human-readable name |
| `value` | No | `""` | Parameter value |
| `value_type` | No | `"STR"` | Type code (see below) |
| `description` | No | `""` | Description |
| `is_global` | No | `false` | Template access |
| `slug` | No | auto | Custom slug (auto-generated from `name`) |
| `validators` | No | `[]` | Validator list |

### Type Codes

**Basic Types:**
- `STR`: String (default)
- `INT`: Integer
- `FLT`: Float
- `DCL`: Decimal
- `BOO`: Boolean

**Date/Time Types:**
- `DAT`: Date (YYYY-MM-DD)
- `DTM`: Datetime (ISO 8601)
- `TIM`: Time (HH:MM:SS)
- `DUR`: Duration (seconds as timedelta)

**Validated Types:**
- `URL`: Validated URL
- `EML`: Validated email
- `PCT`: Percentage (0-100)

**Structured Types:**
- `JSN`: JSON (any structure)
- `LST`: List (comma-separated)
- `DCT`: Dict (JSON object)
- `PTH`: Path (file path)

### Validators

Validators are defined in the `validators` array. Each validator requires:
- `validator_type`: Validator name (built-in or custom)
- `validator_params`: Parameters dict (optional, depends on validator)

#### Built-in Validators

**Value Validators:**
```json
{
    "validator_type": "MinValueValidator",
    "validator_params": {"limit_value": 0}
}
```
```json
{
    "validator_type": "MaxValueValidator",
    "validator_params": {"limit_value": 100}
}
```

**Length Validators:**
```json
{
    "validator_type": "MinLengthValidator",
    "validator_params": {"limit_value": 3}
}
```
```json
{
    "validator_type": "MaxLengthValidator",
    "validator_params": {"limit_value": 255}
}
```

**Pattern Validators:**
```json
{
    "validator_type": "RegexValidator",
    "validator_params": {
        "regex": "^[A-Z0-9]+$",
        "message": "Only uppercase letters and numbers allowed"
    }
}
```
```json
{
    "validator_type": "validate_slug",
    "validator_params": {}
}
```

**Format Validators:**
```json
{"validator_type": "EmailValidator", "validator_params": {}}
```
```json
{"validator_type": "URLValidator", "validator_params": {}}
```
```json
{"validator_type": "validate_ipv4_address", "validator_params": {}}
```
```json
{"validator_type": "validate_ipv6_address", "validator_params": {}}
```

**File Validators:**
```json
{
    "validator_type": "FileExtensionValidator",
    "validator_params": {"allowed_extensions": ["pdf", "jpg", "png"]}
}
```

#### Custom Validators

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

Use in JSON:
```json
{
    "name": "Lucky Number",
    "value": "42",
    "value_type": "INT",
    "validators": [
        {
            "validator_type": "even_number",
            "validator_params": {}
        }
    ]
}
```

See [utils.py](../django_app_parameter/utils.py) for validator registry implementation.

### Complete Examples

#### Tax Rate with Validators
```json
{
    "name": "Tax Rate",
    "value": "20.0",
    "value_type": "DCL",
    "description": "VAT rate in percentage",
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

#### Email with Validation
```json
{
    "name": "Contact Email",
    "value": "contact@example.com",
    "value_type": "EML",
    "is_global": true,
    "validators": [
        {
            "validator_type": "EmailValidator",
            "validator_params": {}
        }
    ]
}
```

#### Launch Date
```json
{
    "name": "Launch Date",
    "value": "2024-12-31",
    "value_type": "DAT",
    "description": "Product launch date"
}
```

### Use Cases

#### Initial Deployment
```bash
#!/bin/bash
python manage.py migrate
python manage.py dap_load --no-update --file config/defaults.json
python manage.py collectstatic --noinput
gunicorn myproject.wsgi
```

#### Environment Migration
```bash
# Export from staging
python manage.py dap_dump staging_params.json

# Import to production (without overwriting)
python manage.py dap_load --no-update --file staging_params.json
```

## dap_dump

Export all parameters to JSON file.

### Syntax

```bash
python manage.py dap_dump <file> [--indent N]
```

### Arguments

- `file`: Output file path (required)
- `--indent`: JSON indentation level (default: 4)

### Examples

```bash
# Export to file
python manage.py dap_dump backup.json

# Export with no indentation (compact)
python manage.py dap_dump backup.json --indent 0

# Export with 2-space indentation
python manage.py dap_dump backup.json --indent 2
```

### Output Format

Includes all fields and validators:

```json
[
    {
        "name": "Site Title",
        "slug": "SITE_TITLE",
        "value": "My Blog",
        "value_type": "STR",
        "description": "Main title",
        "is_global": true,
        "validators": [
            {
                "validator_type": "MaxLengthValidator",
                "validator_params": {"limit_value": 100}
            }
        ]
    },
    {
        "name": "Tax Rate",
        "slug": "TAX_RATE",
        "value": "20.0",
        "value_type": "DCL",
        "description": "VAT rate",
        "is_global": false,
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
]
```

### Use Cases

**Backup:**
```bash
python manage.py dap_dump backup_$(date +%Y%m%d).json
```

**Documentation:**
Export current config for reference.

**Migration:**
Export from one environment, import to another.

**Version Control:**
Track parameter changes in git (exclude sensitive params).

## Next

- [Usage Guide](usage-guide.md)
- [FAQ](faq.md)
- [Command implementations](../django_app_parameter/management/commands/)
