# Django-app-parameter

![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13-yellow)
![Django](https://img.shields.io/badge/django-4.2%20LTS%20|%205.2%20LTS-green)
![coverage](https://img.shields.io/badge/coverage-100%25-green)
![version](https://img.shields.io/badge/version-1.1.3-blue)
![ruff](https://img.shields.io/badge/code%20style-ruff-000000)
![pyright](https://img.shields.io/badge/type%20checker-pyright-2A6DB2)
![licence](https://img.shields.io/badge/licence-CC0%201.0%20Universal-purple)

App-Parameter is a very simple Django app to save some application's parameters in the database. Those parameters can be updated by users at run time (no need to new deployment or any restart). It can be used to store the website's title or default e-mail expeditor...

## Prerequisites

- **Python 3.10+** (3.10, 3.11, 3.12, or 3.13)
- **Django 4.2+ LTS** (4.2 LTS or 5.2 LTS)

## Install

    pip install django-app-parameter

## Settings

1. Add "django_app_parameter" to your INSTALLED_APPS setting like this:

```python
INSTALLED_APPS = [
    ...
    "django_app_parameter",
]
```

If you want global parameters to be available in templates, set provided context processor:

```python
TEMPLATES = [
    ...
    "OPTIONS": {
        "context_processors": [
            ...
            "django_app_parameter.context_processors.add_global_parameter_context",
        ],
    },
]
```

2. Run `python manage.py migrate` to create the django_app_parameter's table.

3. Start development server and visit http://127.0.0.1:8000/admin/ to create parameters (you'll need the Admin app enabled).

## Usage

### Add new parameters

Use admin interface to add parameters. You can access a parameter in your code use the "slug" field. Slug is built at first save with: `slugify(self.name).upper().replace("-", "_")`.

Examples:

    self.name     ==> self.slug
    blog title    ==> BLOG_TITLE
    sender e-mail ==> SENDER_E_MAIL
    ##weird@Na_me ==> WERIDNA_ME

See [Django's slugify function](https://docs.djangoproject.com/fr/4.0/ref/utils/#django.utils.text.slugify) for more informations.

### Access parameter in python code

You can read parameter anywhere in your code:

```python
from django.views.generic import TemplateView
from django_app_parameter import app_parameter

class RandomView(TemplateView):
    def get_context_data(self, **kwargs):
        kwargs.update({"blog_title": app_parameter.BLOG_TITLE})
        return super().get_context_data(**kwargs)
```

In case you try to read a non existent parameter, an ImproperlyConfigured exception is raised.

### Access parameter in templates

You can also access "global" parameters from every templates:

```html
<head>
    <title>{{ BLOG_TITLE }}</title>
</head>
```

A to make a parameter global, you only need to check is_global in admin.

### Bulk load parameter with management command

A management command is provided to let you easily load new parameters: `load_param`.

It will create or update, the key for matching is the SLUG.

It accepts 3 parameters: file, json and no-update.

#### Option --file

Add all parameters listed in the provided file.

`load_param --file /path/to/json.file`

Example of file content:

```json
[
    {"name": "hello ze world", "value": "yes", "description": "123", "is_global": true},
    {"slug": "A8B8C", "name": "back on test", "value": "yes", "value_type": "INT" }
]
```

Here all available property you can add to the json:
* name
* slug
* value_type
* value
* description
* is_global

If slug is not provided it will be built. Default value_type is STR (string) and default is_global is False. Name is always required, others properties are optionnals.

#### Option --json

Add parameters in one shot.

`load_param --json "[{'name': 'param1'}, {'name': 'param2'},]"`

The provided json needs to match same rules as for --file option above.

You can't use --json and --file together.

#### Option --no-update

This option is provided to disable 'update' if parameter with same SLUG already exists. It can be used with --json and --file. It's useful to ensure all parameters are created in all environments and can be executed altogether with migrate. It avoid replacing already existing parameters' values which could lead to breaking environments.

`load_param --no-update --file required_parameters.json`

I use it in my starting container script:
```bash
#!/bin/bash

# Execute migrations
python manage.py migrate

# load new parameters if any
python manage.py load_param --no-update --file required_parameters.json

# launch webserver
gunicorn config.wsgi
```

Enjoy.

## Ideas which could come later (or not)

* [] modifications history
* [] Enable cyphering

If you have new idea you would like to see, feel free to open a new issue in this repo.

## Help developing

If you want to participate to the development, there are a few constraints:
* Format all your code with Ruff
* Add type hints and verify with Pyright
* All unit tests must pass and new code must be covered (100% coverage required)

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines.

## Release Process

New versions are automatically published to PyPI via GitHub Actions when a version tag is pushed. See [.github/RELEASE.md](.github/RELEASE.md) for detailed release instructions.

## Why Django-App-Parameter

Because I wanted to try packaging a Django app and I used this one in most of my projects so it seemed a good idea.