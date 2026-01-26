from __future__ import annotations

import json
import logging
from collections.abc import Callable, Collection
from datetime import date as date_type
from datetime import datetime as datetime_type
from datetime import time as time_type
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator, validate_email
from django.db import models

from django_app_parameter.constants import TYPES
from django_app_parameter.managers import (
    ParameterDict_,
    ParameterManager,
    ValidatorDict,
    get_proxy_class,
)
from django_app_parameter.utils import (
    decrypt_value,
    encrypt_value,
    get_available_validators,
    get_validator_from_registry,
    parameter_slugify,
)

logger = logging.getLogger(__name__)


class ParameterValueTypeError(BaseException):
    """Raised when a parameter value is of incorrect type"""


class Parameter(models.Model):
    """Base model for application parameters with typed value support.

    Parameters are stored as strings in the database and converted to their
    appropriate Python types when accessed. Supports encryption, validation,
    and value history tracking.

    The default value type is STR (string).

    ..todo::
        - Add validate_value methode to validate without setting value
        - add form field support
    """

    objects: ParameterManager = ParameterManager()  # pyright: ignore[reportIncompatibleVariableOverride]

    name = models.CharField("Nom", max_length=100)
    slug = models.SlugField(max_length=40, unique=True)
    value_type = models.CharField(
        "Type de donnée", max_length=3, choices=TYPES.choices, default=TYPES.STR
    )
    description = models.TextField("Description", blank=True)
    value = models.TextField("Valeur")

    # OPTIONS
    is_global = models.BooleanField(default=False)
    enable_cypher = models.BooleanField(
        "Chiffrement activé",
        default=False,
        help_text="Si activé, la valeur sera chiffrée en base de données",
    )
    enable_history = models.BooleanField(
        "Historisation activée",
        default=False,
        help_text=(
            "Si activé, les modifications de valeur seront "
            "enregistrées dans l'historique"
        ),
    )

    @classmethod
    def from_db(
        cls,
        db: str | None,
        field_names: Collection[str],
        values: Collection[Any],
    ) -> Parameter:
        """Create instance from database row and convert to appropriate proxy class.

        This method is called by Django's ORM when loading instances from the database.
        It automatically converts the instance to the correct proxy class based on
        the value_type field.
        """
        instance = super().from_db(db, field_names, values)
        # Get value_type from the loaded values
        field_names_list = list(field_names)
        values_list = list(values)
        if "value_type" in field_names_list:
            value_type_idx = field_names_list.index("value_type")
            value_type = values_list[value_type_idx]
            proxy_class = get_proxy_class(value_type)
            if proxy_class is not cls:
                instance.__class__ = proxy_class  # type: ignore[assignment]
        return instance

    def _cast_from_str(self, value: str) -> Any:
        """Convert a string value to the parameter's native type.

        Args:
            value: The string value to convert.

        Returns:
            The value converted to the parameter's native type.
        """
        return str(value)

    def _cast_to_str(self, value: Any) -> str:
        """Convert a native type value to string for storage.

        Args:
            value: The native type value to convert.

        Returns:
            The string representation for database storage.

        """
        return str(value).strip()

    def _is_instance(self, value: Any) -> bool:
        """Check if a value is of the expected native type.

        Args:
            value: The value to check.

        Returns:
            True if value is of the expected type, False otherwise.

        """
        return isinstance(value, str)

    type: str = TYPES.STR

    def get_type(self) -> str:
        """Return the TYPES value for this parameter.

        Returns:
            The type code (e.g., 'INT', 'STR', etc.). Defaults to 'STR'.

        """
        return self.type

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Save the parameter, auto-generating slug and setting value_type."""
        # Only override value_type if using a typed proxy class (not base Parameter)
        if type(self) is not Parameter:
            self.value_type = self.get_type()
        if not self.slug:
            self.slug = parameter_slugify(self.name)
        super().save(*args, **kwargs)

    def _get_decrypted_value(self, value: str) -> str:
        """Decrypt value if encryption is enabled, otherwise return as-is."""
        if self.enable_cypher:
            return decrypt_value(value)
        return value

    def get(self) -> Any:
        """Get the parameter value converted to its native type."""
        str_value = self._get_decrypted_value(self.value)
        typed_value = self._cast_from_str(str_value)
        return typed_value

    def set(self, new_value: Any, auto_cast: bool = False) -> None:
        """Set the parameter value with type validation.

        Args:
            new_value: The new value to set.
            auto_cast: If True, convert string value to native type before
                validation. Useful when setting from user input.

        Raises:
            ParameterValueTypeError: If value is not of expected type.
            ValidationError: If value fails validator checks.
        """
        # auto cast force the value to parameter type before validation
        if auto_cast:
            new_value = self._cast_from_str(new_value)
        # check if value is of expected type
        if not self._is_instance(new_value):
            raise ParameterValueTypeError(
                f"Invalid type, expected {self.get_type()}"
                f" got {type(new_value).__name__}"
            )
        # validation with validators, apply on typed value (int, datetime...)
        self._run_validators(new_value)
        # cast value to string for storage
        str_value = self._cast_to_str(new_value)
        # save to history if enabled
        self._save_history(str_value)
        # finally set the value
        self.value = encrypt_value(str_value) if self.enable_cypher else str_value
        self.save()

    def _run_validators(self, value: Any) -> None:
        """Run all associated validators on the value"""
        for param_validator in self.validators.all():  # type: ignore[attr-defined]
            validator = cast(
                Callable[[Any], None],
                param_validator.get_validator(),  # type: ignore[attr-defined]
            )
            validator(value)

    def _save_history(self, value: Any) -> None:
        """Save current value to history before updating if history is enabled."""
        # Only save to history if:
        # 1. History is enabled
        # 2. Instance has a pk (is saved in DB)
        # 3. Value is different from current value
        if self.enable_history:
            if self.pk:
                current_value = self.get()  # not cyphered
                if current_value != value:
                    logger.info("Saving to history for parameter %s", self.slug)
                    from django_app_parameter.models import ParameterHistory

                    # Save current value to history before updating
                    # if parameter is cyphered, self.value is excpected to be encrypted
                    ParameterHistory.objects.create(
                        parameter=self,
                        value=self.value,  # Save current (old) value
                    )

    def to_dict(self, decrypt: bool = True) -> ParameterDict_:
        """Export this parameter instance to JSON-compatible dictionary.

        Returns:
            Dictionary with all parameter fields and validators.
            Note: The value is exported in decrypted form for portability.
            History entries are NOT exported.
        """
        param_data: ParameterDict_ = {
            "name": self.name,
            "slug": self.slug,
            "value": self._get_decrypted_value(self.value) if decrypt else self.value,
            "value_type": self.value_type,
            "description": self.description,
            "is_global": self.is_global,
            "enable_cypher": self.enable_cypher,
            "enable_history": self.enable_history,
        }

        # Add validators if any
        validators_qs = self.validators.all()  # type: ignore[attr-defined]
        if validators_qs.exists():  # type: ignore[attr-defined]
            validators: list[ValidatorDict] = []
            for validator in validators_qs:  # type: ignore[attr-defined]
                validators.append(
                    {
                        "validator_type": validator.validator_type,  # type: ignore[attr-defined]
                        "validator_params": validator.validator_params,  # type: ignore[attr-defined]
                    }
                )
            param_data["validators"] = validators

        return param_data

    def from_dict(self, data: ParameterDict_, force_encrypt: bool = False) -> None:
        """Update this parameter instance from a dictionary.

        Args:
            data: Dictionary containing parameter fields and optionally validators.
                  The 'slug' and 'value_type' fields are ignored if the instance
                  already exists (has a pk), as they should not be changed.
                  Validators are always processed: if not present in data, existing
                  validators are removed.
                  History entries are NOT imported.
            force_encrypt: If True, the 'value' field in data is treated as
                  unencrypted and will be encrypted if 'enable_cypher' is True.
        """
        value = data.get("value", self.value)
        force_encrypt &= bool(data.get("enable_cypher", self.enable_cypher))

        # Update basic fields
        self.name = data.get("name", self.name)
        self.value = encrypt_value(value) if force_encrypt else value
        self.description = data.get("description", self.description)
        self.is_global = data.get("is_global", self.is_global)
        self.enable_cypher = data.get("enable_cypher", self.enable_cypher)
        self.enable_history = data.get("enable_history", self.enable_history)

        # Only update slug and value_type if instance is new (no pk)
        if not self.pk:
            if "slug" in data:
                self.slug = data["slug"]
            if "value_type" in data:
                self.value_type = data["value_type"]

        # Save the instance
        self.save()

        # Always handle validators to ensure consistency
        # If not present in data, None will clear all validators
        validators_data = data.get("validators", None)
        self._update_validators(validators_data)

    def _update_validators(self, validators_data: list[ValidatorDict] | None) -> None:
        """Update validators for this parameter instance.

        The validators in the data represent the desired final state.
        All existing validators are removed and replaced with the ones from data.
        If validators_data is None or empty, all validators are removed.

        Args:
            validators_data: List of validator definitions, or None
        """
        # Always clear existing validators first to ensure consistency
        logger.info("Clearing existing validators for parameter %s", self.slug)
        existing_validators = self.validators.all()  # type: ignore[attr-defined]
        existing_validators.delete()  # type: ignore[misc]

        # If no validators provided, we're done (validators are already cleared)
        if not validators_data:
            return

        # Create new validators from data
        for validator_data in validators_data:
            validator_type = validator_data.get("validator_type")
            validator_params = validator_data.get("validator_params", {})

            if not validator_type:
                logger.warning(
                    "Skipping validator without validator_type for parameter %s",
                    self.slug,
                )
                continue

            # Create validator
            logger.info(
                "Creating validator %s for parameter %s",
                validator_type,
                self.slug,
            )
            self.validators.create(  # type: ignore[attr-defined]
                validator_type=validator_type,
                validator_params=validator_params,
            )

    def __str__(self) -> str:
        """Return the parameter name as string representation."""
        return self.name


class ParameterValidator(models.Model):
    """Stores validator configuration for a Parameter"""

    parameter = models.ForeignKey(
        Parameter,
        on_delete=models.CASCADE,
        related_name="validators",
        verbose_name="Paramètre",
    )
    validator_type = models.CharField(
        "Type de validateur",
        max_length=400,
        help_text=(
            "Nom du validateur Django intégré ou clé du validateur "
            "custom défini dans DJANGO_APP_PARAMETER['validators']"
        ),
    )
    validator_params = models.JSONField(  # type: ignore[var-annotated]
        "Paramètres du validateur",
        default=dict,
        blank=True,
        help_text=(
            "Paramètres JSON pour instancier le validateur (ex: {'limit_value': 100})"
        ),
    )

    class Meta:
        verbose_name = "Validateur de paramètre"
        verbose_name_plural = "Validateurs de paramètre"

    def get_validator(self) -> Callable[[Any], None]:
        """
        Instantiate and return the validator based on type and params.

        Supports both built-in Django validators and custom validators
        defined in DJANGO_APP_PARAMETER['validators'] setting.

        Returns:
            Callable validator function or instance

        Raises:
            ValueError: If validator_type is not found in built-in or custom validators
        """
        # Get validator class/function from registry (built-in or custom)
        validator_class = get_validator_from_registry(self.validator_type)

        if validator_class is None:
            raise ValueError(
                f"Unknown validator type: {self.validator_type}. "
                f"Check DJANGO_APP_PARAMETER['validators'] setting."
            )

        # Functions like validate_slug don't need instantiation
        if callable(validator_class) and not isinstance(validator_class, type):
            return cast(Callable[[Any], None], validator_class)

        # Class-based validators need instantiation with params
        params: dict[str, Any] = cast(
            dict[str, Any],
            self.validator_params,  # type: ignore[arg-type]
        )
        return cast(Callable[[Any], None], validator_class(**params))

    def __str__(self) -> str:
        """Return parameter name and validator display name."""
        available = get_available_validators()
        display_name = available.get(self.validator_type, self.validator_type)
        return f"{self.parameter.name} - {display_name}"


class ParameterHistory(models.Model):
    """Stores historical values of a Parameter"""

    parameter = models.ForeignKey(
        Parameter,
        on_delete=models.CASCADE,
        related_name="history",
        verbose_name="Paramètre",
    )
    value = models.TextField(
        "Valeur précédente",
        help_text="Valeur du paramètre avant modification",
    )
    modified_at = models.DateTimeField(
        "Date de modification",
        auto_now_add=True,
        help_text="Date et heure de la modification",
    )

    class Meta:
        verbose_name = "Historique de paramètre"
        verbose_name_plural = "Historiques de paramètres"
        ordering = ["-modified_at"]

    def __str__(self) -> str:
        """Return value and modification timestamp."""
        return f"{self.value} - {self.modified_at.strftime('%Y-%m-%d %H:%M:%S')}"


# =============================================================================
# Typed Parameter Proxy Models
# =============================================================================


class ParameterInt(Parameter):
    """Proxy model for integer parameters."""

    type = TYPES.INT

    class Meta:
        proxy = True

    def _cast_from_str(self, value: str) -> int:
        """Convert string to integer."""
        return int(value)

    def _cast_to_str(self, value: int) -> str:
        """Convert integer to string."""
        return str(value)

    def _is_instance(self, value: Any) -> bool:
        """Check if value is an integer."""
        return isinstance(value, int)


class ParameterStr(Parameter):
    """Proxy model for string parameters."""

    class Meta:
        proxy = True


class ParameterFloat(Parameter):
    """Proxy model for float parameters."""

    type = TYPES.FLT

    class Meta:
        proxy = True

    def _cast_from_str(self, value: str) -> float:
        """Convert string to float."""
        return float(value)

    def _is_instance(self, value: Any) -> bool:
        """Check if value is a float."""
        return isinstance(value, float)


class ParameterDecimal(Parameter):
    """Proxy model for Decimal parameters."""

    type = TYPES.DCL

    class Meta:
        proxy = True

    def _cast_from_str(self, value: str) -> Decimal:
        """Convert string to Decimal."""
        return Decimal(value)

    def _is_instance(self, value: Any) -> bool:
        """Check if value is a Decimal."""
        return isinstance(value, Decimal)


class ParameterJson(Parameter):
    """Proxy model for JSON parameters."""

    type = TYPES.JSN

    class Meta:
        proxy = True

    def _cast_from_str(self, value: str) -> Any:
        """Parse JSON string to Python object."""
        return json.loads(value)

    def _cast_to_str(self, value: Any) -> str:
        """Serialize Python object to JSON string."""
        return json.dumps(value)

    def _is_instance(self, value: Any) -> bool:
        """Check if value is JSON-serializable."""
        if not isinstance(value, (dict, list)):
            return False
        try:
            json.dumps(value)
            return True
        except (TypeError, ValueError):
            return False


class ParameterBool(Parameter):
    """Proxy model for boolean parameters."""

    type = TYPES.BOO

    FALSY_VALUES = ["false", "0", "no", "off"]

    class Meta:
        proxy = True

    def _cast_from_str(self, value: str) -> bool:
        """Convert string to boolean. Empty, 'false', '0' are False."""
        if not value or value.lower() in self.FALSY_VALUES:
            return False
        return True

    def _cast_to_str(self, value: bool) -> str:
        """Convert boolean to '1' or '0'."""
        return "1" if value else "0"

    def _is_instance(self, value: Any) -> bool:
        """Check if value is a boolean."""
        return isinstance(value, bool)


class ParameterDate(Parameter):
    """Proxy model for date parameters."""

    type = TYPES.DATE

    class Meta:
        proxy = True

    def _cast_from_str(self, value: str) -> date_type:
        """Parse ISO format string (YYYY-MM-DD) to date."""
        return datetime_type.fromisoformat(value.strip()).date()

    def _cast_to_str(self, value: date_type) -> str:
        """Convert date to ISO format string."""
        return value.isoformat()

    def _is_instance(self, value: Any) -> bool:
        """Check if value is a date (but not datetime)."""
        return isinstance(value, date_type) and not isinstance(value, datetime_type)


class ParameterDatetime(Parameter):
    """Proxy model for datetime parameters."""

    type = TYPES.DATETIME

    class Meta:
        proxy = True

    def _cast_from_str(self, value: str) -> datetime_type:
        """Parse ISO 8601 format string to datetime."""
        return datetime_type.fromisoformat(value.strip())

    def _cast_to_str(self, value: datetime_type) -> str:
        """Convert datetime to ISO 8601 format string."""
        return value.isoformat()

    def _is_instance(self, value: Any) -> bool:
        """Check if value is a datetime."""
        return isinstance(value, datetime_type)


class ParameterTime(Parameter):
    """Proxy model for time parameters."""

    type = TYPES.TIME

    class Meta:
        proxy = True

    def _cast_from_str(self, value: str) -> time_type:
        """Parse HH:MM:SS format string to time."""
        if isinstance(value, time_type):
            return value
        return datetime_type.strptime(value.strip(), "%H:%M:%S").time()

    def _cast_to_str(self, value: time_type) -> str:
        """Convert time to HH:MM:SS format string."""
        return value.strftime("%H:%M:%S")

    def _is_instance(self, value: Any) -> bool:
        """Check if value is a time."""
        return isinstance(value, time_type)


class ParameterUrl(Parameter):
    """Proxy model for URL parameters with validation."""

    type = TYPES.URL

    class Meta:
        proxy = True

    def _cast_from_str(self, value: str) -> str:
        """Validate and return URL string."""
        url_value = value.strip()
        validator = URLValidator()
        try:
            validator(url_value)
        except ValidationError as e:
            raise ValueError(f"Invalid URL: {url_value}") from e
        return url_value

    def _is_instance(self, value: Any) -> bool:
        """Check if value is a valid URL string."""
        if not isinstance(value, str):
            return False
        validator = URLValidator()
        try:
            validator(value)
            return True
        except ValidationError:
            return False


class ParameterEmail(Parameter):
    """Proxy model for email parameters with validation."""

    type = TYPES.EMAIL

    class Meta:
        proxy = True

    def _cast_from_str(self, value: str) -> str:
        """Validate and return email string."""
        email_value = value.strip()
        try:
            validate_email(email_value)
        except ValidationError as e:
            raise ValueError(f"Invalid email: {email_value}") from e
        return email_value

    def _is_instance(self, value: Any) -> bool:
        """Check if value is a valid email string."""
        if not isinstance(value, str):
            return False
        try:
            validate_email(value)
            return True
        except ValidationError:
            return False


class ParameterList(Parameter):
    """Proxy model for comma-separated list parameters."""

    type = TYPES.LIST

    class Meta:
        proxy = True

    def _cast_from_str(self, value: str) -> list[str]:
        """Split comma-separated string into list of strings."""
        value_str = value.strip()
        if not value_str:
            return []
        return [item.strip() for item in value_str.split(",")]

    def _cast_to_str(self, value: list[Any]) -> str:
        """Join list items with comma separator."""
        return ",".join(str(item) for item in value)

    def _is_instance(self, value: Any) -> bool:
        """Check if value is a list."""
        return isinstance(value, list)


class ParameterDict(Parameter):
    """Proxy model for dict parameters (suffixed to avoid conflict with TypedDict)."""

    type = TYPES.DICT

    class Meta:
        proxy = True

    def _cast_from_str(self, value: str) -> dict[str, Any]:
        """Parse JSON string to dict."""
        result = json.loads(value)
        if not isinstance(result, dict):
            raise ValueError(f"Expected dict, got {type(result).__name__}")
        return result  # type: ignore[return-value]

    def _cast_to_str(self, value: dict[str, Any]) -> str:
        """Serialize dict to JSON string."""
        return json.dumps(value)

    def _is_instance(self, value: Any) -> bool:
        """Check if value is a dict."""
        return isinstance(value, dict)


class ParameterPath(Parameter):
    """Proxy model for filesystem path parameters."""

    type = TYPES.PATH

    class Meta:
        proxy = True

    def _cast_from_str(self, value: str) -> Path:
        """Convert string to Path object."""
        return Path(value.strip())

    def _is_instance(self, value: Any) -> bool:
        """Check if value is a Path."""
        return isinstance(value, Path)


class ParameterDuration(Parameter):
    """Proxy model for duration parameters stored as seconds."""

    type = TYPES.DURATION

    class Meta:
        proxy = True

    def _cast_from_str(self, value: str) -> timedelta:
        """Convert seconds string to timedelta."""
        seconds = float(value)
        return timedelta(seconds=seconds)

    def _cast_to_str(self, value: timedelta) -> str:
        """Convert timedelta to total seconds string."""
        return str(value.total_seconds())

    def _is_instance(self, value: Any) -> bool:
        """Check if value is a timedelta."""
        return isinstance(value, timedelta)


class ParameterPercentage(Parameter):
    """Proxy model for percentage parameters (0-100)."""

    type = TYPES.PERCENTAGE

    class Meta:
        proxy = True

    def _cast_from_str(self, value: str) -> float:
        """Convert string to float, validating range 0-100."""
        result = float(value)
        if not 0 <= result <= 100:
            raise ValueError(f"Percentage must be between 0 and 100, got {result}")
        return result

    def _is_instance(self, value: Any) -> bool:
        """Check if value is a float or int."""
        return isinstance(value, (float, int))
