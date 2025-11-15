from __future__ import annotations

import json
import logging
from collections.abc import Callable
from datetime import date as date_type
from datetime import datetime as datetime_type
from datetime import time as time_type
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, TypedDict, cast

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import URLValidator, validate_email
from django.db import models

from django_app_parameter.utils import (
    decrypt_value,
    encrypt_value,
    get_available_validators,
    get_validator_from_registry,
    parameter_slugify,
)


class ValidatorDict(TypedDict):
    """Structure for validator data in JSON export/import"""

    validator_type: str
    validator_params: dict[str, Any]


class _ParameterDictRequired(TypedDict):
    """Required fields for ParameterDict"""

    name: str
    slug: str
    value: str
    value_type: str
    description: str
    is_global: bool


class ParameterDict(_ParameterDictRequired, total=False):
    """Structure for parameter data in JSON export/import"""

    validators: list[ValidatorDict]
    enable_cypher: bool
    enable_history: bool


logger = logging.getLogger(__name__)


# Type aliasing because there is method name conflict
_str = str
_list = list
_dict = dict
_float = float
_int = int
_bool = bool
_datetime = datetime_type
_time = time_type


class ParameterManager(models.Manager["Parameter"]):
    def get_from_slug(self, slug: _str) -> Parameter:
        """Send ImproperlyConfigured exception if parameter is not in DB"""
        try:
            return super().get(slug=slug)
        except self.model.DoesNotExist as e:
            raise ImproperlyConfigured(f"{slug} parameters need to be set") from e

    def int(self, slug: _str) -> int:
        return self.get_from_slug(slug).int()

    def float(self, slug: _str) -> _float:
        return self.get_from_slug(slug).float()

    def str(self, slug: _str) -> _str:
        return self.get_from_slug(slug).str()

    def decimal(self, slug: _str) -> Decimal:
        return self.get_from_slug(slug).decimal()

    def json(self, slug: _str) -> Any:
        return self.get_from_slug(slug).json()

    def bool(self, slug: _str) -> bool:
        return self.get_from_slug(slug).bool()

    def date(self, slug: _str) -> date_type:
        return self.get_from_slug(slug).date()

    def datetime(self, slug: _str) -> datetime_type:
        return self.get_from_slug(slug).datetime()

    def time(self, slug: _str) -> time_type:
        return self.get_from_slug(slug).time()

    def url(self, slug: _str) -> _str:
        return self.get_from_slug(slug).url()

    def email(self, slug: _str) -> _str:
        return self.get_from_slug(slug).email()

    def list(self, slug: _str) -> _list[_str]:
        return self.get_from_slug(slug).list()

    def dict(self, slug: _str) -> _dict[_str, Any]:
        return self.get_from_slug(slug).dict()

    def path(self, slug: _str) -> Path:
        return self.get_from_slug(slug).path()

    def duration(self, slug: _str) -> timedelta:
        return self.get_from_slug(slug).duration()

    def percentage(self, slug: _str) -> _float:
        return self.get_from_slug(slug).percentage()

    def load_from_json(self, data: Any, do_update: _bool = True) -> None:
        """Load parameters from JSON data.

        Args:
            data: List of parameter dictionaries
            do_update: If True, update existing parameters.
                If False, only create new ones.
        """
        logger.info("load json")
        for param_values in data:
            # Make a copy to avoid modifying the original data
            param_dict = cast(ParameterDict, dict(param_values))

            if "slug" in param_dict:
                slug = param_dict["slug"]
            else:
                slug = parameter_slugify(param_dict["name"])

            if do_update:
                logger.info("Updating parameter %s", slug)
                # Try to get existing parameter or create new one
                try:
                    param = self.get(slug=slug)
                    param.from_dict(param_dict)
                except self.model.DoesNotExist:
                    # Create new parameter
                    param = self.model()
                    param.from_dict(param_dict)
            else:
                logger.info("Adding parameter %s (no update)", slug)
                # Only create if doesn't exist
                try:
                    param = self.get(slug=slug)
                    # Already exists, skip
                except self.model.DoesNotExist:
                    # Create new parameter
                    param = self.model()
                    param.from_dict(param_dict)

    def dump_to_json(self) -> list[ParameterDict]:
        """Export all parameters to JSON-compatible format.

        Returns:
            List of parameter dictionaries with all fields and validators
        """
        logger.info("Dumping parameters to JSON")
        result: list[ParameterDict] = []

        for param in self.all():
            result.append(param.to_dict())

        logger.info("Dumped %d parameters", len(result))
        return result


class Parameter(models.Model):
    objects = ParameterManager()

    class TYPES(models.TextChoices):
        INT = "INT", "Nombre entier"
        STR = "STR", "Chaîne de caractères"
        FLT = "FLT", "Nombre à virgule (Float)"
        DCL = "DCL", "Nombre à virgule (Decimal)"
        JSN = "JSN", "JSON"
        BOO = "BOO", "Booléen"
        DATE = "DAT", "Date (YYYY-MM-DD)"
        DATETIME = "DTM", "Date et heure (ISO 8601)"
        TIME = "TIM", "Heure (HH:MM:SS)"
        URL = "URL", "URL validée"
        EMAIL = "EML", "Email validé"
        LIST = "LST", "Liste (séparée par virgules)"
        DICT = "DCT", "Dictionnaire JSON"
        PATH = "PTH", "Chemin de fichier"
        DURATION = "DUR", "Durée (en secondes)"
        PERCENTAGE = "PCT", "Pourcentage (0-100)"

    name = models.CharField("Nom", max_length=100)
    slug = models.SlugField(max_length=40, unique=True)
    value_type = models.CharField(
        "Type de donnée", max_length=3, choices=TYPES.choices, default=TYPES.STR
    )
    description = models.TextField("Description", blank=True)
    value = models.CharField("Valeur", max_length=250)
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

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            self.slug = parameter_slugify(self.name)
        super().save(*args, **kwargs)

    def _get_raw_value(self) -> _str:
        """
        Get the raw value, decrypting it if enable_cypher is True.

        Returns:
            The decrypted value if enable_cypher is True, otherwise the raw value
        """
        if self.enable_cypher:
            return decrypt_value(self.value)
        return self.value

    def _set_raw_value(self, value: _str) -> None:
        """
        Set the raw value, encrypting it if enable_cypher is True.

        Args:
            value: The plaintext value to store (will be encrypted if needed)
        """
        if self.enable_cypher:
            self.value = encrypt_value(value)
        else:
            self.value = value

    def get(self) -> Any:
        """Return parameter value casted accordingly to its value_type"""
        functions: dict[str, str] = {
            self.TYPES.INT: "int",
            self.TYPES.STR: "str",
            self.TYPES.FLT: "float",
            self.TYPES.DCL: "decimal",
            self.TYPES.JSN: "json",
            self.TYPES.BOO: "bool",
            self.TYPES.DATE: "date",
            self.TYPES.DATETIME: "datetime",
            self.TYPES.TIME: "time",
            self.TYPES.URL: "url",
            self.TYPES.EMAIL: "email",
            self.TYPES.LIST: "list",
            self.TYPES.DICT: "dict",
            self.TYPES.PATH: "path",
            self.TYPES.DURATION: "duration",
            self.TYPES.PERCENTAGE: "percentage",
        }
        function_name = functions.get(self.value_type, "str")
        return getattr(self, function_name)()

    def int(self) -> int:
        """Return parameter value casted as int()"""
        return int(self._get_raw_value())

    def str(self) -> _str:
        """Return parameter value casted as str()"""
        return self._get_raw_value()

    def float(self) -> float:
        """Return parameter value casted as float()"""
        return float(self._get_raw_value())

    def decimal(self) -> Decimal:
        """Return parameter value casted as Decimal()"""
        return Decimal(self._get_raw_value())

    def json(self) -> Any:
        """Return parameter value casted as dict() using json lib"""
        return json.loads(self._get_raw_value())

    def bool(self) -> bool:
        """Return parameter value casted as bool()"""
        raw_value = self._get_raw_value()
        if not raw_value or raw_value.lower() in ["false", "0"]:
            return False
        return bool(raw_value)

    def date(self) -> date_type:
        """Return parameter value casted as date() from ISO format YYYY-MM-DD"""
        return datetime_type.fromisoformat(self._get_raw_value().strip()).date()

    def datetime(self) -> _datetime:
        """Return parameter value casted as datetime() from ISO 8601 format"""
        return _datetime.fromisoformat(self._get_raw_value().strip())

    def time(self) -> _time:
        """Return parameter value casted as time() from HH:MM:SS format"""
        return _datetime.strptime(self._get_raw_value().strip(), "%H:%M:%S").time()

    def url(self) -> _str:
        """Return parameter value validated as URL"""
        url_value = self._get_raw_value().strip()
        validator = URLValidator()
        try:
            validator(url_value)
        except ValidationError as e:
            raise ValueError(f"Invalid URL: {url_value}") from e
        return url_value

    def email(self) -> _str:
        """Return parameter value validated as email"""
        email_value = self._get_raw_value().strip()
        try:
            validate_email(email_value)
        except ValidationError as e:
            raise ValueError(f"Invalid email: {email_value}") from e
        return email_value

    def list(self) -> _list[_str]:
        """Return parameter value as list split by comma"""
        value_str = self._get_raw_value().strip()
        if not value_str:
            return []
        return [item.strip() for item in value_str.split(",")]

    def dict(self) -> _dict[_str, Any]:
        """Return parameter value as dict from JSON"""
        result = json.loads(self._get_raw_value())
        if not isinstance(result, _dict):
            raise ValueError(f"Expected dict, got {type(result).__name__}")
        return result  # type: ignore[return-value]

    def path(self) -> Path:
        """Return parameter value as Path object"""
        return Path(self._get_raw_value().strip())

    def duration(self) -> timedelta:
        """Return parameter value as timedelta from seconds"""
        seconds = _float(self._get_raw_value())
        return timedelta(seconds=seconds)

    def percentage(self) -> _float:
        """Return parameter value as percentage (validated 0-100)"""
        value = _float(self._get_raw_value())
        if not 0 <= value <= 100:
            raise ValueError(f"Percentage must be between 0 and 100, got {value}")
        return value

    def _run_validators(self, value: Any) -> None:
        """Run all associated validators on the value"""
        for param_validator in self.validators.all():  # type: ignore[attr-defined]
            validator = cast(
                Callable[[Any], None],
                param_validator.get_validator(),  # type: ignore[attr-defined]
            )
            validator(value)

    def _save_to_history(self, new_raw_value: _str) -> None:
        """Save current value to history if enable_history is True and value changed.

        Args:
            new_raw_value: The new value to be saved (in raw string format)
        """
        # Only save to history if:
        # 1. History is enabled
        # 2. Instance has a pk (is saved in DB)
        # 3. Value is different from current value
        if self.enable_history and self.pk and self.value != new_raw_value:
            logger.info("Saving to history for parameter %s", self.slug)
            # Import here to avoid circular import
            from django_app_parameter.models import ParameterHistory

            # Save current value to history before updating
            ParameterHistory.objects.create(
                parameter=self,
                value=self.value,  # Save current (old) value
            )

    def set(self, new_value: Any) -> None:
        """Set parameter value with automatic conversion based on value_type"""
        # Run validators before conversion
        self._run_validators(new_value)

        functions: _dict[_str, _str] = {
            self.TYPES.INT: "set_int",
            self.TYPES.STR: "set_str",
            self.TYPES.FLT: "set_float",
            self.TYPES.DCL: "set_decimal",
            self.TYPES.JSN: "set_json",
            self.TYPES.BOO: "set_bool",
            self.TYPES.DATE: "set_date",
            self.TYPES.DATETIME: "set_datetime",
            self.TYPES.TIME: "set_time",
            self.TYPES.URL: "set_url",
            self.TYPES.EMAIL: "set_email",
            self.TYPES.LIST: "set_list",
            self.TYPES.DICT: "set_dict",
            self.TYPES.PATH: "set_path",
            self.TYPES.DURATION: "set_duration",
            self.TYPES.PERCENTAGE: "set_percentage",
        }
        function_name = functions.get(self.value_type, "set_str")
        function = getattr(self, function_name)
        function(new_value)

    def set_int(self, new_value: Any) -> None:
        """Set parameter value from int"""
        if not isinstance(new_value, int):
            raise TypeError(f"Expected int, got {type(new_value).__name__}")
        self._run_validators(new_value)
        new_raw_value = _str(new_value)
        encrypted_value = (
            encrypt_value(new_raw_value) if self.enable_cypher else new_raw_value
        )
        self._save_to_history(encrypted_value)
        self._set_raw_value(new_raw_value)
        self.save()

    def set_str(self, new_value: Any) -> None:
        """Set parameter value from str"""
        if not isinstance(new_value, str):
            raise TypeError(f"Expected str, got {type(new_value).__name__}")
        encrypted_value = encrypt_value(new_value) if self.enable_cypher else new_value
        self._save_to_history(encrypted_value)
        self._set_raw_value(new_value)
        self.save()

    def set_float(self, new_value: Any) -> None:
        """Set parameter value from float"""
        if not isinstance(new_value, float):
            raise TypeError(f"Expected float, got {type(new_value).__name__}")
        new_raw_value = _str(new_value)
        encrypted_value = (
            encrypt_value(new_raw_value) if self.enable_cypher else new_raw_value
        )
        self._save_to_history(encrypted_value)
        self._set_raw_value(new_raw_value)
        self.save()

    def set_decimal(self, new_value: Any) -> None:
        """Set parameter value from Decimal"""
        if not isinstance(new_value, Decimal):
            raise TypeError(f"Expected Decimal, got {type(new_value).__name__}")
        new_raw_value = _str(new_value)
        encrypted_value = (
            encrypt_value(new_raw_value) if self.enable_cypher else new_raw_value
        )
        self._save_to_history(encrypted_value)
        self._set_raw_value(new_raw_value)
        self.save()

    def set_json(self, new_value: Any) -> None:
        """Set parameter value from JSON-serializable object"""
        new_raw_value = json.dumps(new_value)
        encrypted_value = (
            encrypt_value(new_raw_value) if self.enable_cypher else new_raw_value
        )
        self._save_to_history(encrypted_value)
        self._set_raw_value(new_raw_value)
        self.save()

    def set_bool(self, new_value: Any) -> None:
        """Set parameter value from bool"""
        if not isinstance(new_value, bool):
            raise TypeError(f"Expected bool, got {type(new_value).__name__}")
        new_raw_value = "1" if new_value else "0"
        encrypted_value = (
            encrypt_value(new_raw_value) if self.enable_cypher else new_raw_value
        )
        self._save_to_history(encrypted_value)
        self._set_raw_value(new_raw_value)
        self.save()

    def set_date(self, new_value: Any) -> None:
        """Set parameter value from date object"""
        if not isinstance(new_value, date_type):
            raise TypeError(f"Expected date, got {type(new_value).__name__}")
        new_raw_value = new_value.isoformat()
        encrypted_value = (
            encrypt_value(new_raw_value) if self.enable_cypher else new_raw_value
        )
        self._save_to_history(encrypted_value)
        self._set_raw_value(new_raw_value)
        self.save()

    def set_datetime(self, new_value: Any) -> None:
        """Set parameter value from datetime object"""
        if not isinstance(new_value, datetime_type):
            raise TypeError(f"Expected datetime, got {type(new_value).__name__}")
        new_raw_value = new_value.isoformat()
        encrypted_value = (
            encrypt_value(new_raw_value) if self.enable_cypher else new_raw_value
        )
        self._save_to_history(encrypted_value)
        self._set_raw_value(new_raw_value)
        self.save()

    def set_time(self, new_value: Any) -> None:
        """Set parameter value from time object"""
        if not isinstance(new_value, time_type):
            raise TypeError(f"Expected time, got {type(new_value).__name__}")
        new_raw_value = new_value.strftime("%H:%M:%S")
        encrypted_value = (
            encrypt_value(new_raw_value) if self.enable_cypher else new_raw_value
        )
        self._save_to_history(encrypted_value)
        self._set_raw_value(new_raw_value)
        self.save()

    def set_url(self, new_value: Any) -> None:
        """Set parameter value from URL string (validates before saving)"""
        if not isinstance(new_value, str):
            raise TypeError(f"Expected str, got {type(new_value).__name__}")
        url_value = new_value.strip()
        validator = URLValidator()
        try:
            validator(url_value)
        except ValidationError as e:
            raise ValueError(f"Invalid URL: {url_value}") from e
        encrypted_value = encrypt_value(url_value) if self.enable_cypher else url_value
        self._save_to_history(encrypted_value)
        self._set_raw_value(url_value)
        self.save()

    def set_email(self, new_value: Any) -> None:
        """Set parameter value from email string (validates before saving)"""
        if not isinstance(new_value, str):
            raise TypeError(f"Expected str, got {type(new_value).__name__}")
        email_value = new_value.strip()
        try:
            validate_email(email_value)
        except ValidationError as e:
            raise ValueError(f"Invalid email: {email_value}") from e
        encrypted_value = (
            encrypt_value(email_value) if self.enable_cypher else email_value
        )
        self._save_to_history(encrypted_value)
        self._set_raw_value(email_value)
        self.save()

    def set_list(self, new_value: Any) -> None:
        """Set parameter value from list"""
        if not isinstance(new_value, list):
            raise TypeError(f"Expected list, got {type(new_value).__name__}")
        typed_list = cast(_list[Any], new_value)
        new_raw_value = ", ".join(str(item) for item in typed_list)
        encrypted_value = (
            encrypt_value(new_raw_value) if self.enable_cypher else new_raw_value
        )
        self._save_to_history(encrypted_value)
        self._set_raw_value(new_raw_value)
        self.save()

    def set_dict(self, new_value: Any) -> None:
        """Set parameter value from dict"""
        if not isinstance(new_value, dict):
            raise TypeError(f"Expected dict, got {type(new_value).__name__}")
        new_raw_value = json.dumps(new_value)
        encrypted_value = (
            encrypt_value(new_raw_value) if self.enable_cypher else new_raw_value
        )
        self._save_to_history(encrypted_value)
        self._set_raw_value(new_raw_value)
        self.save()

    def set_path(self, new_value: Any) -> None:
        """Set parameter value from Path object"""
        if not isinstance(new_value, Path):
            raise TypeError(f"Expected Path, got {type(new_value).__name__}")
        new_raw_value = _str(new_value)
        encrypted_value = (
            encrypt_value(new_raw_value) if self.enable_cypher else new_raw_value
        )
        self._save_to_history(encrypted_value)
        self._set_raw_value(new_raw_value)
        self.save()

    def set_duration(self, new_value: Any) -> None:
        """Set parameter value from timedelta object"""
        if not isinstance(new_value, timedelta):
            raise TypeError(f"Expected timedelta, got {type(new_value).__name__}")
        new_raw_value = _str(new_value.total_seconds())
        encrypted_value = (
            encrypt_value(new_raw_value) if self.enable_cypher else new_raw_value
        )
        self._save_to_history(encrypted_value)
        self._set_raw_value(new_raw_value)
        self.save()

    def set_percentage(self, new_value: Any) -> None:
        """Set parameter value from percentage (validates 0-100)"""
        if not isinstance(new_value, float | int):
            raise TypeError(f"Expected float or int, got {type(new_value).__name__}")
        if not 0 <= new_value <= 100:
            raise ValueError(f"Percentage must be between 0 and 100, got {new_value}")
        new_raw_value = _str(new_value)
        encrypted_value = (
            encrypt_value(new_raw_value) if self.enable_cypher else new_raw_value
        )
        self._save_to_history(encrypted_value)
        self._set_raw_value(new_raw_value)
        self.save()

    def to_dict(self) -> ParameterDict:
        """Export this parameter instance to JSON-compatible dictionary.

        Returns:
            Dictionary with all parameter fields and validators.
            Note: The value is exported in decrypted form for portability.
            History entries are NOT exported.
        """
        param_data: ParameterDict = {
            "name": self.name,
            "slug": self.slug,
            "value": self._get_raw_value(),  # Export decrypted value
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

    def from_dict(self, data: ParameterDict) -> None:
        """Update this parameter instance from a dictionary.

        Args:
            data: Dictionary containing parameter fields and optionally validators.
                  The 'slug' and 'value_type' fields are ignored if the instance
                  already exists (has a pk), as they should not be changed.
                  Validators are always processed: if not present in data, existing
                  validators are removed.
                  History entries are NOT imported.
        """
        # Update basic fields
        self.name = data.get("name", self.name)
        self.value = data.get("value", self.value)
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

    def __str__(self) -> _str:
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
        params: _dict[_str, Any] = cast(
            _dict[_str, Any],
            self.validator_params,  # type: ignore[arg-type]
        )
        return cast(Callable[[Any], None], validator_class(**params))

    def __str__(self) -> _str:
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
    value = models.CharField(
        "Valeur précédente",
        max_length=250,
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

    def __str__(self) -> _str:
        return f"{self.value} - {self.modified_at.strftime('%Y-%m-%d %H:%M:%S')}"
