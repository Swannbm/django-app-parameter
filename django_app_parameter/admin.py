from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib import admin
from django.forms import ModelForm
from django.http import HttpRequest

from django_app_parameter.forms import (
    ParameterCreateForm,
    ParameterEditForm,
    ParameterValidatorForm,
    create_parameter_field,
)
from django_app_parameter.models import (
    TYPES,
    Parameter,
    ParameterHistory,
    ParameterValidator,
)

if TYPE_CHECKING:
    from django.contrib.admin import ModelAdmin as BaseModelAdmin
    from django.contrib.admin import TabularInline as BaseTabularInline

    class _ModelAdmin(BaseModelAdmin[Parameter]): ...

    class _TabularInline(BaseTabularInline[ParameterValidator]): ...

    class _HistoryTabularInline(BaseTabularInline[ParameterHistory]): ...
else:
    _ModelAdmin = admin.ModelAdmin
    _TabularInline = admin.TabularInline
    _HistoryTabularInline = admin.TabularInline


class ParameterValidatorInline(_TabularInline):
    """Inline admin for managing validators associated with a Parameter."""

    model = ParameterValidator
    form = ParameterValidatorForm
    extra = 1
    fields = ["validator_type", "validator_params"]


class ParameterHistoryInline(_HistoryTabularInline):
    """Inline admin for displaying parameter history (read-only)."""

    model = ParameterHistory
    extra = 0
    fields = ["value", "modified_at"]
    readonly_fields = ["value", "modified_at"]
    can_delete = False

    def has_add_permission(
        self, request: HttpRequest, obj: Parameter | None = None
    ) -> bool:
        """Prevent adding history entries manually."""
        return False


@admin.register(Parameter)
class ParameterAdmin(_ModelAdmin):
    model = Parameter
    change_form_template = "admin/django_app_parameter/parameter/change_form.html"
    list_display = (
        "name",
        "slug",
        "value",
        "value_type",
        "enable_cypher",
        "enable_history",
    )
    list_filter = ("value_type", "is_global", "enable_cypher", "enable_history")
    search_fields = (
        "name",
        "slug",
        "description",
        "value",
    )
    readonly_fields = ("slug", "value_type")

    def get_inlines(
        self, request: HttpRequest, obj: Parameter | None = None
    ) -> list[type[ParameterValidatorInline] | type[ParameterHistoryInline]]:
        """Show validators and history inlines only when editing."""
        if obj:  # Editing
            return [ParameterValidatorInline, ParameterHistoryInline]
        return []  # Creating - no inlines

    def get_form(
        self,
        request: HttpRequest,
        obj: Parameter | None = None,
        change: bool = False,
        **kwargs: Any,
    ) -> type[ModelForm]:
        """Customize form to use appropriate widget based on value_type."""
        # Use simplified form for creation
        if obj is None:
            kwargs["form"] = ParameterCreateForm
            return super().get_form(request, obj, **kwargs)

        # Use the edit form for updates
        kwargs["form"] = ParameterEditForm
        form_class = super().get_form(request, obj, **kwargs)

        # Customize the value field based on value_type
        form_class.base_fields["value"] = create_parameter_field(obj)  # type: ignore[attr-defined]

        return form_class

    def save_model(
        self, request: HttpRequest, obj: Parameter, form: ModelForm, change: bool
    ) -> None:
        """Handle saving with proper value conversion."""
        if change and "value" in form.cleaned_data:
            # For updates, use the model's set() method
            new_value = form.cleaned_data["value"]
            obj.set(new_value, auto_cast=True)
        else:
            # For new objects, set a default empty value based on type
            if not change:
                # Provide sensible defaults for new parameters
                default_values: dict[str, str] = {
                    TYPES.BOO: "0",
                    TYPES.INT: "0",
                    TYPES.FLT: "0.0",
                    TYPES.DCL: "0",
                    TYPES.STR: "",
                    TYPES.JSN: "{}",
                    TYPES.DICT: "{}",
                    TYPES.LIST: "",
                    TYPES.PERCENTAGE: "0",
                    TYPES.DURATION: "0",
                }
                if not obj.value:
                    obj.value = default_values.get(obj.value_type, "")
            super().save_model(request, obj, form, change)
