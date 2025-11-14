# Installation

## Prerequisites

- **Python 3.10+** (3.10, 3.11, 3.12, or 3.13)
- **Django 4.2+ LTS** (4.2 LTS or 5.2 LTS)

## Install

```bash
pip install django-app-parameter
```

## Configure

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'django_app_parameter',  # After Django base apps
]
```

```bash
python manage.py migrate
```

## Optional: Templates

Add context processor for global parameters in templates:

```python
# settings.py
TEMPLATES = [{
    'OPTIONS': {
        'context_processors': [
            # ...
            'django_app_parameter.context_processors.add_global_parameter_context',
        ],
    },
}]
```

Only `is_global=True` parameters available.

## Optional: Initial Parameters

Create `initial_parameters.json`:

```json
[
    {
        "name": "Blog Title",
        "value": "My Blog",
        "value_type": "STR",
        "is_global": true
    }
]
```

Load in deployment:

```bash
python manage.py migrate
python manage.py load_param --no-update --file initial_parameters.json
python manage.py collectstatic --noinput
```

See [management-commands.md](management-commands.md) for details.

## Next

- [Usage Guide](usage-guide.md)
- [Management Commands](management-commands.md)
