# Installation and Configuration

## Prerequisites

- **Python**: 3.7 or higher
- **Django**: 3.2 or higher

## Installation

```bash
pip install django-app-parameter
```

### From Source

```bash
git clone https://github.com/Swannbm/django-app-parameter.git
cd django-app-parameter
pip install -e .
```

## Basic Configuration

### 1. Add to INSTALLED_APPS

Edit your `settings.py` file:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your applications
    'myapp',

    # Django App Parameter
    'django_app_parameter',
]
```

**Important**: Place `django_app_parameter` after Django's base applications to ensure the admin is available.

### 2. Apply Migrations

```bash
python manage.py migrate django_app_parameter
```

## Advanced Configuration (Optional)

### Enable Global Parameters in Templates

If you want to access parameters directly in your Django templates, add the context processor:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # Add this context processor
                'django_app_parameter.context_processors.add_global_parameter_context',
            ],
        },
    },
]
```

**Note**: Only parameters with `is_global=True` will be available in templates.

### Create Default Parameters at App Startup

Create an `initial_parameters.json` file:

```json
[
    {
        "name": "Blog Title",
        "value": "My Awesome Blog",
        "value_type": "STR",
        "is_global": true,
        "description": "Main blog title"
    },
    {
        "name": "Max Upload Size",
        "value": "5242880",
        "value_type": "INT",
        "description": "Max upload size in bytes"
    },
    {
        "name": "Tax Rate",
        "value": "20.00",
        "value_type": "DCL",
        "description": "Tax rate in percentage"
    },
    {
        "name": "Maintenance Mode",
        "value": "false",
        "value_type": "BOO",
        "is_global": true,
        "description": "Enable maintenance mode"
    }
]
```

Add the following command at the same location as your database migration:

```bash
python manage.py load_param --no-update --file initial_parameters.json
```

For example:
```bash
#!/bin/bash
# deploy.sh

# Apply migrations
python manage.py migrate

# Load required parameters without overwriting existing ones
python manage.py load_param --no-update --file config/required_parameters.json

# Collect static files
python manage.py collectstatic --noinput

# Start the application
gunicorn myproject.wsgi
```

## Next Steps

- [Usage Guide with Practical Examples](usage-guide.md)
- [Complete API Reference](api-reference.md)
- [load_param Management Command](management-commands.md)
