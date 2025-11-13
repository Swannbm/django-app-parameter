# Guide de publication

Guide pour publier une nouvelle version de Django App Parameter sur PyPI.

## Prérequis

- Compte PyPI (https://pypi.org/)
- Token d'API PyPI configuré
- Tous les tests passent
- Couverture à 100%
- Code formaté avec Black
- CHANGELOG.md à jour

## Configuration Poetry pour PyPI

### 1. Configurer les credentials PyPI

```bash
# Ajouter le token PyPI
poetry config pypi-token.pypi <votre-token-pypi>

# Vérifier la configuration
poetry config --list
```

### 2. Vérifier les informations du package

Vérifier que [pyproject.toml](../pyproject.toml) contient les bonnes informations :
- `version` : à jour
- `description` : claire et concise
- `authors` : corrects
- `license` : CC0 1.0 Universal
- `repository` : URL GitHub correcte
- `keywords` : pertinents pour PyPI

## Processus de publication

### 1. Préparer la release

```bash
# S'assurer d'être sur master et à jour
git checkout master
git pull

# Vérifier que tout fonctionne
make check

# Tester avec plusieurs versions
make test-all
```

### 2. Mettre à jour la version

Utiliser Poetry pour mettre à jour la version :

```bash
# Incrémenter automatiquement
poetry version patch   # 1.1.3 -> 1.1.4
poetry version minor   # 1.1.3 -> 1.2.0
poetry version major   # 1.1.3 -> 2.0.0

# Ou définir une version spécifique
poetry version 1.2.0
```

Suivre le versioning sémantique (semver) :
- **MAJOR** (1.0.0) : Changements incompatibles
- **MINOR** (0.1.0) : Nouvelles fonctionnalités rétrocompatibles
- **PATCH** (0.0.1) : Corrections de bugs

### 3. Mettre à jour CHANGELOG.md

Ajouter une entrée pour la nouvelle version :

```markdown
## [1.2.0] - 2025-01-XX

### Added
- Nouvelle fonctionnalité X

### Fixed
- Correction du bug Y

### Changed
- Amélioration de Z
```

### 4. Commiter les changements

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to 1.2.0"
git push
```

### 5. Créer un tag Git

```bash
# Créer le tag
git tag v1.2.0

# Pousser le tag
git push origin v1.2.0
```

### 6. Construire le package

```bash
# Nettoyer les anciens builds
make clean

# Construire le package
make build
# ou: poetry build

# Vérifier les fichiers générés dans dist/
ls -lh dist/
```

Cela crée deux fichiers :
- `django-app-parameter-1.2.0.tar.gz` (source)
- `django_app_parameter-1.2.0-py3-none-any.whl` (wheel)

### 7. Publier sur PyPI

```bash
# Publier
make publish
# ou: poetry publish

# Vérifier sur PyPI
# https://pypi.org/project/django-app-parameter/
```

### 8. Créer une release GitHub

1. Aller sur https://github.com/Swannbm/django-app-parameter/releases
2. Cliquer "Draft a new release"
3. Choisir le tag `v1.2.0`
4. Titre : `v1.2.0`
5. Description : Copier depuis CHANGELOG.md
6. Publier

## Test de la publication

Avant de publier en production, tester avec TestPyPI :

```bash
# Configurer TestPyPI
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi <votre-token-testpypi>

# Publier sur TestPyPI
poetry publish -r testpypi

# Tester l'installation
pip install --index-url https://test.pypi.org/simple/ django-app-parameter
```

## Checklist avant publication

- [ ] Tous les tests passent (`make test`)
- [ ] Couverture à 100% (`make test-cov`)
- [ ] Code formaté (`make format`)
- [ ] Linting OK (`make lint`)
- [ ] Tests multi-versions OK (`make test-all`)
- [ ] Version mise à jour dans `pyproject.toml`
- [ ] CHANGELOG.md mis à jour
- [ ] Commits poussés sur `master`
- [ ] Tag Git créé et poussé
- [ ] Package construit (`make build`)
- [ ] Publication réussie (`make publish`)
- [ ] Release GitHub créée
- [ ] Installation depuis PyPI testée

## Vérification post-publication

```bash
# Créer un environnement de test propre
python -m venv test_env
source test_env/bin/activate

# Installer depuis PyPI
pip install django-app-parameter

# Vérifier la version
python -c "import django_app_parameter; print(django_app_parameter.__version__)"

# Nettoyage
deactivate
rm -rf test_env
```

## Rollback en cas de problème

Si une version publiée a des problèmes :

1. **Ne pas supprimer** la version de PyPI (impossible après 24h)
2. Publier rapidement une version patch corrective
3. Marquer la version problématique dans le CHANGELOG

```markdown
## [1.2.1] - 2025-01-XX - HOTFIX

### Fixed
- Correction critique du bug X introduit en 1.2.0

## [1.2.0] - 2025-01-XX - DEPRECATED

**Note** : Cette version contient un bug critique. Utiliser 1.2.1.
```

## Automatisation avec GitHub Actions (optionnel)

Créer `.github/workflows/publish.yml` :

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install Poetry
        run: pip install poetry
      - name: Build and publish
        env:
          PYPI_TOKEN: ${{ secrets.PYPI_TOKEN }}
        run: |
          poetry config pypi-token.pypi $PYPI_TOKEN
          poetry build
          poetry publish
```

## Ressources

- [Poetry Publishing](https://python-poetry.org/docs/libraries/#publishing-to-pypi)
- [Semantic Versioning](https://semver.org/)
- [PyPI](https://pypi.org/)
- [TestPyPI](https://test.pypi.org/)
