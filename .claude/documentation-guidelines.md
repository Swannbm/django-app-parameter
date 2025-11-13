# Guidelines de documentation pour django-app-parameter

Ce document résume les bonnes pratiques de rédaction de documentation pour ce projet, basées sur les retours utilisateur.

## Principes généraux

### 1. Éviter la redondance avec le code

❌ **Ne pas faire** : Recopier le code dans la documentation

```markdown
### Configuration pytest

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "tests.settings"
python_files = ["tests.py", "test_*.py"]
# ... tout le contenu de pyproject.toml
```
```

✅ **Faire** : Référencer le fichier et résumer l'essentiel

```markdown
### Configuration pytest

La configuration complète est dans [pyproject.toml](../pyproject.toml) (`[tool.pytest.ini_options]`).

Un fichier [tests/settings.py](../tests/settings.py) minimal permet d'exécuter les tests sans nécessiter un projet Django complet.
```

### 2. La meilleure documentation est le code

❌ **Ne pas faire** : Documenter chaque test individuellement

```markdown
### test_default_slug

**Objectif** : Vérifier la génération automatique du slug

```python
@pytest.mark.django_db
def test_default_slug():
    p = Parameter(name="hello ze world", value="yes")
    p.save()
    assert p.slug == "HELLO_ZE_WORLD"
```

**Couvre** :
- Méthode `save()`
- Fonction `parameter_slugify()`
```

✅ **Faire** : Résumer et référencer le code

```markdown
## Structure des tests

**19 tests** répartis en 5 catégories :
- Tests du modèle Parameter
- Tests du manager
- Tests de la commande load_param
- Tests du proxy app_parameter
- Tests du context processor

Les tests utilisent des fixtures pytest. Consultez [tests/test_django_app_parameter.py](../tests/test_django_app_parameter.py) pour les détails.
```

### 3. Se concentrer sur l'orientation du projet

❌ **Ne pas faire** : Donner des alternatives multiples (pip, virtualenv, etc.)

```markdown
#### Avec Poetry (recommandé)
...

#### Avec pip
...

#### Avec conda
...
```

✅ **Faire** : Documenter uniquement Poetry (l'outil choisi)

```markdown
Le projet utilise **Poetry** pour la gestion des dépendances.

```bash
poetry install
poetry shell
```
```

### 4. Responsabilité du développeur

❌ **Ne pas faire** : Expliquer des prérequis généraux (pyenv, git, etc.)

```markdown
**Note** : Si vous utilisez `pyenv`, assurez-vous d'avoir une version de Python récente :

```bash
pyenv versions
pyenv install 3.10.18
pyenv local 3.10.18
```
```

✅ **Faire** : Considérer que le lecteur maîtrise les prérequis

```markdown
Le projet utilise **Poetry** pour la gestion des dépendances.

```bash
poetry install
```
```

**Rationale** : L'installation et la configuration de pyenv sont hors du scope de notre documentation. Le développeur doit déjà maîtriser son environnement.

## Règles spécifiques

### Documentation des tests

- ✅ Expliquer **comment** lancer les tests
- ✅ Résumer la **structure** des tests
- ✅ Indiquer la **couverture**
- ❌ Ne pas recopier le code des tests
- ❌ Ne pas détailler chaque test individuellement

### Documentation de configuration

- ✅ Référencer les fichiers de configuration
- ✅ Donner les commandes essentielles
- ❌ Ne pas dupliquer le contenu des fichiers
- ❌ Ne pas expliquer la syntaxe TOML/YAML/etc.

### Documentation des outils

- ✅ Se concentrer sur **Poetry** (l'outil choisi)
- ❌ Ne pas documenter pip, virtualenv, conda en alternative
- ❌ Ne pas expliquer comment installer Poetry/pyenv/etc.

## Structure recommandée de la documentation

### Pour un guide de tests

```markdown
# Guide des tests

## Vue d'ensemble
- Résumé du nombre de tests
- Technologies utilisées

## Installation
- Commandes Poetry uniquement

## Exécution
- Commandes essentielles
- Raccourcis Makefile

## Workflow
- Étapes recommandées

## Structure
- Arborescence des fichiers
- Références aux fichiers sources

## Configuration
- Références aux fichiers de config
- Résumé des points clés (pas de copie)

## Ressources
- Liens vers le code
- Documentation externe
```

## Exemples de bonnes formulations

### Référencer du code

✅ "La configuration est dans [pyproject.toml](../pyproject.toml) (`[tool.pytest.ini_options]`)"

✅ "Consultez [tests/test_django_app_parameter.py](../tests/test_django_app_parameter.py) pour les détails"

✅ "Les tests utilisent des fixtures pytest pour créer des données réutilisables"

### Donner des commandes

✅ Grouper les alternatives avec des commentaires concis :

```bash
pytest                    # Tous les tests
pytest -v                 # Verbeux
make test                 # Raccourci Makefile
```

### Résumer sans dupliquer

✅ "Un fichier [tests/settings.py](../tests/settings.py) minimal permet d'exécuter les tests sans nécessiter un projet Django complet. Il configure une base de données SQLite en mémoire."

## Checklist avant de publier la documentation

- [ ] Aucun code n'est dupliqué (références uniquement)
- [ ] Pas d'explication de prérequis généraux (pyenv, git, etc.)
- [ ] Focus sur Poetry uniquement
- [ ] Références claires vers les fichiers sources
- [ ] Commandes essentielles avec raccourcis Makefile
- [ ] Documentation concise et directe
- [ ] Pas de détails d'implémentation (ils sont dans le code)

## Principe directeur

> "La documentation doit se focaliser uniquement sur le fonctionnement de notre app et considérer que le lecteur maîtrise l'ensemble des prérequis."

En cas de doute : **moins c'est mieux**. Référencer plutôt que dupliquer.
