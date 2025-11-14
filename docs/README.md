# Django App Parameter

Store configurable application parameters in database. Modify them via Django admin without redeployment.

## Quick Start

```bash
pip install django-app-parameter
```

```python
# settings.py
INSTALLED_APPS += ['django_app_parameter']
```

```bash
python manage.py migrate
```

```python
from django_app_parameter import app_parameter
title = app_parameter.BLOG_TITLE
```

## Documentation

- [Overview](overview.md) - Features and concepts
- [Installation](installation.md) - Setup guide
- [Usage Guide](usage-guide.md) - Examples
- [Management Commands](management-commands.md) - `load_param` command
- [FAQ](faq.md)

## Info

- **Version:** 1.1.3
- **License:** CC0 1.0 Universal
- **Python:** 3.7+
- **Test Coverage:** 100%
- **Repository:** [github.com/Swannbm/django-app-parameter](https://github.com/Swannbm/django-app-parameter)
