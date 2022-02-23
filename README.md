# Django-app-parameter

App-Parameter is a very simple Django app to save application's parameter in the database. Therefor those parameter can be updated by users at running. It can be used to store title of the website, e-mail of the mail expeditor and so on.

Detailed documentation is in the "docs" directory.

## Install

    pip install django-app-parameter

## Quick start

1. Add "app_parameter" to your INSTALLED_APPS setting like this:

    INSTALLED_APPS = [
        ...
        "app_parameter.apps.AppParameterConfig",
    ]

2. Run ``python manage.py migrate`` to create the app_parameter table in models.

3. Start the development server and visit http://127.0.0.1:8000/admin/
   to create parameters (you'll need the Admin app enabled).

## Usage

You can read parameter anywhere in your code. For instance, in a view:

    from app_parameter.models import Parameter

    def send_confirmation_email_view(request):
        from = Parameter.objects.str("TEAM_EMAIL")
        subject = "Alright!"
        ...
        send_email(...)

You can also access "global" parameters from every template (a context processor is included):

    <head>
        <title>{{ BLOG_TITLE }}</title>
    </head>

Use admin interface to add parameters.

## Ideas which could come later (or not)

* A migration process to keep a list of your parameters in a file and automatically add them in each environment
* Shortcut to use Parameter.str(slug) (skip 'objects' key word)
* Check correctness of value on save
* Management command to add a new parameter

## Why Django-App-Parameter

Because I wanted to try to package a Django app and I used this one in most of my projects so it seemed a good idea.