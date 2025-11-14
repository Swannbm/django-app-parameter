from typing import TYPE_CHECKING

from django.contrib import admin

if TYPE_CHECKING:
    from .models import Parameter as ParameterModel

from .models import Parameter


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    model = Parameter
    list_display = (
        "name",
        "slug",
        "value",
        "value_type",
    )
    list_filter = ("value_type", "is_global")
    readonly_fields = ("slug",)
    search_fields = (
        "name",
        "slug",
        "description",
        "value",
    )
