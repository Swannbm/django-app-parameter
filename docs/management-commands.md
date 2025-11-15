# Management Commands

## dap_load

Import parameters from JSON file or string.

> **Backward Compatibility**: The `dap_load` command is **backward compatible** and can load dumps from any previous version (v1.x, v2.0, v2.1+). Missing fields automatically use default values. See [dump-format-versions.md](dump-format-versions.md) for details.

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

**Complete example (v2.1+):**
```json
[
    {
        "name": "Site Title",
        "value": "My Blog",
        "value_type": "STR",
        "description": "Main site title",
        "is_global": true,
        "slug": "SITE_TITLE",
        "enable_cypher": false,
        "enable_history": true,
        "validators": [
            {
                "validator_type": "MaxLengthValidator",
                "validator_params": {"limit_value": 100}
            }
        ]
    }
]
```

**Minimal example (all versions):**
```json
[
    {
        "name": "Site Title",
        "value": "My Blog"
    }
]
```

### Fields

| Field | Required | Default | Since | Description |
|-------|----------|---------|-------|-------------|
| `name` | Yes | - | v1.0 | Human-readable name |
| `value` | No | `""` | v1.0 | Parameter value |
| `value_type` | No | `"STR"` | v1.0 | Type code (see below) |
| `description` | No | `""` | v1.0 | Description |
| `is_global` | No | `false` | v1.0 | Template access |
| `slug` | No | auto | v1.0 | Custom slug (auto-generated from `name`) |
| `validators` | No | `[]` | v2.0 | Validator list |
| `enable_cypher` | No | `false` | v2.0 | Enable encryption for this parameter |
| `enable_history` | No | `false` | v2.1 | Track value changes in history |

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

Includes all parameter fields and validators (v2.1+ format):

```json
[
    {
        "name": "Site Title",
        "slug": "SITE_TITLE",
        "value": "My Blog",
        "value_type": "STR",
        "description": "Main title",
        "is_global": true,
        "enable_cypher": false,
        "enable_history": true,
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
        "enable_cypher": false,
        "enable_history": false,
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

> **Note**: History entries themselves are NOT exported. Only the `enable_history` flag is included. This means you can enable history tracking on import, but previous historical values are not migrated.

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

## dap_rotate_key

Rotate encryption key for encrypted parameters (two-step process).

> **Note**: For encryption setup and basic usage, see the [Encryption](../README.md#encryption) section in the main README.

### Syntax

**Step 1: Generate new key and backup**
```bash
python manage.py dap_rotate_key [--backup-file <path>]
```

**Step 2: Apply rotation**
```bash
python manage.py dap_rotate_key --old-key <key> [--backup-file <path>]
```

### Options

- `--old-key <key>`: Old encryption key for decryption. When provided, performs step 2.
- `--backup-file <path>`: Path to backup file (default: `dap_backup_key.json` at project root)

### Examples

**Step 1: Generate new key**
```bash
# Generate new key and backup old one
python manage.py dap_rotate_key

# With custom backup location
python manage.py dap_rotate_key --backup-file /path/to/backup.json
```

Output shows:
- The new encryption key to add to settings
- Command for step 2

**Step 2: Apply rotation**
```bash
# After updating settings with new key
python manage.py dap_rotate_key --old-key <old-key-from-step1>
```

### Process

**Step 1:**
1. Reads current key from settings
2. Generates new encryption key
3. Backs up old key to `dap_backup_key.json` (appends with timestamp)
4. Displays new key and instructions

**Step 2:**
1. Validates old key (from parameter) and new key (from settings)
2. Decrypts all encrypted parameters with old key
3. Re-encrypts with new key from settings
4. Saves updated parameters

### Backup File Format

```json
{
  "keys": [
    {
      "timestamp": "2024-11-14T15:30:00",
      "key": "old_key_base64...",
      "parameters_count": 5
    }
  ]
}
```

### Custom Backup Location

Via settings:
```python
DJANGO_APP_PARAMETER = {
    'encryption_key': '...',
    'encryption_key_backup_file': '/secure/location/dap_backup_key.json'
}
```

Or via command option:
```bash
python manage.py dap_rotate_key --backup-file /path/to/backup.json
```

## Next

- [Usage Guide](usage-guide.md)
- [FAQ](faq.md)
- [Command implementations](../django_app_parameter/management/commands/)
