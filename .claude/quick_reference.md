# Quick Reference - Django-App-Parameter

## 🚀 Commandes rapides

### Développement

```bash
# Installation
poetry install

# Environnement virtuel
poetry shell

# Formater le code
make format
# ou
poetry run ruff format .

# Vérifier le code
make check
# ou
poetry run ruff check .
poetry run pyright
poetry run pytest

# Tests
poetry run pytest                                    # Tous les tests
poetry run pytest tests/test_admin.py               # Fichier spécifique
poetry run pytest -k "validator"                    # Par pattern
poetry run pytest --cov=django_app_parameter        # Avec couverture

# Tests multi-versions
tox                                                 # Tous les envs
tox -e py310-django42                              # Env spécifique
tox -p auto                                        # Parallèle

# Démo
cd demo_project
./setup_demo.sh    # Setup (DB fresh)
./run_demo.sh      # Lancer serveur (localhost:8000, admin/admin)
```

### Git workflow

```bash
# Nouvelle fonctionnalité
git checkout -b feat/nom-fonctionnalite
# ... faire les modifications et tests ...
make check
git add .
git commit -m "feat: description de la fonctionnalité"
git push origin feat/nom-fonctionnalite

# Correction de bug
git checkout -b fix/description-bug
# ... écrire test qui reproduit le bug ...
# ... corriger le bug ...
poetry run pytest
git add .
git commit -m "fix: description du bug"
git push origin fix/description-bug
```

## 📚 API Quick Reference

### Accès aux paramètres

```python
# 1. Via proxy (recommandé)
from django_app_parameter import app_parameter
title = app_parameter.BLOG_TITLE  # Auto-converti

# 2. Via Manager
from django_app_parameter.models import Parameter
title = Parameter.objects.str("BLOG_TITLE")
year = Parameter.objects.int("BIRTH_YEAR")

# 3. Objet direct
param = Parameter.objects.get(slug="BLOG_TITLE")
value = param.get()  # Auto-conversion

# 4. Template (globaux uniquement)
# {{ BLOG_TITLE }}
```

### Créer un paramètre

```python
from django_app_parameter.models import Parameter

# Simple
param = Parameter.objects.create(
    name="Blog Title",
    value_type=Parameter.TYPES.STR,
    value="My Awesome Blog"
)

# Avec description et global
param = Parameter.objects.create(
    name="Max Upload Size",
    value_type=Parameter.TYPES.INT,
    value="10485760",  # 10 MB
    description="Maximum file upload size in bytes",
    is_global=False
)

# Avec validateurs
param = Parameter.objects.create(
    name="Age",
    value_type=Parameter.TYPES.INT,
    value="25"
)
param.parametervalidator_set.create(
    validator_type="min_value",
    validator_params={"limit_value": 18}
)
param.parametervalidator_set.create(
    validator_type="max_value",
    validator_params={"limit_value": 120}
)
```

### Modifier un paramètre

```python
# Via setter typé (recommandé - avec validation)
param.set_int(42)
param.set_str("new value")
param.set_bool(True)

# Via setter générique
param.set(42)  # Route vers bon setter

# Via assignation directe (sans validation)
param.value = "42"
param.save()
```

### Types de données

| Code | Type | Exemple valeur | Retour Python |
|------|------|----------------|---------------|
| `STR` | String | `"hello"` | `str` |
| `INT` | Integer | `"42"` | `int` |
| `FLT` | Float | `"3.14"` | `float` |
| `DCL` | Decimal | `"19.99"` | `Decimal` |
| `BOO` | Boolean | `"true"` | `bool` |
| `DAT` | Date | `"2025-01-15"` | `date` |
| `DTM` | DateTime | `"2025-01-15T10:30:00Z"` | `datetime` |
| `TIM` | Time | `"14:30:00"` | `time` |
| `DUR` | Duration | `"3600"` (secondes) | `timedelta` |
| `URL` | URL | `"https://example.com"` | `str` |
| `EML` | Email | `"user@example.com"` | `str` |
| `PCT` | Percentage | `"75"` | `int` |
| `JSN` | JSON | `'{"key": "value"}'` | `dict/list/any` |
| `LST` | List | `"a,b,c"` | `list[str]` |
| `DCT` | Dictionary | `'{"k": "v"}'` | `dict` |
| `PTH` | Path | `"/home/user/file.txt"` | `Path` |

### Validateurs intégrés

```python
# Valeur min/max
"min_value": {"limit_value": 0}
"max_value": {"limit_value": 100}

# Longueur min/max
"min_length": {"limit_value": 3}
"max_length": {"limit_value": 50}

# Regex
"regex": {"regex": r"^\d{5}$", "message": "Code postal invalide"}

# Email
"email": {}

# URL
"url": {}

# Slug
"slug": {}

# IP
"ipv4": {}
"ipv6": {}

# Extension de fichier
"file_extension": {"allowed_extensions": ["jpg", "png", "pdf"]}
```

## 🗂️ Fichiers importants

### Code source

| Fichier | Description | Lignes |
|---------|-------------|--------|
| [models.py](django_app_parameter/models.py) | Modèles Parameter et ParameterValidator | 592 |
| [admin.py](django_app_parameter/admin.py) | Configuration admin Django | 368 |
| [utils.py](django_app_parameter/utils.py) | Registre validateurs et utilitaires | 214 |
| [context_processors.py](django_app_parameter/context_processors.py) | Context processor pour templates | ~20 |

### Tests

| Fichier | Description | Lignes |
|---------|-------------|--------|
| [test_django_app_parameter.py](tests/test_django_app_parameter.py) | Tests modèle et conversions | 2,063 |
| [test_admin.py](tests/test_admin.py) | Tests formulaires admin | 787 |
| [test_admin_views.py](tests/test_admin_views.py) | Tests vues admin | 562 |
| [test_dump_param.py](tests/test_dump_param.py) | Tests commande export | 363 |
| [test_utils.py](tests/test_utils.py) | Tests utilitaires | 308 |
| [test_validators.py](tests/test_validators.py) | Tests validateurs | 75 |

### Configuration

| Fichier | Description |
|---------|-------------|
| [pyproject.toml](pyproject.toml) | Poetry, Ruff, Pyright, Coverage |
| [tox.ini](tox.ini) | Configuration Tox |
| [Makefile](Makefile) | Commandes de dev |
| [.github/workflows/ci.yml](.github/workflows/ci.yml) | CI GitHub Actions |

## 🎨 Patterns de code courants

### Ajouter un nouveau type

```python
# 1. Dans models.py - définir le type
class TYPES(models.TextChoices):
    CUSTOM = "CST", "Custom Type"

# 2. Ajouter dans VALUE_TYPE_CHOICES
VALUE_TYPE_CHOICES = [
    # ...
    (TYPES.CUSTOM, "Custom Type"),
]

# 3. Créer getter
def custom(self) -> CustomType:
    """Getter pour type custom"""
    # logique de conversion
    return converted_value

# 4. Créer setter
def set_custom(self, value: CustomType) -> None:
    """Setter avec validation"""
    if not isinstance(value, CustomType):
        raise TypeError(f"Expected CustomType, got {type(value)}")
    self.value = _str(value)
    self._run_validators()
    self.save()

# 5. Mettre à jour get() et set()
def get(self) -> ParameterReturnType:
    functions = {
        # ...
        self.TYPES.CUSTOM: "custom",
    }
    # ...

# 6. Ajouter méthode Manager
def custom(self, slug: str) -> CustomType:
    return self.get_from_slug(slug).custom()

# 7. Migration
# cd demo_project && poetry run python manage.py makemigrations

# 8. Tests
def test_custom_type(db):
    param = Parameter.objects.create(
        name="Test Custom",
        value_type=Parameter.TYPES.CUSTOM,
        value="custom_value"
    )
    assert param.custom() == expected_result
```

### Ajouter un validateur personnalisé

```python
# 1. Créer validateur (myapp/validators.py)
def validate_custom(value):
    if not is_valid(value):
        raise ValidationError("Invalid value")

# 2. Déclarer dans settings.py
DJANGO_APP_PARAMETER = {
    'validators': {
        'custom_validator': 'myapp.validators.validate_custom',
    }
}

# 3. Utiliser
param.parametervalidator_set.create(
    validator_type="custom_validator",
    validator_params={}
)
```

### Test pattern de base

```python
import pytest
from django_app_parameter.models import Parameter

def test_feature(db):
    """Test description"""
    # Arrange
    param = Parameter.objects.create(
        name="Test",
        value_type=Parameter.TYPES.INT,
        value="42"
    )

    # Act
    result = param.int()

    # Assert
    assert result == 42
```

## 🔍 Debugging rapide

### Problème: Paramètre non trouvé

```python
# Erreur
ImproperlyConfigured: Parameter 'MY_PARAM' does not exist

# Solution
# 1. Vérifier l'admin: http://localhost:8000/admin/django_app_parameter/parameter/
# 2. Créer le paramètre:
Parameter.objects.create(
    name="My Param",
    value_type=Parameter.TYPES.STR,
    value="default"
)
```

### Problème: Conversion échoue

```python
# Erreur
ValueError: Cannot convert 'abc' to int for parameter 'MY_INT'

# Solution
# 1. Vérifier la valeur dans l'admin
# 2. Corriger le type ou la valeur:
param = Parameter.objects.get(slug="MY_INT")
param.value = "42"
param.save()
```

### Problème: Validation échoue

```python
# Erreur
ValidationError: Ensure this value is less than or equal to 100

# Solution
# 1. Vérifier les validateurs:
param = Parameter.objects.get(slug="MY_PARAM")
for v in param.parametervalidator_set.all():
    print(v.validator_type, v.validator_params)

# 2. Modifier ou supprimer validateur via admin
```

### Problème: Tests échouent

```bash
# Lancer tests avec plus d'info
poetry run pytest -vv --tb=long

# Test spécifique avec print()
poetry run pytest tests/test_admin.py::test_name -s

# Avec pdb
poetry run pytest tests/test_admin.py::test_name -s --pdb
```

## 📖 Documentation complète

Pour plus de détails, voir:
- [project_overview.md](.claude/project_overview.md) - Vue d'ensemble complète
- [development_guide.md](.claude/development_guide.md) - Guide de développement détaillé
- [code_patterns.md](.claude/code_patterns.md) - Patterns et conventions
- [testing_guide.md](.claude/testing_guide.md) - Guide de testing complet

Documentation externe:
- [docs/overview.md](docs/overview.md) - Aperçu des fonctionnalités
- [docs/usage-guide.md](docs/usage-guide.md) - Guide d'utilisation
- [docs/management-commands.md](docs/management-commands.md) - Commandes de management
- [README.md](README.md) - Documentation principale

## 🆘 Support

- **Issues GitHub**: https://github.com/Swannbm/django-app-parameter/issues
- **Auteur**: Swann Bouvier-Muller
- **Email**: swann.bm@gmail.com
