# Encryption

Store sensitive parameter values encrypted in database.

## Setup

```python
# settings.py
from cryptography.fernet import Fernet

DJANGO_APP_PARAMETER = {
    'encryption_key': Fernet.generate_key().decode('utf-8'),  # Generate once, store securely
}
```

**Install**: `pip install cryptography`

## Usage

```python
# Enable encryption for a parameter
param = Parameter.objects.create(
    name="API Secret",
    value_type=Parameter.TYPES.STR,
    value="initial_value",
    enable_cypher=True  # Enable encryption
)

# Set/get works transparently
param.set_str("secret_api_key")
value = param.str()  # Automatically decrypted
```

## Key Rotation

```bash
# Rotate encryption key
python manage.py rotate_encryption_key

# With custom key
python manage.py rotate_encryption_key --new-key <base64-key>

# Custom backup directory
python manage.py rotate_encryption_key --backup-dir /path/to/backups
```

Process:
1. Decrypts all encrypted parameters
2. Backs up old key
3. Re-encrypts with new key

## Notes

- Value encrypted on `set()`, decrypted on `get()`
- Export/import (`to_dict`/`from_dict`) uses plaintext
- Max encrypted value: ~190 chars (Fernet overhead: ~60 bytes)
- Admin shows encrypted field as checkbox

## Config

- [models.py](../django_app_parameter/models.py) (`enable_cypher` field)
- [utils.py](../django_app_parameter/utils.py) (encryption functions)
- [rotate_encryption_key.py](../django_app_parameter/management/commands/rotate_encryption_key.py) (key rotation)
