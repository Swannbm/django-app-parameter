"""Home view with auto-login for demo purposes."""

from typing import Any

from django.contrib.auth import get_user_model, login
from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView

User = get_user_model()


class HomeView(TemplateView):
    """Home view that auto-logs in the admin user for demo purposes."""

    template_name = "home.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Auto-login admin user if not already authenticated."""
        if not request.user.is_authenticated:
            try:
                admin_user = User.objects.get(username="admin")
                login(request, admin_user)
            except User.DoesNotExist:
                pass  # Admin user doesn't exist yet

        return super().get(request, *args, **kwargs)
