# Guide de développement

## 🚀 Configuration de l'environnement

### Prérequis
- Python 3.10 ou supérieur
- Poetry (gestionnaire de dépendances)
- Git

### Installation initiale

```bash
# Cloner le repository
git clone <repository-url>
cd django-app-parameter

# Installer les dépendances avec Poetry
poetry install

# Activer l'environnement virtuel
poetry shell
```

## 🧪 Exécution des tests

### Tests complets
```bash
# Via Poetry
poetry run pytest

# Avec couverture
poetry run pytest --cov=django_app_parameter --cov-report=html --cov-report=term

# Tests spécifiques
poetry run pytest tests/test_admin.py
poetry run pytest tests/test_admin.py::TestParameterAdmin
poetry run pytest tests/test_admin.py::TestParameterAdmin::test_specific_case
```

### Tests multi-versions avec Tox
```bash
# Tous les environnements (8 combinaisons Python/Django)
tox

# Environnement spécifique
tox -e py310-django42
tox -e py313-django52

# Vérifications de qualité
tox -e ruff      # Formatage et lint
tox -e pyright   # Vérification de types
tox -e coverage  # Couverture de tests
```

### Configuration des tests

**Fichier de configuration**: [tests/settings.py](tests/settings.py)
- Base de données: SQLite en mémoire (`:memory:`)
- Apps requis: contenttypes, auth, admin, sessions, messages, django_app_parameter
- Context processor configuré
- Configuration URL pour tests admin

## 🎨 Qualité de code

### Ruff (Linter et Formateur)

```bash
# Formatter le code
poetry run ruff format .

# Vérifier le lint
poetry run ruff check .

# Corriger automatiquement les problèmes
poetry run ruff check --fix .

# Via Makefile
make format
```

**Configuration**: `pyproject.toml`
- Longueur de ligne: 88 caractères
- Target: Python 3.10+
- Règles: pycodestyle (E/W), pyflakes (F), isort (I), flake8-bugbear (B), etc.

### Pyright (Vérification de types)

```bash
# Vérifier les types
poetry run pyright

# Via tox
tox -e pyright
```

**Configuration**: `pyproject.toml`
- Mode strict activé
- Includes: `django_app_parameter/`
- Excludes: migrations, .tox, .venv, dist, build

### Coverage

```bash
# Générer le rapport de couverture
poetry run coverage run -m pytest
poetry run coverage report
poetry run coverage html

# Ouvrir le rapport HTML
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Exigence**: 100% de couverture requis (imposé dans CI)

## 📁 Structure du code source

### [django_app_parameter/models.py](django_app_parameter/models.py) (592 lignes)

**ParameterManager**:
- `get_from_slug(slug)`: Récupère un paramètre ou lève ImproperlyConfigured
- Getters typés: `int()`, `str()`, `float()`, `decimal()`, `bool()`, etc.
- `load_from_json(data, do_update)`: Import en masse depuis JSON
- `dump_to_json()`: Export tous les paramètres en format JSON
- `_handle_validators()`: Gestion des validateurs lors de l'import

**Parameter Model**:
- Génération auto du slug depuis le nom
- Méthodes de conversion pour les 15 types de données
- Méthodes setters avec vérification de type et validation
- `_run_validators()`: Exécute tous les validateurs associés

**ParameterValidator Model**:
- `get_validator()`: Instancie un validateur selon son type et paramètres
- Support validateurs fonction et classe

### [django_app_parameter/admin.py](django_app_parameter/admin.py) (368 lignes)

**ParameterAdmin**:
- Formulaires différents pour création vs édition
- `ParameterCreateForm`: Formulaire simplifié pour nouveaux paramètres
- `ParameterEditForm`: Formulaire complet avec validation
- Champ de valeur dynamique selon `value_type` (ex: BooleanField pour BOO)
- Validateurs en ligne (ParameterValidatorInline)
- Template de formulaire personnalisé
- Champs readonly: slug et value_type (après création)

**ParameterValidatorInline**:
- Inline tabulaire pour gérer les validateurs
- Choix validator_type dynamiques depuis le registre
- Champ JSON pour paramètres du validateur

### [django_app_parameter/utils.py](django_app_parameter/utils.py) (214 lignes)

**Gestion des validateurs**:
- `BUILTIN_VALIDATORS`: Dictionnaire des validateurs Django
- `get_setting()`: Récupère les settings DJANGO_APP_PARAMETER
- `import_validator()`: Import dynamique depuis chemin dotted
- `get_validator_from_registry()`: Lookup avec cache
- `get_available_validators()`: Tous les validateurs avec noms d'affichage
- `clear_validator_cache()`: Reset du cache d'import

### [django_app_parameter/context_processors.py](django_app_parameter/context_processors.py)

```python
def add_global_parameter_context(request):
    return {
        param.slug: param.str()
        for param in Parameter.objects.filter(is_global=True)
    }
```
Rend les paramètres globaux disponibles dans tous les templates (en strings uniquement).

### Commandes de management

**[load_param.py](django_app_parameter/management/commands/load_param.py)**:
- Options: `--file`, `--json`, `--no-update`
- Crée ou met à jour les paramètres par slug
- Support des validateurs en format JSON
- Les validateurs représentent l'état final désiré (remplace existants)

```bash
# Import depuis fichier
python manage.py load_param --file parameters.json

# Import depuis JSON direct
python manage.py load_param --json '[{"name": "Title", ...}]'

# Sans mise à jour des existants
python manage.py load_param --file parameters.json --no-update
```

**[dump_param.py](django_app_parameter/management/commands/dump_param.py)**:
- Export tous les paramètres vers fichier JSON
- Inclut les validateurs pour chaque paramètre
- Option: `--indent` pour formatage JSON

```bash
# Export vers fichier
python manage.py dump_param output.json

# Export avec indentation
python manage.py dump_param output.json --indent 2
```

## 🔄 Workflow de développement

### 1. Créer une nouvelle fonctionnalité

```bash
# Créer une branche
git checkout -b feat/ma-fonctionnalite

# Faire les modifications
# Ajouter les tests correspondants dans tests/

# Vérifier la qualité
make check  # ou poetry run ruff check && poetry run pyright && poetry run pytest

# Commit et push
git add .
git commit -m "feat: ajouter nouvelle fonctionnalité"
git push origin feat/ma-fonctionnalite
```

### 2. Ajouter un nouveau type de données

**Étapes**:
1. Ajouter le type dans `Parameter.TYPES` (models.py)
2. Ajouter les choix dans `VALUE_TYPE_CHOICES`
3. Créer méthode getter `def type_name(self) -> TypeHint:`
4. Créer méthode setter `def set_type_name(self, value: TypeHint) -> None:`
5. Mettre à jour dictionnaire dans `get()` et `set()`
6. Créer migration pour modifier les choix
7. Ajouter tests dans `test_django_app_parameter.py`
8. Ajouter champ de formulaire dans `ParameterEditForm` (admin.py)
9. Mettre à jour la documentation

### 3. Ajouter un validateur intégré

**Dans utils.py**:
```python
from django.core.validators import YourValidator

BUILTIN_VALIDATORS = {
    # ... existants ...
    "your_validator": YourValidator,
}

# Ajouter le nom d'affichage dans get_available_validators()
```

**Tests**:
```python
# Dans tests/test_validators.py
def test_your_validator():
    # Tester l'instanciation et la validation
    pass
```

### 4. Corriger un bug

```bash
# Créer une branche
git checkout -b fix/description-du-bug

# Écrire un test qui reproduit le bug (TDD)
# Fichier: tests/test_*.py

# Vérifier que le test échoue
poetry run pytest tests/test_*.py::test_nom

# Corriger le bug
# Fichier: django_app_parameter/*.py

# Vérifier que le test passe
poetry run pytest tests/test_*.py::test_nom

# Vérifier tous les tests
poetry run pytest

# Commit et push
git add .
git commit -m "fix: corriger le bug X"
git push origin fix/description-du-bug
```

## 📦 Ajout de dépendances

### Dépendances de production

```bash
# Ajouter une dépendance
poetry add nom-package

# Avec version spécifique
poetry add "nom-package>=1.0,<2.0"
```

**⚠️ Important**: Le projet a pour objectif d'avoir **zéro dépendance** en dehors de Django. Toute nouvelle dépendance doit être **fortement justifiée**.

### Dépendances de développement

```bash
# Ajouter une dépendance de dev
poetry add --group dev nom-package

# Exemples
poetry add --group dev pytest-mock
poetry add --group dev django-stubs
```

## 🏗️ Migrations Django

### Créer une migration

```bash
# Depuis le projet de démo
cd demo_project
poetry run python manage.py makemigrations django_app_parameter

# La migration sera créée dans django_app_parameter/migrations/
```

### Conventions de nommage
- Utiliser des noms descriptifs: `0004_add_new_parameter_types.py`
- Documenter les changements dans le docstring de la migration

### Tester les migrations

```bash
# Appliquer les migrations
poetry run python manage.py migrate

# Tester le rollback
poetry run python manage.py migrate django_app_parameter 0003

# Retester la migration forward
poetry run python manage.py migrate django_app_parameter
```

## 🐛 Debugging

### Utiliser le projet de démo

```bash
cd demo_project

# Configuration (base de données fresh à chaque fois)
./setup_demo.sh

# Lancer le serveur
./run_demo.sh

# Accéder à l'admin
# URL: http://127.0.0.1:8000/admin/
# User: admin
# Password: admin
```

### Tests avec pdb/ipdb

```python
# Dans le code de test ou source
import pdb; pdb.set_trace()  # Python standard
# ou
import ipdb; ipdb.set_trace()  # Si ipdb installé

# Exécuter le test
poetry run pytest tests/test_*.py::test_nom -s
```

### Logging

```python
import logging
logger = logging.getLogger(__name__)

# Dans le code
logger.debug("Message de debug")
logger.info("Message d'info")
logger.warning("Attention")
logger.error("Erreur")
```

## 📊 CI/CD

### GitHub Actions

**CI** ([.github/workflows/ci.yml](.github/workflows/ci.yml)):
- Déclenché sur pull requests vers master
- Matrice: Python 3.10-3.13 × Django 4.2, 5.2
- Étapes:
  1. Setup Python
  2. Installation Poetry
  3. Cache venv
  4. Installation des dépendances
  5. Vérification formatage Ruff
  6. Lint Ruff
  7. Vérification types Pyright
  8. Tests Pytest avec couverture
  9. Upload couverture vers Codecov

**Publish** ([.github/workflows/publish.yml](.github/workflows/publish.yml)):
- Publie sur PyPI lors de tags de version
- Processus de release automatisé

### Vérifications locales avant push

```bash
# Exécuter toutes les vérifications
make check

# Ou manuellement
poetry run ruff format .
poetry run ruff check .
poetry run pyright
poetry run pytest --cov=django_app_parameter
```

## 📝 Convention de commits

Utiliser [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: ajout d'une nouvelle fonctionnalité
fix: correction d'un bug
docs: modification de documentation
style: formatage, virgules manquantes, etc.
refactor: refactoring du code
test: ajout ou modification de tests
chore: tâches de maintenance
```

## 🔍 Ressources utiles

- **Documentation Django**: https://docs.djangoproject.com/
- **Poetry**: https://python-poetry.org/docs/
- **Pytest**: https://docs.pytest.org/
- **Ruff**: https://docs.astral.sh/ruff/
- **Pyright**: https://microsoft.github.io/pyright/

## 💡 Tips et bonnes pratiques

1. **Tests d'abord**: Écrire les tests avant le code (TDD)
2. **Couverture 100%**: Maintenir la couverture complète
3. **Type hints**: Ajouter des type hints sur toutes les fonctions publiques
4. **Documentation**: Documenter les fonctions complexes avec docstrings
5. **Commits atomiques**: Un commit = une modification logique
6. **Branches courtes**: Garder les branches de fonctionnalité petites et focalisées
7. **Revue de code**: Demander une revue avant de merger
8. **Tox avant push**: Lancer tox localement avant de pusher
