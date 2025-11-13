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

# Activer l'environnement virtuel
poetry shell
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

### 3. Formater le code avec Black

```bash
# Formater tous les fichiers
black django_app_parameter/

# Ou avec le Makefile
make format
```

### 4. Vérifier le linting avec flake8

```bash
# Vérifier le style du code
flake8 django_app_parameter/

# Ou avec le Makefile
make lint
```

### 5. Écrire des tests

Tous les nouveaux codes doivent être couverts par des tests. Ajoutez vos tests dans `tests/test_django_app_parameter.py` ou créez un nouveau fichier de test.

```bash
# Lancer les tests
pytest

# Avec couverture
pytest --cov=django_app_parameter --cov-report=term-missing

# La couverture doit rester à 100%
pytest --cov=django_app_parameter --cov-report=term-missing --cov-fail-under=100
```

### 6. Tester avec plusieurs versions

Avant de soumettre votre PR, testez avec différentes versions de Python et Django :

```bash
# Installer tox
pip install tox

# Lancer tous les tests
tox

# Ou tester une version spécifique
tox -e py310-django42
```

### 7. Commiter vos changements

```bash
git add .
git commit -m "Description claire de vos changements"
```

### 8. Pousser et créer une Pull Request

```bash
git push origin feature/ma-nouvelle-fonctionnalite
```

Puis créez une Pull Request sur GitHub.

## Standards de code

### Style de code

- **Formatage** : Utilisez Black avec les paramètres par défaut (88 caractères par ligne)
- **Linting** : Le code doit passer flake8 sans erreurs
- **Imports** : Organisez les imports dans l'ordre : stdlib, packages tiers, imports locaux

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
├── pyproject.toml             # Configuration Poetry et outils
├── tox.ini                    # Configuration tox
├── .flake8                    # Configuration flake8
├── README.md
├── CHANGELOG.md
└── CONTRIBUTING.md
```

## Checklist avant de soumettre une PR

- [ ] Le code suit le style Black (lancez `black django_app_parameter/`)
- [ ] Flake8 ne rapporte aucune erreur (lancez `flake8 django_app_parameter/`)
- [ ] Tous les tests passent (lancez `pytest`)
- [ ] La couverture de code est à 100% (lancez `pytest --cov=django_app_parameter --cov-fail-under=100`)
- [ ] Les tests passent avec tox (au moins une version, idéalement toutes)
- [ ] La documentation est à jour
- [ ] Le CHANGELOG est mis à jour
- [ ] Les commits ont des messages clairs

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
