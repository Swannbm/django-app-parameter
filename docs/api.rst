API Reference
=============

This section provides detailed API documentation for all modules, classes, and functions in django-app-parameter.

Models
------

The models module contains the core data models for storing parameters, validators, and history.

.. automodule:: django_app_parameter.models
   :members:
   :undoc-members:
   :show-inheritance:

Parameter Model
~~~~~~~~~~~~~~~

.. autoclass:: django_app_parameter.models.Parameter
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __str__

ParameterValidator Model
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: django_app_parameter.models.ParameterValidator
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __str__

ParameterHistory Model
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: django_app_parameter.models.ParameterHistory
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __str__

Admin
-----

The admin module provides Django admin customization for parameter management.

.. automodule:: django_app_parameter.admin
   :members:
   :undoc-members:
   :show-inheritance:

Forms
-----

The forms module provides a flexible system to create form fields adapted to each parameter type.

.. automodule:: django_app_parameter.forms
   :members:
   :undoc-members:
   :show-inheritance:

FieldConfig
~~~~~~~~~~~

.. autoclass:: django_app_parameter.forms.FieldConfig
   :members:
   :undoc-members:
   :show-inheritance:

create_parameter_field
~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: django_app_parameter.forms.create_parameter_field

ParameterCreateForm
~~~~~~~~~~~~~~~~~~~

.. autoclass:: django_app_parameter.forms.ParameterCreateForm
   :members:
   :undoc-members:
   :show-inheritance:

ParameterEditForm
~~~~~~~~~~~~~~~~~

.. autoclass:: django_app_parameter.forms.ParameterEditForm
   :members:
   :undoc-members:
   :show-inheritance:

ParameterValidatorForm
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: django_app_parameter.forms.ParameterValidatorForm
   :members:
   :undoc-members:
   :show-inheritance:

Utilities
---------

The utils module contains helper functions for encryption, slugification, and validator management.

.. automodule:: django_app_parameter.utils
   :members:
   :undoc-members:
   :show-inheritance:

Context Processors
------------------

Template context processor for making global parameters available in templates.

.. automodule:: django_app_parameter.context_processors
   :members:
   :undoc-members:
   :show-inheritance:

Management Commands
-------------------

Command-line tools for importing and exporting parameters.

dap_load
~~~~~~~~

.. automodule:: django_app_parameter.management.commands.dap_load
   :members:
   :undoc-members:
   :show-inheritance:

dap_dump
~~~~~~~~

.. automodule:: django_app_parameter.management.commands.dap_dump
   :members:
   :undoc-members:
   :show-inheritance:

dap_rotate_key
~~~~~~~~~~~~~~

.. automodule:: django_app_parameter.management.commands.dap_rotate_key
   :members:
   :undoc-members:
   :show-inheritance:

AccessParameter Proxy
---------------------

The AccessParameter class provides convenient attribute-style access to parameters.

.. autoclass:: django_app_parameter.AccessParameter
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __getattr__
