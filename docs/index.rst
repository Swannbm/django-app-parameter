Django App Parameter
====================

**Django App Parameter** is a Django application that enables storing and managing application configuration parameters in the database. It allows non-developers to modify application settings at runtime through the Django admin interface without requiring code deployment or server restarts.

.. image:: https://img.shields.io/pypi/pyversions/django-app-parameter
   :alt: Python Version
   :target: https://pypi.org/project/django-app-parameter/

.. image:: https://img.shields.io/badge/django-4.2%20%7C%205.2-blue
   :alt: Django Version
   :target: https://www.djangoproject.com/

.. image:: https://img.shields.io/pypi/v/django-app-parameter
   :alt: PyPI Version
   :target: https://pypi.org/project/django-app-parameter/

Key Features
------------

- **Database-backed configuration**: Store parameters in your database instead of hardcoded settings
- **Runtime modification**: Change configuration without redeploying or restarting your application
- **Django Admin integration**: Full CRUD operations through the familiar Django admin interface
- **Type safety**: Support for 15+ data types with automatic type conversion
- **Validation**: Built-in Django validators to ensure data integrity
- **Encryption**: Optional encryption for sensitive values (requires cryptography package)
- **History tracking**: Track parameter value changes over time (v2.1.0+)
- **Bulk operations**: Import/export parameters via management commands
- **Template integration**: Access global parameters directly in Django templates

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install django-app-parameter

Configuration
~~~~~~~~~~~~~

Add to your ``INSTALLED_APPS``:

.. code-block:: python

   INSTALLED_APPS = [
       ...
       'django_app_parameter',
   ]

Run migrations:

.. code-block:: bash

   python manage.py migrate

Usage Example
~~~~~~~~~~~~~

.. code-block:: python

   from django_app_parameter import app_parameter

   # Get a parameter value (recommended way)
   max_items = app_parameter.MAX_ITEMS_PER_PAGE  # Returns typed value

   # Alternative: Use the manager with type-safe methods
   from django_app_parameter.models import Parameter

   max_items = Parameter.objects.int("MAX_ITEMS_PER_PAGE", default=10)
   site_name = Parameter.objects.str("SITE_NAME", default="My Site")
   is_enabled = Parameter.objects.bool("FEATURE_ENABLED", default=False)

Documentation
-------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   README
   usage-guide
   management-commands
   faq

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api

.. toctree::
   :maxdepth: 1
   :caption: Development

   changelog
   contributing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
