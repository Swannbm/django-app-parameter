"""
Sphinx configuration for django-app-parameter documentation.
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path so Sphinx can find the package
sys.path.insert(0, os.path.abspath(".."))

# Configure Django settings for Sphinx autodoc
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django_app_parameter",
        ],
        SECRET_KEY="fake-secret-key-for-sphinx-docs",
    )
    django.setup()

# -- Project information -----------------------------------------------------
project = "django-app-parameter"
copyright = f"{datetime.now().year}, Swann Bouvier-Muller"
author = "Swann Bouvier-Muller"

# The short X.Y version
version = "2.1"
# The full version, including alpha/beta/rc tags
release = "2.1.1"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings.
extensions = [
    "sphinx.ext.autodoc",  # Génère automatiquement la doc depuis les docstrings
    "sphinx.ext.napoleon",  # Support des docstrings Google/NumPy style
    "sphinx.ext.viewcode",  # Ajoute des liens vers le code source
    "sphinx.ext.intersphinx",  # Liens vers d'autres documentations (Django, Python)
    "sphinx.ext.coverage",  # Vérification de la couverture de la documentation
    "sphinx_autodoc_typehints",  # Documentation automatique des type hints
    "myst_parser",  # Support Markdown
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The suffix(es) of source filenames.
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# The master document (table of contents)
master_doc = "index"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.
html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "includehidden": True,
    "titles_only": False,
}

# Add any paths that contain custom static files (such as style sheets)
html_static_path = ["_static"]

# -- Extension configuration -------------------------------------------------

# -- Options for autodoc extension -------------------------------------------
autodoc_default_options = {
    "members": True,  # Documente tous les membres
    "member-order": "bysource",  # Ordre des membres comme dans le code source
    "special-members": "__init__",  # Inclut les __init__
    "undoc-members": True,  # Inclut les membres sans docstring
    "exclude-members": "__weakref__",  # Exclut __weakref__
}

# Don't show type hints in the signature (sphinx-autodoc-typehints les mettra ailleurs)
autodoc_typehints = "description"

# -- Options for intersphinx extension ---------------------------------------

# Liens vers d'autres documentations
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": (
        "https://docs.djangoproject.com/en/stable/",
        "https://docs.djangoproject.com/en/stable/_objects/",
    ),
}

# -- Options for Napoleon extension ------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Options for MyST parser -------------------------------------------------
myst_enable_extensions = [
    "colon_fence",  # Support ::: pour les directives
    "deflist",  # Listes de définitions
    "tasklist",  # Listes de tâches [ ] [x]
]
