from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, TypedDict, cast

from django.core.exceptions import ImproperlyConfigured
from django.db import models

from django_app_parameter.constants import TYPES
from django_app_parameter.utils import (
    parameter_slugify,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from django_app_parameter.models import Parameter


class ValidatorDict(TypedDict):
    """Structure for validator data in JSON export/import"""

    validator_type: str
    validator_params: dict[str, Any]


class ParameterDictRequired(TypedDict):
    """Required fields for ParameterDict"""

    name: str
    slug: str
    value: str
    value_type: str
    description: str
    is_global: bool


class ParameterDict_(ParameterDictRequired, total=False):
    """Structure for parameter data in JSON export/import"""

    validators: list[ValidatorDict]
    enable_cypher: bool
    enable_history: bool


def get_proxy_class(value_type: str) -> type[Parameter]:
    """Get the proxy class for a given value_type, imported lazily"""
    # Import mapping lazily to avoid circular imports
    from django_app_parameter.models import (
        ParameterBool,
        ParameterDate,
        ParameterDatetime,
        ParameterDecimal,
        ParameterDict,
        ParameterDuration,
        ParameterEmail,
        ParameterFloat,
        ParameterInt,
        ParameterJson,
        ParameterList,
        ParameterPath,
        ParameterPercentage,
        ParameterStr,
        ParameterTime,
        ParameterUrl,
    )

    mapping: dict[str, type[Parameter]] = {
        TYPES.INT: ParameterInt,
        TYPES.STR: ParameterStr,
        TYPES.FLT: ParameterFloat,
        TYPES.DCL: ParameterDecimal,
        TYPES.JSN: ParameterJson,
        TYPES.BOO: ParameterBool,
        TYPES.DATE: ParameterDate,
        TYPES.DATETIME: ParameterDatetime,
        TYPES.TIME: ParameterTime,
        TYPES.URL: ParameterUrl,
        TYPES.EMAIL: ParameterEmail,
        TYPES.LIST: ParameterList,
        TYPES.DICT: ParameterDict,
        TYPES.PATH: ParameterPath,
        TYPES.DURATION: ParameterDuration,
        TYPES.PERCENTAGE: ParameterPercentage,
    }
    subclass = mapping.get(value_type)
    if not subclass:
        raise ImproperlyConfigured(f"Unsupported parameter type: {value_type}")
    return subclass


class ParameterQuerySet(models.QuerySet["Parameter"]):
    """QuerySet for Parameter model."""

    pass


class ParameterManager(models.Manager["Parameter"]):
    """Custom manager for Parameter model with typed accessor methods."""

    def get_queryset(self) -> ParameterQuerySet:
        """Return a ParameterQuerySet."""
        return ParameterQuerySet(self.model, using=self._db)

    def create(self, **kwargs: Any) -> Parameter:
        """Create a new Parameter and return it with the correct proxy class."""
        obj = super().create(**kwargs)
        proxy_class = get_proxy_class(obj.value_type)
        if proxy_class is not type(obj):
            obj.__class__ = proxy_class  # type: ignore[assignment]
        return obj

    def get_from_slug(self, slug: str) -> Parameter:
        """Send ImproperlyConfigured exception if parameter is not in DB"""
        try:
            return self.get(slug=slug)
        except self.model.DoesNotExist as e:
            raise ImproperlyConfigured(f"{slug} parameters need to be set") from e

    def load_from_json(self, data: Any, do_update: bool = True) -> None:
        """Load parameters from JSON data.

        Args:
            data: List of parameter dictionaries
            do_update: If True, update existing parameters.
                If False, only create new ones.
        """
        logger.info("load json")
        for param_values in data:
            # Make a copy to avoid modifying the original data
            param_dict = cast(ParameterDict_, dict(param_values))

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

    def dump_to_json(self) -> list[ParameterDict_]:
        """Export all parameters to JSON-compatible format.

        Returns:
            List of parameter dictionaries with all fields and validators
        """
        logger.info("Dumping parameters to JSON")
        result: list[ParameterDict_] = []

        for param in self.all():
            result.append(param.to_dict())

        logger.info("Dumped %d parameters", len(result))
        return result
