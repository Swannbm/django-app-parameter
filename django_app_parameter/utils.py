"""Utility functions for django-app-parameter."""

from __future__ import annotations

from importlib import import_module
from typing import Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.validators import (
    EmailValidator,
    FileExtensionValidator,
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    RegexValidator,
    URLValidator,
    validate_ipv4_address,
    validate_ipv6_address,
    validate_slug,
)
from django.utils.text import slugify

try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None  # type: ignore[assignment, misc]

HAS_CRYPTOGRAPHY = Fernet is not None

# Cache for imported validators to avoid repeated imports
_VALIDATOR_CACHE: dict[str, Any] = {}


def parameter_slugify(content: str) -> str:
    """
    Transform content :
    * slugify (with django's function)
    * upperise
    * replace dash (-) with underscore (_)
    """
    return slugify(content).upper().replace("-", "_")


# Built-in Django validators that are available by default
BUILTIN_VALIDATORS: dict[str, Any] = {
    "MinValueValidator": MinValueValidator,
    "MaxValueValidator": MaxValueValidator,
    "MinLengthValidator": MinLengthValidator,
    "MaxLengthValidator": MaxLengthValidator,
    "RegexValidator": RegexValidator,
    "EmailValidator": EmailValidator,
    "URLValidator": URLValidator,
    "validate_slug": validate_slug,
    "validate_ipv4_address": validate_ipv4_address,
    "validate_ipv6_address": validate_ipv6_address,
    "FileExtensionValidator": FileExtensionValidator,
}


def get_setting(key: str, default: Any = None) -> Any:
    """
    Get a value from DJANGO_APP_PARAMETER settings dictionary.

    Args:
        key: The setting key to retrieve
        default: Default value if key is not found

    Returns:
        The setting value or default

    Example:
        >>> get_setting("validators", {})
        {'even_number': 'myapp.validators.validate_even_number'}
    """
    app_settings = getattr(settings, "DJANGO_APP_PARAMETER", {})
    return app_settings.get(key, default)


def import_validator(validator_path: str) -> Any:
    """
    Import a validator from a dotted path string.

    Args:
        validator_path: Dotted path to the validator
                       (e.g., 'myapp.validators.validate_even_number')

    Returns:
        The imported validator function or class

    Raises:
        ImportError: If the module or validator cannot be imported
        AttributeError: If the validator doesn't exist in the module

    Example:
        >>> validator = import_validator("myapp.validators.validate_even_number")
        >>> validator(4)  # Should not raise
        >>> validator(3)  # Should raise ValidationError
    """
    try:
        module_path, validator_name = validator_path.rsplit(".", 1)
    except ValueError as e:
        raise ImportError(
            f"Invalid validator path '{validator_path}'. "
            f"Expected format: 'module.path.validator_name'"
        ) from e

    try:
        module = import_module(module_path)
    except ImportError as e:
        raise ImportError(
            f"Cannot import module '{module_path}'"
            f" from validator path '{validator_path}'"
        ) from e

    try:
        validator = getattr(module, validator_name)
    except AttributeError as e:
        raise AttributeError(
            f"Module '{module_path}' does not have attribute '{validator_name}'"
        ) from e

    return validator


def get_validator_from_registry(
    validator_type: str, use_cache: bool = True
) -> Any | None:
    """
    Get a validator by type from built-in or custom validators.

    This function looks up validators in the following order:
    1. Built-in Django validators (from BUILTIN_VALIDATORS)
    2. Custom validators from settings (DJANGO_APP_PARAMETER['validators'])

    Args:
        validator_type: The validator type/key to look up
        use_cache: Whether to use cached imports (default: True)

    Returns:
        The validator class/function, or None if not found

    Example:
        >>> # Built-in validator
        >>> validator = get_validator_from_registry("MinValueValidator")
        >>> validator is MinValueValidator
        True

        >>> # Custom validator (from settings)
        >>> validator = get_validator_from_registry("even_number")
        >>> validator.__name__
        'validate_even_number'
    """
    # Check built-in validators first
    if validator_type in BUILTIN_VALIDATORS:
        return BUILTIN_VALIDATORS[validator_type]

    # Check cache for custom validators
    if use_cache and validator_type in _VALIDATOR_CACHE:
        return _VALIDATOR_CACHE[validator_type]

    # Check custom validators from settings
    custom_validators = get_setting("validators", {})
    if validator_type in custom_validators:
        validator_path = custom_validators[validator_type]
        try:
            validator = import_validator(validator_path)
            if use_cache:
                _VALIDATOR_CACHE[validator_type] = validator
            return validator
        except (ImportError, AttributeError):
            # Let the caller handle the error
            raise

    return None


def get_available_validators() -> dict[str, str]:
    """
    Get all available validators (built-in + custom) with their display names.

    Returns a dictionary mapping validator keys to human-readable names.
    Built-in validators use their class/function names as display names.
    Custom validators use their keys as display names.

    Returns:
        Dictionary of {validator_key: display_name}

    Example:
        >>> validators = get_available_validators()
        >>> "MinValueValidator" in validators
        True
        >>> "even_number" in validators  # If defined in settings
        True
    """
    validators: dict[str, str] = {}

    # Add built-in validators with friendly names
    builtin_display_names = {
        "MinValueValidator": "Valeur minimale",
        "MaxValueValidator": "Valeur maximale",
        "MinLengthValidator": "Longueur minimale",
        "MaxLengthValidator": "Longueur maximale",
        "RegexValidator": "Expression régulière",
        "EmailValidator": "Validation email",
        "URLValidator": "Validation URL",
        "validate_slug": "Validation slug",
        "validate_ipv4_address": "Adresse IPv4",
        "validate_ipv6_address": "Adresse IPv6",
        "FileExtensionValidator": "Extensions de fichier autorisées",
    }

    for key in BUILTIN_VALIDATORS.keys():
        validators[key] = builtin_display_names.get(key, key)

    # Add custom validators from settings
    custom_validators = get_setting("validators", {})
    for key in custom_validators.keys():
        # Use a more friendly display name for custom validators
        display_name = key.replace("_", " ").title()
        validators[key] = f"{display_name} (custom)"

    return validators


def clear_validator_cache() -> None:
    """
    Clear the validator import cache.

    Useful for testing or when validators are dynamically modified.
    """
    _VALIDATOR_CACHE.clear()


# ===== Encryption utilities =====


def get_encryption_key(key: str | bytes | None = None) -> bytes:
    """
    Get the encryption key from Django settings or use provided key.

    The key should be stored in settings.DJANGO_APP_PARAMETER['encryption_key']
    and must be a Fernet-compatible key (32 url-safe base64-encoded bytes).

    Args:
        key: Optional encryption key to use. If provided, this key is used
             instead of the one from settings. Can be str or bytes.

    Returns:
        The encryption key as bytes

    Raises:
        ImproperlyConfigured: If cryptography is not installed, or if the
                              encryption key is not configured and no key
                              parameter is provided
    """
    if not HAS_CRYPTOGRAPHY:
        raise ImproperlyConfigured(
            "Encryption requires the 'cryptography' package. "
            "Install it with: pip install django-app-parameter[cryptography]"
        )

    # Use provided key if given
    if key is not None:
        if isinstance(key, str):
            return key.encode("utf-8")
        return key

    # Otherwise get from settings
    settings_key = get_setting("encryption_key")
    if not settings_key:
        raise ImproperlyConfigured(
            "No encryption key configured. "
            "Set DJANGO_APP_PARAMETER['encryption_key'] in settings. "
            "Generate one with: from cryptography.fernet import Fernet; "
            "Fernet.generate_key()"
        )

    # Convert to bytes if string
    if isinstance(settings_key, str):
        return settings_key.encode("utf-8")
    return settings_key


def encrypt_value(value: str, encryption_key: str | bytes | None = None) -> str:
    """
    Encrypt a string value using Fernet symmetric encryption.

    Args:
        value: The plaintext string to encrypt
        encryption_key: Optional encryption key to use. If not provided,
                       uses key from settings.

    Returns:
        The encrypted value as a string (base64-encoded)

    Raises:
        ImproperlyConfigured: If cryptography is not installed or if
                              encryption key is not configured
    """
    key = get_encryption_key(encryption_key)
    fernet = Fernet(key)  # type: ignore[misc]
    encrypted_bytes = fernet.encrypt(value.encode("utf-8"))
    return encrypted_bytes.decode("utf-8")


def decrypt_value(
    encrypted_value: str, encryption_key: str | bytes | None = None
) -> str:
    """
    Decrypt a string value using Fernet symmetric encryption.

    Args:
        encrypted_value: The encrypted value as a string (base64-encoded)
        encryption_key: Optional encryption key to use. If not provided,
                       uses key from settings.

    Returns:
        The decrypted plaintext string

    Raises:
        ImproperlyConfigured: If cryptography is not installed or if
                              encryption key is not configured
        cryptography.fernet.InvalidToken: If decryption fails
            (wrong key or corrupted data)
    """
    key = get_encryption_key(encryption_key)
    fernet = Fernet(key)  # type: ignore[misc]
    decrypted_bytes = fernet.decrypt(encrypted_value.encode("utf-8"))
    return decrypted_bytes.decode("utf-8")
