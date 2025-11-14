from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django import forms
from django.contrib import admin
from django.forms import ModelForm
from django.http import HttpRequest

from django_app_parameter.models import Parameter, ParameterValidator

if TYPE_CHECKING:
    from django.contrib.admin import ModelAdmin as BaseModelAdmin
    from django.contrib.admin import TabularInline as BaseTabularInline

    class _ModelAdmin(BaseModelAdmin[Parameter]): ...

    class _TabularInline(BaseTabularInline[ParameterValidator]): ...
else:
    _ModelAdmin = admin.ModelAdmin
    _TabularInline = admin.TabularInline


class ParameterCreateForm(forms.ModelForm):
    """Form for creating a new Parameter with only essential fields"""

    class Meta:
        model = Parameter
        fields = ["name", "slug", "value_type", "description", "is_global"]
        help_texts = {
            "name": "Nom du paramètre",
            "slug": "Laissez vide pour générer automatiquement depuis le nom",
            "value_type": "Le type ne pourra plus être modifié après création",
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Make slug optional during creation
        if "slug" in self.fields:
            self.fields["slug"].required = False


class ParameterEditForm(forms.ModelForm):
    """Form for editing Parameter with custom validation"""

    class Meta:
        model = Parameter
        fields = ["name", "description", "value", "is_global"]

    def _convert_value_to_type(self, value: Any, value_type: str) -> Any:
        """Convert a value to its appropriate type for validation.

        Args:
            value: The raw value from the form
            value_type: The parameter's value_type

        Returns:
            The value converted to the appropriate type

        Raises:
            ValueError: If conversion fails
            TypeError: If value type is incorrect
        """
        if value_type == Parameter.TYPES.BOO.value:
            return value if isinstance(value, bool) else bool(value)
        elif value_type == Parameter.TYPES.INT.value:
            return value if isinstance(value, int) else int(value)
        elif value_type == Parameter.TYPES.FLT.value:
            return value if isinstance(value, float) else float(value)
        elif value_type == Parameter.TYPES.DCL.value:
            from decimal import Decimal

            return value if isinstance(value, Decimal) else Decimal(str(value))
        elif value_type == Parameter.TYPES.PERCENTAGE.value:
            return value if isinstance(value, int | float) else float(value)
        else:
            # For string-based types, use as-is
            return value

    def clean_value(self) -> Any:
        """Validate the value field using the parameter's validators"""
        value = self.cleaned_data.get("value")
        instance = self.instance

        if not instance or not instance.pk:
            return value

        # Convert string value to the appropriate type for validation
        try:
            typed_value = self._convert_value_to_type(value, instance.value_type)

            # Collect all validation errors
            error_messages: list[Any] = []
            for param_validator in instance.validators.all():
                validator = param_validator.get_validator()
                try:
                    validator(typed_value)
                except Exception as e:
                    # Collect error message as string
                    error_messages.append(str(e))

            # If there are errors, raise them all at once
            if error_messages:
                raise forms.ValidationError(error_messages)

        except (ValueError, TypeError) as e:
            raise forms.ValidationError(
                f"Valeur invalide pour le type {instance.get_value_type_display()}: {e}"
            ) from e

        return value


class ParameterValidatorForm(forms.ModelForm):
    """Form for ParameterValidator with dynamic validator_type choices"""

    class Meta:
        model = ParameterValidator
        fields = ["validator_type", "validator_params"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # Import here to avoid circular imports (utils.py uses Django validators)
        # Build dynamic choices from built-in + custom validators
        from django_app_parameter.utils import get_available_validators

        validators = get_available_validators()
        choices = [("", "--- Sélectionnez un validateur ---")]
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
        """Validate that the validator_type exists in available validators"""
        validator_type = self.cleaned_data.get("validator_type")

        if not validator_type:
            raise forms.ValidationError("Veuillez sélectionner un validateur")

        # Import here to avoid circular imports (utils.py uses Django validators)
        from django_app_parameter.utils import get_available_validators

        available = get_available_validators()
        if validator_type not in available:
            raise forms.ValidationError(
                f"Validateur '{validator_type}' non trouvé. "
                f"Vérifiez DJANGO_APP_PARAMETER['validators']."
            )

        return validator_type


class ParameterValidatorInline(_TabularInline):
    """Inline admin for managing validators associated with a Parameter"""

    model = ParameterValidator
    form = ParameterValidatorForm
    extra = 1
    fields = ["validator_type", "validator_params"]


@admin.register(Parameter)
class ParameterAdmin(_ModelAdmin):
    model = Parameter
    change_form_template = "admin/django_app_parameter/parameter/change_form.html"
    list_display = (
        "name",
        "slug",
        "value",
        "value_type",
    )
    list_filter = ("value_type", "is_global")
    search_fields = (
        "name",
        "slug",
        "description",
        "value",
    )

    def get_readonly_fields(
        self, request: HttpRequest, obj: Parameter | None = None
    ) -> tuple[str, ...]:
        """Make slug and value_type readonly only when editing"""
        del request  # Unused but required by signature
        if obj:  # Editing
            return ("slug", "value_type")
        return ()  # Creating - slug is editable and optional

    def get_inlines(
        self, request: HttpRequest, obj: Parameter | None = None
    ) -> list[type[ParameterValidatorInline]]:
        """Show validators inline only when editing"""
        del request  # Unused but required by signature
        if obj:  # Editing
            return [ParameterValidatorInline]
        return []  # Creating - no inlines

    def _get_field_mapping(
        self,
    ) -> dict[str, type[forms.Field] | type[forms.CharField]]:
        """Get mapping of value types to form field classes.

        Returns:
            Dictionary mapping Parameter.TYPES values to form field classes
        """
        return {
            Parameter.TYPES.BOO.value: forms.BooleanField,
            Parameter.TYPES.INT.value: forms.IntegerField,
            Parameter.TYPES.FLT.value: forms.FloatField,
            Parameter.TYPES.DCL.value: forms.DecimalField,
            Parameter.TYPES.DATE.value: forms.DateField,
            Parameter.TYPES.DATETIME.value: forms.DateTimeField,
            Parameter.TYPES.TIME.value: forms.TimeField,
            Parameter.TYPES.URL.value: forms.URLField,
            Parameter.TYPES.EMAIL.value: forms.EmailField,
            Parameter.TYPES.STR.value: forms.CharField,
            Parameter.TYPES.PATH.value: forms.CharField,
            Parameter.TYPES.DURATION.value: forms.FloatField,
            Parameter.TYPES.PERCENTAGE.value: forms.FloatField,
        }

    def _get_current_value(self, obj: Parameter) -> Any:
        """Get the current value of a parameter in its typed form.

        Args:
            obj: The Parameter instance

        Returns:
            The current value converted to its appropriate type,
            or raw value if conversion fails
        """
        try:
            if obj.value_type == Parameter.TYPES.BOO.value:
                return obj.bool()
            elif obj.value_type == Parameter.TYPES.INT.value:
                return obj.int()
            elif obj.value_type == Parameter.TYPES.FLT.value:
                return obj.float()
            elif obj.value_type == Parameter.TYPES.DCL.value:
                return obj.decimal()
            elif obj.value_type == Parameter.TYPES.DATE.value:
                return obj.date()
            elif obj.value_type == Parameter.TYPES.DATETIME.value:
                return obj.datetime()
            elif obj.value_type == Parameter.TYPES.TIME.value:
                return obj.time()
            elif obj.value_type == Parameter.TYPES.DURATION.value:
                return obj.duration().total_seconds()
            elif obj.value_type == Parameter.TYPES.PERCENTAGE.value:
                return obj.percentage()
            else:
                # For all string-based types
                # (URL, EMAIL, STR, LIST, DICT, JSON, etc.)
                return obj.value
        except (ValueError, TypeError):
            # If there's an error parsing, fall back to raw value
            return obj.value

    def _get_field_for_value_type(
        self,
        obj: Parameter,
        field_mapping: dict[str, type[forms.Field] | type[forms.CharField]],
    ) -> tuple[type[forms.Field] | type[forms.CharField], dict[str, Any]]:
        """Get the appropriate form field class and kwargs for a value type.

        Args:
            obj: The Parameter instance
            field_mapping: Mapping of value types to field classes

        Returns:
            Tuple of (field_class, field_kwargs)
        """
        current_value = self._get_current_value(obj)
        field_kwargs: dict[str, Any] = {
            "required": False,
            "initial": current_value,
        }

        # Special handling for specific types
        if obj.value_type == Parameter.TYPES.JSN.value:
            field_kwargs["widget"] = forms.Textarea(attrs={"rows": 4})
            return forms.CharField, field_kwargs
        elif obj.value_type == Parameter.TYPES.DICT.value:
            field_kwargs["widget"] = forms.Textarea(attrs={"rows": 4})
            return forms.CharField, field_kwargs
        elif obj.value_type == Parameter.TYPES.LIST.value:
            field_kwargs["help_text"] = "Séparez les valeurs par des virgules"
            return forms.CharField, field_kwargs
        elif obj.value_type == Parameter.TYPES.PERCENTAGE.value:
            field_kwargs["min_value"] = 0
            field_kwargs["max_value"] = 100
            field_kwargs["help_text"] = "Valeur entre 0 et 100"
            field_class = field_mapping.get(obj.value_type, forms.CharField)
            return field_class, field_kwargs
        elif obj.value_type == Parameter.TYPES.DURATION.value:
            field_kwargs["help_text"] = "Durée en secondes"
            field_class = field_mapping.get(obj.value_type, forms.CharField)
            return field_class, field_kwargs
        else:
            field_class = field_mapping.get(obj.value_type, forms.CharField)
            return field_class, field_kwargs

    def get_form(
        self,
        request: HttpRequest,
        obj: Parameter | None = None,
        change: bool = False,
        **kwargs: Any,
    ) -> type[ModelForm]:
        """Customize form to use appropriate widget based on value_type"""
        del change  # Unused but required by signature
        # Use simplified form for creation
        if obj is None:
            kwargs["form"] = ParameterCreateForm
            return super().get_form(request, obj, **kwargs)

        # Use the edit form for updates
        kwargs["form"] = ParameterEditForm
        form_class = super().get_form(request, obj, **kwargs)

        # Customize the value field based on value_type
        if obj:  # Editing existing object
            field_mapping = self._get_field_mapping()
            field_class, field_kwargs = self._get_field_for_value_type(
                obj, field_mapping
            )
            # Modify base_fields directly (ModelForm metaclass creates this)
            form_class.base_fields["value"] = field_class(**field_kwargs)  # type: ignore[attr-defined]

        return form_class

    def save_model(
        self, request: HttpRequest, obj: Parameter, form: ModelForm, change: bool
    ) -> None:
        """Handle saving with proper value conversion"""
        if change and "value" in form.cleaned_data:
            # For updates, use the model's set() method
            new_value = form.cleaned_data["value"]
            obj.set(new_value)
        else:
            # For new objects, set a default empty value based on type
            if not change:
                # Provide sensible defaults for new parameters
                default_values = {
                    Parameter.TYPES.BOO.value: "0",
                    Parameter.TYPES.INT.value: "0",
                    Parameter.TYPES.FLT.value: "0.0",
                    Parameter.TYPES.DCL.value: "0",
                    Parameter.TYPES.STR.value: "",
                    Parameter.TYPES.JSN.value: "{}",
                    Parameter.TYPES.DICT.value: "{}",
                    Parameter.TYPES.LIST.value: "",
                    Parameter.TYPES.PERCENTAGE.value: "0",
                    Parameter.TYPES.DURATION.value: "0",
                }
                if not obj.value:
                    obj.value = default_values.get(obj.value_type, "")
            super().save_model(request, obj, form, change)
