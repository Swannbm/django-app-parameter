"""
Django settings for testing django-app-parameter.

This is a minimal Django configuration to run tests in isolation
without requiring a full Django project.
"""

# SECURITY WARNING: keep the secret key used in production secret!
# This is only for testing purposes
SECRET_KEY = "django-insecure-test-key-for-django-app-parameter-testing-only"

# Application definition
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django_app_parameter",
]

# Database
# Use in-memory SQLite database for tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Templates configuration (required for context processor tests)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django_app_parameter.context_processors.add_global_parameter_context",
            ],
        },
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# URL configuration (required for admin views)
ROOT_URLCONF = "tests.urls"

# Middleware (required for sessions and admin)
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Disable migrations for faster tests
# Migrations will be created in memory
USE_TZ = True
