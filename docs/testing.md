# Guide des tests

Documentation de la stratégie de test et de la couverture de Django App Parameter.

## Vue d'ensemble

Django App Parameter dispose d'une suite de tests complète avec **100% de couverture** utilisant pytest et pytest-django.

**19 tests** répartis en 5 catégories :
- Tests du modèle Parameter
- Tests du manager
- Tests de la commande load_param
- Tests du proxy app_parameter
- Tests du context processor

## Installation

Le projet utilise **Poetry** pour la gestion des dépendances.

```bash
poetry install
```

## Exécution des tests

### Tests de base

```bash
poetry run pytest                    # Tous les tests
poetry run pytest -v                 # Verbeux
poetry run pytest tests/test_django_app_parameter.py::TestParameter  # Classe spécifique

make test                            # Raccourci Makefile (recommandé)
```

### Tests avec couverture

```bash
poetry run pytest --cov=django_app_parameter --cov-report=term-missing
poetry run pytest --cov=django_app_parameter --cov-report=html

make test-cov             # Raccourci (recommandé)
```

La configuration de couverture est dans [pyproject.toml](../pyproject.toml) (`[tool.coverage.*]`).

### Tests multi-versions avec Tox

Tox permet de tester avec différentes versions de Python et Django. Configuration dans [tox.ini](../tox.ini).

```bash
tox                       # Tous les environnements
tox -e py310-django42     # Version spécifique
tox -e ruff               # Formater et vérifier avec Ruff
tox -e coverage           # Vérifier couverture à 100%

make test-all             # Raccourci
```

**Environnements disponibles** : `py{37,38,39,310,311}-django{32,40,41,42}`, `ruff`, `coverage`, `dev`

## Workflow de développement

### Commandes Makefile

```bash
make help                 # Afficher toutes les commandes
make install              # Installer les dépendances
make test                 # Lancer les tests
make test-cov             # Tests avec couverture
make test-all             # Tests multi-versions (tox)
make ruff                 # Formater et vérifier le code (ruff)
make check                # Tout vérifier avant commit
make clean                # Nettoyer les fichiers temporaires
```

### Workflow recommandé

```bash
# 1. Installer
poetry install

# 2. Développer
# ... éditer le code ...

# 3. Formater et vérifier avec Ruff
make ruff

# 4. Tester
make test-cov

# 5. Avant commit (tout vérifier)
make check
```

## Structure des tests

```
django-app-parameter/
├── django_app_parameter/       # Code source
│   ├── models.py
│   ├── admin.py
│   ├── context_processors.py
│   └── management/
└── tests/                      # Tests séparés
    ├── __init__.py
    ├── settings.py            # Configuration Django pour tests
    └── test_django_app_parameter.py  # Suite de tests
```

Les tests utilisent [tests/settings.py](../tests/settings.py) pour configurer un environnement Django minimal avec une base SQLite en mémoire.

## Couverture de code

La configuration est dans [pyproject.toml](../pyproject.toml) (`[tool.coverage.*]`).

```bash
# Générer le rapport
pytest --cov=django_app_parameter --cov-report=html

# Ouvrir le rapport
open htmlcov/index.html
```

**Couverture actuelle** : **100%**

| Module | Coverage |
|--------|----------|
| models.py | 100% |
| admin.py | 100% |
| apps.py | 100% |
| context_processors.py | 100% |
| management/commands/load_param.py | 100% |

## Configuration

### pytest

Configuration dans [pyproject.toml](../pyproject.toml) (`[tool.pytest.ini_options]`) :
- Utilise `tests/settings.py` pour Django
- Cherche les tests dans `tests/`
- Options : `--strict-markers`, `--verbose`, `--reuse-db`

### Django pour les tests

[tests/settings.py](../tests/settings.py) configure :
- Base SQLite en mémoire
- Applications Django minimales
- Context processor pour les tests

### Coverage

Exclut automatiquement :
- Migrations
- Fichiers de tests
- `__pycache__`

## Bonnes pratiques

✅ **DO**
- Maintenir 100% de couverture
- Utiliser des fixtures pour les données de test
- Tester les cas limites et les erreurs
- Lancer `make check` avant chaque commit

❌ **DON'T**
- Ne pas skipper les tests
- Ne pas utiliser la BDD de production
- Ne pas ignorer les warnings

## Ressources

- Code des tests : [tests/test_django_app_parameter.py](../tests/test_django_app_parameter.py)
- [Documentation pytest](https://docs.pytest.org/)
- [Documentation pytest-django](https://pytest-django.readthedocs.io/)
- [Documentation coverage.py](https://coverage.readthedocs.io/)
