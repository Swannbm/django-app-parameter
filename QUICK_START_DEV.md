# Démarrage rapide - Développement

Guide rapide pour démarrer le développement sur Django App Parameter.

## Installation initiale

```bash
# Cloner le projet
git clone https://github.com/Swannbm/django-app-parameter.git
cd django-app-parameter

# Installer les dépendances avec Poetry
poetry install

# Activer l'environnement virtuel
poetry shell
```

## Commandes essentielles

```bash
make help         # Voir toutes les commandes disponibles
make test         # Lancer les tests
make test-cov     # Tests + couverture
make lint         # Vérifier le style
make format       # Formater le code
make check        # Tout vérifier avant commit
```

## Workflow de développement

```bash
# 1. Créer une branche
git checkout -b feature/ma-fonctionnalite

# 2. Développer
# ... éditer le code ...

# 3. Formater
make format

# 4. Tester
make test-cov

# 5. Vérifier tout
make check

# 6. Commiter
git add .
git commit -m "Description"
git push
```

## Structure du projet

```
django-app-parameter/
├── django_app_parameter/    # Code source
├── tests/                   # Tests séparés
│   ├── settings.py         # Config Django pour tests
│   └── test_*.py           # Fichiers de tests
├── docs/                    # Documentation
├── pyproject.toml          # Config Poetry + outils
├── tox.ini                 # Tests multi-versions
├── Makefile                # Raccourcis
└── CONTRIBUTING.md         # Guide de contribution
```

## Documentation

- [Guide de contribution](CONTRIBUTING.md) - Workflow complet
- [Guide des tests](docs/testing.md) - Tests et couverture
- [Guide de publication](docs/publishing.md) - Publier sur PyPI

## Standards

- **Formatage** : Black (88 caractères)
- **Linting** : Flake8
- **Tests** : pytest + pytest-django
- **Couverture** : 100% obligatoire

## Questions ?

Consultez [docs/](docs/) ou ouvrez une issue sur GitHub.
