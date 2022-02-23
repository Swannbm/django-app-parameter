# Django-app-parameter

App-Parameter is a very simple Django app to save application's parameter in the database. Therefor those parameter can be updated by users at running. It can be used to store title of the website, e-mail of the mail expeditor and so on.

Detailed documentation is in the "docs" directory.

## Install

    pip install django-app-parameter

## Quick start

1. Add "django_app_parameter" to your INSTALLED_APPS setting like this:

    INSTALLED_APPS = [
        ...
        "django_app_parameter",
    ]

If you want to have your global parameter available in template, activate the provided context processor:

    TEMPLATES = [
        ...
        "OPTIONS": {
            "context_processors": [
                ...
                "django_app_parameter.context_processors.add_global_parameter_context",
            ],
        },
    ]

2. Run ``python manage.py migrate`` to create the django_app_parameter table in models.

3. Start the development server and visit http://127.0.0.1:8000/admin/
   to create parameters (you'll need the Admin app enabled).

## Usage

Use admin interface to add parameters. You can access a parameter in your code use the "slug" field. It's built at first save with: slugify(self.name).upper().replace("-", "_"), examples:

```
    self.name     ==> self.slug()
    blog title    ==> BLOG_TITLE
    sender e-mail ==> SENDER_E_MAIL
    ##weird@Na_me ==> WERIDNA_ME
```

See [Django's slugify function](https://docs.djangoproject.com/fr/4.0/ref/utils/#django.utils.text.slugify) for more informations.

You can read parameter anywhere in your code:

    from django_app_parameter.models import Parameter

    def send_confirmation_email_view(request):
        from = Parameter.objects.str("TEAM_EMAIL")
        subject = "Alright!"
        ...
        send_email(...)

You can also access "global" parameters from every templates:

    <head>
        <title>{{ BLOG_TITLE }}</title>
    </head>

## Ideas which could come later (or not)

* A migration process to keep a list of your parameters in a file and automatically add them in each environment
* Shortcut to use Parameter.str(slug) (skip 'objects' key word)
* Check correctness of value on save
* Management command to add a new parameter
* modification history

## Why Django-App-Parameter

Because I wanted to try to package a Django app and I used this one in most of my projects so it seemed a good idea.