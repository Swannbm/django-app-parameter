from typing import Any

from django.http import HttpRequest

from .models import Parameter


def add_global_parameter_context(request: HttpRequest) -> dict[str, Any]:
    return {
        param.slug: param.get() for param in Parameter.objects.filter(is_global=True)
    }
