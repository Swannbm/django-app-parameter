"""Forms and field configuration for django-app-parameter.

This module provides a flexible system to create form fields adapted to each
parameter type. It can be used in Django Admin or in any custom form.

Usage in a custom form
----------------------

    from django import forms
    from django_app_parameter.forms import ParameterField
    from django_app_parameter.models import Parameter

    class MySettingsForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            # Dynamically add a field for each parameter
            for param in Parameter.objects.filter(is_global=True):
                self.fields[param.slug] = ParameterField(param)

Usage with a single parameter
-----------------------------

    from django_app_parameter.forms import ParameterField
    from django_app_parameter.models import Parameter

    param = Parameter.objects.get(slug="max-retries")
    field = ParameterField(param)
    # Returns an IntegerField with initial=param.get(), required=False

"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as dataclass_field
from typing import Any

from django import forms

from django_app_parameter.models import TYPES, Parameter, ParameterValidator
from django_app_parameter.utils import get_available_validators

# =============================================================================
# Field Configuration System
# =============================================================================


@dataclass(frozen=True)
class FieldConfig:
    """Configuration for a form field associated with a parameter type.

    Attributes:
        field_class: The Django form field class to use.
        widget: Optional widget instance or class to use.
        extra_kwargs: Additional keyword arguments for field instantiation.
        help_text: Optional help text for the field.
    """

    field_class: type[forms.Field] = forms.CharField
    widget: forms.Widget | type[forms.Widget] | None = None
    extra_kwargs: dict[str, Any] = dataclass_field(default_factory=lambda: {})
    help_text: str = ""


# Registry mapping parameter types to their field configurations
FIELD_TYPE_REGISTRY: dict[str, FieldConfig] = {
    TYPES.STR: FieldConfig(field_class=forms.CharField),
    TYPES.INT: FieldConfig(field_class=forms.IntegerField),
    TYPES.FLT: FieldConfig(field_class=forms.FloatField),
    TYPES.DCL: FieldConfig(field_class=forms.DecimalField),
    TYPES.BOO: FieldConfig(field_class=forms.BooleanField),
    TYPES.DATE: FieldConfig(field_class=forms.DateField),
    TYPES.DATETIME: FieldConfig(field_class=forms.DateTimeField),
    TYPES.TIME: FieldConfig(field_class=forms.TimeField),
    TYPES.URL: FieldConfig(field_class=forms.URLField),
    TYPES.EMAIL: FieldConfig(field_class=forms.EmailField),
    TYPES.PATH: FieldConfig(field_class=forms.CharField),
    TYPES.JSN: FieldConfig(
        field_class=forms.CharField,
        widget=forms.Textarea(attrs={"rows": 4}),
    ),
    TYPES.DICT: FieldConfig(
        field_class=forms.CharField,
        widget=forms.Textarea(attrs={"rows": 4}),
    ),
    TYPES.LIST: FieldConfig(
        field_class=forms.CharField,
        help_text="Séparez les valeurs par des virgules",
    ),
    TYPES.DURATION: FieldConfig(
        field_class=forms.FloatField,
        help_text="Durée en secondes",
    ),
    TYPES.PERCENTAGE: FieldConfig(
        field_class=forms.FloatField,
        extra_kwargs={"min_value": 0, "max_value": 100},
        help_text="Valeur entre 0 et 100",
    ),
}

# Default configuration for unknown types
DEFAULT_FIELD_CONFIG = FieldConfig(field_class=forms.CharField)


def get_field_config_for_type(value_type: str) -> FieldConfig:
    """Get the field configuration for a given parameter type.

    Args:
        value_type: The parameter type (e.g., TYPES.INT, TYPES.STR).

    Returns:
        The FieldConfig for the given type, or DEFAULT_FIELD_CONFIG if unknown.
    """
    return FIELD_TYPE_REGISTRY.get(value_type, DEFAULT_FIELD_CONFIG)


def create_parameter_field(parameter: Parameter, **kwargs: Any) -> forms.Field:
    """Create a form field adapted to a Parameter's value_type.

    This factory function dynamically selects the appropriate field class
    and widget based on the parameter's type.

    Args:
        parameter: The Parameter instance to create a field for.
        **kwargs: Additional keyword arguments passed to the field.
            Common options: required, initial, help_text, widget, label.

    Returns:
        A configured Django form field instance of the appropriate type.

    Example:
        >>> param = Parameter.objects.get(slug="max-retries")
        >>> field = ParameterField(param)
        >>> # Returns an IntegerField if param.value_type == TYPES.INT

        >>> # Override default options
        >>> field = ParameterField(param, required=True, help_text="Custom help")
    """
    config = get_field_config_for_type(parameter.value_type)
    current_value = parameter.get()

    # Build kwargs for field instantiation
    field_kwargs: dict[str, Any] = {
        "required": kwargs.pop("required", False),
        "initial": kwargs.pop("initial", current_value),
        **config.extra_kwargs,
        **kwargs,
    }

    # Add widget if configured (can be overridden by kwargs)
    if "widget" not in field_kwargs and config.widget is not None:
        field_kwargs["widget"] = config.widget

    # Add help_text if configured (can be overridden by kwargs)
    if "help_text" not in field_kwargs and config.help_text:
        field_kwargs["help_text"] = config.help_text

    return config.field_class(**field_kwargs)


# =============================================================================
# Parameter Forms
# =============================================================================


class ParameterCreateForm(forms.ModelForm):
    """Form for creating a new Parameter with only essential fields."""

    class Meta:
        model = Parameter
        fields = [
            "name",
            "slug",
            "value_type",
            "description",
            "is_global",
            "enable_cypher",
            "enable_history",
        ]
        help_texts = {
            "name": "Nom du paramètre",
            "slug": "Laissez vide pour générer automatiquement depuis le nom",
            "value_type": "Le type ne pourra plus être modifié après création",
            "enable_cypher": "Si activé, la valeur sera chiffrée en base de données",
            "enable_history": (
                "Si activé, les modifications de valeur seront enregistrées"
            ),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Make slug optional during creation
        if "slug" in self.fields:
            self.fields["slug"].required = False


class ParameterEditForm(forms.ModelForm):
    """Form for editing Parameter with custom validation."""

    class Meta:
        model = Parameter
        fields = [
            "name",
            "description",
            "value",
            "is_global",
            "enable_cypher",
            "enable_history",
        ]

    def clean_value(self) -> Any:
        """Validate the value field using the parameter's validators."""
        value = self.cleaned_data.get("value")
        instance: Parameter = self.instance

        if not instance or not instance.pk:
            return value

        # Convert string value to the appropriate type for validation
        try:
            instance.set(value, auto_cast=True)
        except (ValueError, TypeError) as e:
            get_value_type_display = getattr(instance, "get_value_type_display", None)
            value_type_display = (
                get_value_type_display()
                if callable(get_value_type_display)
                else str(getattr(instance, "value_type", ""))
            )
            raise forms.ValidationError(
                f"Valeur invalide pour le type {value_type_display}: {e}"
            ) from e

        return value


class ParameterValidatorForm(forms.ModelForm):
    """Form for ParameterValidator with dynamic validator_type choices."""

    class Meta:
        model = ParameterValidator
        fields = ["validator_type", "validator_params"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        validators = get_available_validators()
        choices: list[tuple[str, str]] = [("", "--- Sélectionnez un validateur ---")]
        choices.extend(sorted(validators.items(), key=lambda x: x[1]))

        # Set the field as a ChoiceField with dynamic choices
        self.fields["validator_type"] = forms.ChoiceField(
            choices=choices,
            label="Type de validateur",
            help_text=(
                "Validateur Django intégré ou custom défini dans "
                "DJANGO_APP_PARAMETER['validators']"
            ),
        )

    def clean_validator_type(self) -> str:
        """Validate that the validator_type exists in available validators."""
        validator_type = self.cleaned_data.get("validator_type")

        if not validator_type:
            raise forms.ValidationError("Veuillez sélectionner un validateur")

        available = get_available_validators()
        if validator_type not in available:
            raise forms.ValidationError(
                f"Validateur '{validator_type}' non trouvé. "
                f"Vérifiez DJANGO_APP_PARAMETER['validators']."
            )

        return validator_type
