# Plan de migration des outils de développement

## Contexte
Le projet `django-app-parameter` utilise actuellement:
- **Linter**: Flake8 (configuration dans `.flake8`)
- **Type checker**: Aucun installé explicitement
- **Test runner**: Tests présents (`django_app_parameter/tests.py`) mais framework de test non défini dans les dépendances
- **Gestionnaire de dépendances**: Poetry

## Objectifs
Moderniser la stack d'outils de développement en adoptant:
1. **Ruff** - Linter et formateur Python ultra-rapide (remplace Flake8, Black, isort, etc.)
2. **Pyright** - Type checker statique performant
3. **Pytest** - Framework de test moderne et extensible
4. **Mise à jour des compatibilités** - Supporter les versions maintenues de Python et Django
5. **Chiffrement des données sensibles** - Ajouter le support du chiffrement pour les paramètres confidentiels

### Versions cibles (2025)
- **Python**: 3.10, 3.11, 3.12, 3.13, 3.14 (actuellement: ^3.7)
  - Python 3.7, 3.8, 3.9 ne sont plus maintenus
  - Python 3.10+ sont en support actif
- **Django**: 4.2 LTS (jusqu'à avril 2026) et 5.2 LTS (jusqu'à avril 2028)
  - Django 3.2 LTS n'est plus maintenu depuis avril 2024

## Plan d'action

### Phase 1: Installation de Ruff
- [ ] Ajouter `ruff` aux dépendances de développement dans `pyproject.toml`
- [ ] Configurer Ruff dans `pyproject.toml` (section `[tool.ruff]`)
  - Migrer les règles de Flake8 (max-line-length: 88, exclusions, etc.)
  - Configurer le formateur
  - Configurer les règles de lint
- [ ] Supprimer l'ancienne configuration `.flake8`
- [ ] Tester Ruff sur le code existant
- [ ] Corriger les éventuels problèmes détectés

### Phase 2: Installation de Pyright
- [ ] Ajouter `pyright` aux dépendances de développement
- [ ] Créer la configuration `pyrightconfig.json` ou ajouter section dans `pyproject.toml`
- [ ] Configurer le niveau de vérification (basic/standard/strict)
- [ ] Définir les chemins à analyser et à exclure
- [ ] Tester Pyright sur le code existant
- [ ] Ajouter des annotations de types si nécessaire
- [ ] Corriger les erreurs de typage

### Phase 3: Configuration complète de l'environnement de test avec Pytest
**Note**: Les tests utilisent déjà pytest (voir `django_app_parameter/tests.py`), mais l'environnement n'est pas complètement configuré.

#### 3.1 Installation des dépendances de test
- [ ] Ajouter `pytest` aux dépendances de développement
- [ ] Ajouter `pytest-django` pour l'intégration Django
- [ ] Ajouter `pytest-cov` pour la couverture de code
- [ ] Ajouter Django (version compatible avec Python ^3.7) pour les tests

#### 3.2 Configuration de l'environnement de test Django
- [ ] Créer un mini projet Django pour les tests (structure `tests/` ou configuration directe)
- [ ] Créer `conftest.py` à la racine avec la configuration pytest-django
- [ ] Créer `tests/settings.py` avec les paramètres Django minimaux:
  - Configuration de la base de données (SQLite en mémoire)
  - INSTALLED_APPS avec django_app_parameter
  - SECRET_KEY
  - Autres paramètres Django requis
- [ ] Configurer le DJANGO_SETTINGS_MODULE

#### 3.3 Configuration de Pytest
- [ ] Configurer Pytest dans `pyproject.toml` (section `[tool.pytest.ini_options]`):
  - Définir le DJANGO_SETTINGS_MODULE
  - Définir les chemins de test
  - Configurer les markers Django
  - Configurer les options de couverture
- [ ] Migrer/remplacer `.coveragerc` vers `pyproject.toml`

#### 3.4 Vérification et exécution des tests
- [ ] Créer/appliquer les migrations dans l'environnement de test
- [ ] Exécuter les tests existants avec pytest
- [ ] Vérifier que tous les tests passent
- [ ] Générer un rapport de couverture de code
- [ ] Corriger les éventuels problèmes

### Phase 4: Mise à jour des compatibilités Python et Django

#### 4.1 Mise à jour de la compatibilité Python
- [ ] Mettre à jour `pyproject.toml` pour supporter Python ^3.10 (au lieu de ^3.7)
- [ ] Vérifier le code pour les fonctionnalités obsolètes de Python 3.7-3.9
- [ ] Tester avec Python 3.10, 3.11, 3.12, 3.13
- [ ] Mettre à jour les classifiers dans `pyproject.toml`:
  ```toml
  Programming Language :: Python :: 3.10
  Programming Language :: Python :: 3.11
  Programming Language :: Python :: 3.12
  Programming Language :: Python :: 3.13
  ```
- [ ] Documenter les versions Python supportées

#### 4.2 Mise à jour de la compatibilité Django
- [ ] Ajouter Django dans les dépendances (actuellement non spécifié)
- [ ] Définir le support pour Django 4.2 LTS et 5.2 LTS
- [ ] Tester l'app avec Django 4.2 et 5.2
- [ ] Vérifier les APIs Django utilisées pour les changements breaking
- [ ] Mettre à jour les classifiers:
  ```toml
  Framework :: Django :: 4.2
  Framework :: Django :: 5.0
  Framework :: Django :: 5.1
  Framework :: Django :: 5.2
  ```

#### 4.3 Configuration de la matrice de test
- [ ] Configurer tox ou nox pour tester plusieurs versions:
  - Python: 3.10, 3.11, 3.12, 3.13
  - Django: 4.2, 5.2
- [ ] Créer une matrice de compatibilité dans le README
- [ ] Documenter les combinaisons testées et supportées

### Phase 5: Configuration de la CI/CD (GitHub Actions)

#### 5.1 CI pour les tests et la qualité du code
- [ ] Créer `.github/workflows/test.yml`
- [ ] Configurer la matrice de test (Python 3.10-3.13 × Django 4.2, 5.2)
- [ ] Ajouter les jobs:
  - Linting avec Ruff
  - Type checking avec Pyright
  - Tests avec Pytest sur toutes les combinaisons
  - Rapport de couverture (upload vers Codecov ou Coveralls)
- [ ] Configurer les badges de statut dans le README

#### 5.2 CI pour la publication Docker
- [ ] Créer `.github/workflows/docker-publish.yml`
- [ ] Configurer le déclenchement:
  - Sur push de tags (ex: v1.2.0)
  - Sur release GitHub
- [ ] Étapes du workflow:
  - Build de l'image Docker
  - Tag avec la version (depuis git tag ou pyproject.toml)
  - Push vers Docker Hub ou GitHub Container Registry
  - Création de tags multiples (latest, version, version-major)
- [ ] Créer le `Dockerfile` si nécessaire
- [ ] Configurer les secrets GitHub:
  - `DOCKER_USERNAME`
  - `DOCKER_TOKEN` ou `GITHUB_TOKEN`

#### 5.3 CI pour la publication PyPI (bonus)
- [ ] Créer `.github/workflows/publish-pypi.yml` (optionnel)
- [ ] Configurer la publication automatique sur PyPI lors des releases
- [ ] Utiliser Poetry pour le build et la publication
- [ ] Configurer le secret `PYPI_TOKEN`

### Phase 6: Ajout du chiffrement des données sensibles

#### 6.1 Conception de la fonctionnalité de chiffrement
- [ ] Choisir la bibliothèque de chiffrement (cryptography recommandée)
- [ ] Définir l'architecture:
  - Chiffrement symétrique (AES-256)
  - Clé de chiffrement stockée dans Django settings
  - Champ `is_encrypted` dans le modèle Parameter
  - Chiffrement/déchiffrement transparent lors des get/set
- [ ] Planifier la migration pour ajouter le champ `is_encrypted`

#### 6.2 Implémentation du chiffrement
- [ ] Ajouter `cryptography` aux dépendances
- [ ] Créer un module `encryption.py` avec les fonctions:
  - `encrypt_value(value: str, key: str) -> str`
  - `decrypt_value(encrypted_value: str, key: str) -> str`
  - `get_encryption_key()` - récupère la clé depuis settings
- [ ] Ajouter le champ `is_encrypted` au modèle Parameter (BooleanField)
- [ ] Créer la migration Django
- [ ] Modifier les méthodes du modèle:
  - `save()` - chiffrer si `is_encrypted=True`
  - `get()` - déchiffrer automatiquement si nécessaire
  - `str()`, `int()`, `float()`, etc. - support du déchiffrement

#### 6.3 Configuration et sécurité
- [ ] Ajouter le paramètre dans settings:
  ```python
  # settings.py
  APP_PARAMETER_ENCRYPTION_KEY = env('APP_PARAMETER_ENCRYPTION_KEY')
  ```
- [ ] Documenter la génération de la clé de chiffrement:
  ```python
  from cryptography.fernet import Fernet
  key = Fernet.generate_key()
  ```
- [ ] Ajouter des validations:
  - Vérifier que la clé existe si `is_encrypted=True`
  - Gérer les erreurs de déchiffrement
- [ ] Ajouter un avertissement si la clé n'est pas définie

#### 6.4 Tests du chiffrement
- [ ] Créer des tests pour le chiffrement/déchiffrement
- [ ] Tester la sauvegarde de valeurs chiffrées
- [ ] Tester la récupération de valeurs chiffrées
- [ ] Tester les erreurs (clé manquante, valeur corrompue)
- [ ] Tester la compatibilité avec tous les types (str, int, float, json, etc.)
- [ ] Tester la migration de données existantes

#### 6.5 Documentation du chiffrement
- [ ] Documenter l'utilisation dans le README:
  - Comment générer une clé
  - Comment configurer la clé dans les settings
  - Comment créer un paramètre chiffré
  - Exemples d'utilisation
- [ ] Ajouter des exemples de code
- [ ] Documenter les bonnes pratiques de sécurité
- [ ] Ajouter une section "Security" dans le README

### Phase 7: Nettoyage et documentation
- [ ] Mettre à jour le README avec les nouvelles commandes
- [ ] Ajouter les badges CI/CD dans le README
- [ ] Nettoyer les fichiers de configuration obsolètes (.flake8, .coveragerc)
- [ ] Documenter les commandes pour les développeurs:
  ```bash
  # Linting et formatage
  ruff check .
  ruff format .

  # Type checking
  pyright

  # Tests
  pytest
  pytest --cov=django_app_parameter

  # Installation pour le développement
  poetry install
  ```
- [ ] Mettre à jour le CHANGELOG.md avec toutes les modifications

## Notes importantes
- **Python actuel**: ^3.7 → **Cible**: ^3.10 (versions maintenues en 2025)
- **Django**: Pas de version spécifiée → **Cible**: Support Django 4.2 LTS et 5.2 LTS
- Les migrations Django sont exclues du linting (à conserver)
- Configuration actuelle de Flake8: max-line-length=88, ignore E203,W503
- Des tests existent déjà dans `django_app_parameter/tests.py` utilisant pytest
- Tests actuels: 19 tests couvrant les modèles, managers, commandes et context processors
- Fichier de test de données: `django_app_parameter/data_for_test.json`
- **Nouveau**: CI/CD pour publication automatique Docker sur tags/releases

## Structure de test recommandée
```
django-app-parameter/
├── conftest.py                    # Configuration pytest principale
├── tests/
│   ├── __init__.py
│   ├── settings.py                # Settings Django pour les tests
│   └── manage.py                  # (optionnel) Script de gestion Django
├── django_app_parameter/
│   ├── tests.py                   # Tests existants (à conserver)
│   └── data_for_test.json         # Données de test
└── pyproject.toml                 # Configuration centralisée
```

## Prochaines étapes
Commencer par la Phase 1: Installation et configuration de Ruff