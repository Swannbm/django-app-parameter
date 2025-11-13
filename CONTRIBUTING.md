# Guide de contribution

Merci de votre intérêt pour contribuer à Django App Parameter !

## Prérequis

- Python 3.10 ou supérieur
- Poetry
- Git

## Configuration de l'environnement de développement

### 1. Cloner le dépôt

```bash
git clone https://github.com/Swannbm/django-app-parameter.git
cd django-app-parameter
```

### 2. Installer les dépendances

```bash
# Installer les dépendances avec Poetry
poetry install
```

## Workflow de développement

### 1. Créer une branche

```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
# ou
git checkout -b fix/correction-bug
```

### 2. Faire vos modifications

Éditez le code dans `django_app_parameter/`

### 3. Formater et vérifier le code avec Ruff

```bash
# Avec le Makefile (recommandé)
make ruff  # Formater et vérifier le code (avec auto-fix)

# Ou avec Poetry
poetry run ruff format django_app_parameter/  # Formater
poetry run ruff check --fix django_app_parameter/  # Vérifier et corriger
```

### 4. Écrire des tests

Tous les nouveaux codes doivent être couverts par des tests. Ajoutez vos tests dans `tests/test_django_app_parameter.py` ou créez un nouveau fichier de test.

```bash
# Lancer les tests
poetry run pytest

# Avec couverture
poetry run pytest --cov=django_app_parameter --cov-report=term-missing

# Ou avec le Makefile (recommandé)
make test
make test-cov
```

### 5. Tester avec plusieurs versions

Avant de soumettre votre PR, testez avec différentes versions de Python et Django :

```bash
# Installer tox
pip install tox

# Lancer tous les tests
tox

# Ou tester une version spécifique
tox -e py310-django42
```

### 6. Commiter vos changements

```bash
git add .
git commit -m "Description claire de vos changements"
```

### 7. Pousser et créer une Pull Request

```bash
git push origin feature/ma-nouvelle-fonctionnalite
```

Puis créez une Pull Request sur GitHub.

## Standards de code

### Style de code

- **Formatage et linting** : Utilisez Ruff avec les paramètres configurés (88 caractères par ligne)
- **Imports** : Ruff organise automatiquement les imports dans l'ordre : stdlib, packages tiers, imports locaux

### Tests

- **Couverture** : 100% de couverture de code est obligatoire
- **Isolation** : Chaque test doit être indépendant
- **Clarté** : Les noms de tests doivent décrire ce qui est testé
- **Fixtures** : Utilisez des fixtures pytest pour les données de test réutilisables

### Documentation

- **Docstrings** : Ajoutez des docstrings pour les nouvelles fonctions/classes
- **README** : Mettez à jour le README si vous ajoutez de nouvelles fonctionnalités
- **CHANGELOG** : Ajoutez une entrée dans CHANGELOG.md

## Structure du projet

```
django-app-parameter/
├── django_app_parameter/       # Code source
│   ├── __init__.py
│   ├── models.py              # Modèle Parameter
│   ├── admin.py               # Interface admin
│   ├── apps.py
│   ├── context_processors.py  # Context processor pour templates
│   ├── management/
│   │   └── commands/
│   │       └── load_param.py  # Commande de gestion
│   └── migrations/
├── tests/                      # Tests
│   ├── __init__.py
│   ├── settings.py            # Configuration Django pour tests
│   └── test_django_app_parameter.py
├── docs/                       # Documentation
├── pyproject.toml             # Configuration Poetry et outils (Ruff, pytest, coverage)
├── tox.ini                    # Configuration tox
├── README.md
├── CHANGELOG.md
└── CONTRIBUTING.md
```

## Checklist avant de soumettre une PR

- [ ] Le code est formaté avec Ruff (lancez `ruff format django_app_parameter/`)
- [ ] Ruff ne rapporte aucune erreur (lancez `ruff check django_app_parameter/`)
- [ ] Tous les tests passent (lancez `pytest`)
- [ ] La couverture de code est à 100% (lancez `pytest --cov=django_app_parameter --cov-fail-under=100`)
- [ ] Les tests passent avec tox (au moins une version, idéalement toutes)
- [ ] La documentation est à jour
- [ ] Le CHANGELOG est mis à jour
- [ ] Les commits ont des messages clairs

**Astuce** : Vous pouvez lancer `make check` pour vérifier automatiquement le formatage, le linting et les tests.

## Types de contributions acceptées

- 🐛 Corrections de bugs
- ✨ Nouvelles fonctionnalités
- 📝 Améliorations de documentation
- ✅ Ajout de tests
- ♻️ Refactoring
- 🎨 Améliorations d'interface (admin)

## Questions ?

Si vous avez des questions, n'hésitez pas à :
- Ouvrir une issue sur GitHub
- Consulter la [documentation](docs/)
- Regarder les PR existantes pour des exemples

## Licence

En contribuant à ce projet, vous acceptez que vos contributions soient sous la licence CC0 1.0 Universal.
