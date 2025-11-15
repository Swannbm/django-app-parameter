# Development Tools Migration Plan

## Current Status (2025-11-14)

---

## Remaining Tasks

---

## Phase 7: Documentation automatique avec Sphinx et Read the Docs

### Objectif
Générer automatiquement la documentation à partir du code Python et la publier sur Read the Docs.

### 7.1 Configuration de Sphinx
- [ ] Ajouter les dépendances à `pyproject.toml` (groupe dev) :
  - `sphinx` : moteur de documentation
  - `sphinx-rtd-theme` : thème Read the Docs
  - `sphinx-autodoc-typehints` : documentation des types Python
  - `myst-parser` : support Markdown
- [ ] Initialiser la configuration Sphinx dans `docs/` :
  - Créer `docs/conf.py` avec la configuration
  - Créer `docs/index.rst` (page d'accueil)
  - Créer `docs/api.rst` (documentation API auto-générée)
- [ ] Migrer/intégrer les fichiers Markdown existants :
  - `docs/README.md`
  - `docs/usage-guide.md`
  - `docs/management-commands.md`
  - `docs/faq.md`

### 7.2 Documentation automatique de l'API
- [ ] Configurer `sphinx.ext.autodoc` pour extraire les docstrings
- [ ] Vérifier/améliorer les docstrings existantes dans :
  - `django_app_parameter/models.py`
  - `django_app_parameter/utils.py`
  - `django_app_parameter/admin.py`
  - `django_app_parameter/context_processors.py`
  - Commandes de gestion (`management/commands/`)
- [ ] Créer la structure de documentation API :
  - Documentation des modèles
  - Documentation des fonctions utilitaires
  - Documentation des commandes de gestion

### 7.3 Configuration Read the Docs
- [ ] Créer `.readthedocs.yaml` à la racine du projet
- [ ] Configurer la construction de la documentation :
  - Version Python
  - Dépendances à installer
  - Commande de build Sphinx
- [ ] S'inscrire sur readthedocs.org
- [ ] Importer le projet GitHub
- [ ] Vérifier la première construction

### 7.4 Amélioration de la documentation
- [ ] Ajouter un Makefile pour générer la doc localement
- [ ] Ajouter des exemples de code
- [ ] Créer un changelog intégré
- [ ] Ajouter des badges (ReadTheDocs, Coverage, etc.) au README


