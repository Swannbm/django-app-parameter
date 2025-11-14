"""
Example of use:

in views.py:

    from django.views.generic import TemplateView
    from django_app_parameter import app_parameter

    class RandomView(TemplateView):
        def get_context_data(self, **kwargs):
            kwargs.update({"blog_title": app_parameter.BLOG_TITLE})
            return super().get_context_data(**kwargs)
"""

from decimal import Decimal
from typing import Any


class AccessParameter:
    """
    This class is a proxy to mimick Django's settings. You will be able to read
    Parameter value through app_parameter.A_RANDOM_SLUG
    """

    def __getattr__(self, slug: str) -> int | str | float | Decimal | bool | Any:
        from .models import Parameter

        param = Parameter.objects.get_from_slug(slug)  # type: ignore[attr-defined]
        return param.get()  # type: ignore[no-any-return]

    def __setattr__(self, name: str, value: Any) -> None:
        raise Exception("You can't set an app parameter at run time")


app_parameter = AccessParameter()
