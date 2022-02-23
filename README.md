# Django-app-parameter

App-Parameter is a very simple Django app to save some application's parameters in the database. Those parameters can be updated by users at running (no need to new deployment or any restart). It can be used to store the website's title or default e-mail expeditor...

## Install

    pip install django-app-parameter

## Settings

1. Add "django_app_parameter" to your INSTALLED_APPS setting like this:

    INSTALLED_APPS = [
        ...
        "django_app_parameter",
    ]

If you want global parameters to be available in templates, set provided context processor:

    TEMPLATES = [
        ...
        "OPTIONS": {
            "context_processors": [
                ...
                "django_app_parameter.context_processors.add_global_parameter_context",
            ],
        },
    ]

2. Run `python manage.py migrate` to create the django_app_parameter's table.

3. Start development server and visit http://127.0.0.1:8000/admin/ to create parameters (you'll need the Admin app enabled).

## Usage

Use admin interface to add parameters. You can access a parameter in your code use the "slug" field. Slug is built at first save with: `slugify(self.name).upper().replace("-", "_")`.

Examples:

    self.name     ==> self.slug
    blog title    ==> BLOG_TITLE
    sender e-mail ==> SENDER_E_MAIL
    ##weird@Na_me ==> WERIDNA_ME

See [Django's slugify function](https://docs.djangoproject.com/fr/4.0/ref/utils/#django.utils.text.slugify) for more informations.

You can read parameter anywhere in your code:

    from django_app_parameter.models import Parameter

    def send_confirmation_email_view(request):
        from = Parameter.objects.str("TEAM_EMAIL")
        subject = "Alright!"
        ...
        send_email(...)

In case you try to read a non existent parameters, an ImproperlyConfigured exception is raised.

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

Because I wanted to try packaging a Django app and I used this one in most of my projects so it seemed a good idea.