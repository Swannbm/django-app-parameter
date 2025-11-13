# Architecture technique

Documentation détaillée de l'architecture interne de Django App Parameter.

## Vue d'ensemble

Django App Parameter est conçu comme une extension légère et modulaire pour Django, suivant les conventions du framework. L'architecture est organisée en plusieurs couches distinctes.

## Structure du projet

```
django-app-parameter/
│
├── django_app_parameter/        # Package principal
│   ├── __init__.py             # Exports publics (AccessParameter)
│   ├── models.py               # Modèle Parameter et ParameterManager
│   ├── admin.py                # Configuration Django admin
│   ├── apps.py                 # Configuration AppConfig
│   ├── context_processors.py  # Context processor pour templates
│   ├── tests.py                # Suite de tests complète
│   ├── data_for_test.json     # Fixtures de test
│   │
│   ├── migrations/             # Migrations de base de données
│   │   ├── __init__.py
│   │   ├── 0001_initial.py
│   │   ├── 0002_parameter_is_global_alter_...
│   │   └── 0003_alter_parameter_value_type.py
│   │
│   └── management/             # Commandes de gestion
│       └── commands/
│           ├── __init__.py
│           └── load_param.py
│
├── docs/                        # Documentation
├── pyproject.toml              # Configuration Poetry
├── README.md                   # Documentation utilisateur
├── CHANGELOG.md                # Historique des versions
├── LICENSE                     # Licence CC0 1.0
├── .flake8                     # Configuration linting
├── .coveragerc                 # Configuration couverture
└── .gitignore                  # Fichiers ignorés par Git
```

## Architecture en couches

```
┌─────────────────────────────────────────────────────────┐
│                    COUCHE PRÉSENTATION                   │
│  ┌────────────────┐  ┌──────────────────────────────┐   │
│  │  Django Admin  │  │  Templates (context_processor)│   │
│  └────────┬───────┘  └──────────┬───────────────────┘   │
└───────────┼────────────────────┼─────────────────────────┘
            │                    │
┌───────────┼────────────────────┼─────────────────────────┐
│           │   COUCHE ACCÈS     │                         │
│  ┌────────▼────────┐  ┌────────▼─────────┐              │
│  │ AccessParameter │  │  Python Code     │              │
│  │    (Proxy)      │  │  (app_parameter) │              │
│  └────────┬────────┘  └────────┬─────────┘              │
└───────────┼────────────────────┼─────────────────────────┘
            │                    │
┌───────────┼────────────────────┼─────────────────────────┐
│           │  COUCHE LOGIQUE    │                         │
│  ┌────────▼────────────────────▼─────────┐               │
│  │      ParameterManager                 │               │
│  │  - get_from_slug()                    │               │
│  │  - int(), str(), float(), etc.        │               │
│  │  - create_or_update()                 │               │
│  └────────┬──────────────────────────────┘               │
└───────────┼─────────────────────────────────────────────┘
            │
┌───────────┼─────────────────────────────────────────────┐
│           │  COUCHE MODÈLE                              │
│  ┌────────▼────────┐                                    │
│  │   Parameter     │                                    │
│  │  - name         │                                    │
│  │  - slug         │                                    │
│  │  - value        │                                    │
│  │  - value_type   │                                    │
│  │  - description  │                                    │
│  │  - is_global    │                                    │
│  └────────┬────────┘                                    │
└───────────┼─────────────────────────────────────────────┘
            │
┌───────────▼─────────────────────────────────────────────┐
│              COUCHE PERSISTANCE (BDD)                    │
│         Table: django_app_parameter_parameter            │
└──────────────────────────────────────────────────────────┘
```

## Composants principaux

### 1. Modèle Parameter

**Responsabilités** :
- Définir le schéma de données
- Fournir des méthodes de conversion de type
- Gérer l'auto-génération des slugs

**Dépendances** :
- `django.db.models`
- `django.utils.text.slugify`
- `json` (pour type JSON)
- `decimal.Decimal` (pour type Decimal)

**Interactions** :
- Appelé par `ParameterManager`
- Utilisé par l'admin Django
- Interrogé par le context processor

**Design patterns** :
- **Active Record** : Modèle Django standard
- **Type Conversion** : Méthodes de casting pour chaque type

### 2. ParameterManager

**Responsabilités** :
- Fournir des méthodes d'accès typées
- Gérer la création/mise à jour en masse
- Lancer des exceptions appropriées (`ImproperlyConfigured`)

**Dépendances** :
- `models.Manager` (héritage)
- `django.core.exceptions.ImproperlyConfigured`

**Interactions** :
- Utilisé par `AccessParameter`
- Appelé directement par le code utilisateur
- Utilisé par la commande `load_param`

**Design patterns** :
- **Manager Pattern** : Pattern Django standard
- **Factory Methods** : Méthodes de création typées

### 3. AccessParameter (Proxy)

**Responsabilités** :
- Fournir un accès de type `settings` aux paramètres
- Empêcher les modifications directes
- Conversion automatique de type

**Dépendances** :
- `ParameterManager`
- Import lazy du modèle `Parameter`

**Interactions** :
- Point d'entrée principal pour le code utilisateur
- Utilisé via `from django_app_parameter import app_parameter`

**Design patterns** :
- **Proxy Pattern** : Intermédiaire entre l'utilisateur et le modèle
- **Singleton Pattern** : Instance unique `app_parameter`
- **Lazy Loading** : Import du modèle dans `__getattr__` pour éviter les imports circulaires

**Code clé** :
```python
class AccessParameter:
    def __getattr__(self, slug):
        from .models import Parameter  # Import lazy
        param = Parameter.objects.get_from_slug(slug)
        return param.get()

    def __setattr__(self, name, value):
        raise Exception("You can't set an app parameter at run time")

app_parameter = AccessParameter()  # Singleton
```

### 4. Context Processor

**Responsabilités** :
- Injecter les paramètres globaux dans le contexte des templates
- Convertir toutes les valeurs en chaînes

**Dépendances** :
- Modèle `Parameter`

**Interactions** :
- Appelé automatiquement par Django pour chaque requête
- Utilisé par les templates Django

**Limitations** :
- Exécuté à chaque requête (considérations de performance)
- Conversion en chaînes uniquement

**Code clé** :
```python
def add_global_parameter_context(request):
    params = Parameter.objects.filter(is_global=True)
    context = dict()
    for param in params:
        context[param.slug] = param.str()
    return context
```

### 5. Admin Configuration

**Responsabilités** :
- Fournir l'interface de gestion
- Configurer l'affichage et les filtres
- Rendre le slug en lecture seule

**Dépendances** :
- `django.contrib.admin`
- Modèle `Parameter`

**Interactions** :
- Utilisé par les administrateurs via `/admin/`
- Enregistré automatiquement via `@admin.register`

### 6. Commande load_param

**Responsabilités** :
- Charger des paramètres depuis JSON
- Gérer les options (fichier, chaîne, no-update)
- Afficher les résultats

**Dépendances** :
- `django.core.management.base.BaseCommand`
- `ParameterManager.create_or_update()`
- `json` (parsing)

**Interactions** :
- Appelée via `python manage.py load_param`
- Utilisable programmatiquement via `call_command()`

## Flux de données

### Lecture d'un paramètre

```
┌────────────────┐
│  Code Python   │
│  app_parameter │
│  .BLOG_TITLE   │
└───────┬────────┘
        │
        ▼
┌────────────────────┐
│ AccessParameter    │
│ __getattr__()      │
└───────┬────────────┘
        │
        ▼
┌────────────────────┐
│ ParameterManager   │
│ get_from_slug()    │
└───────┬────────────┘
        │
        ▼
┌────────────────────┐
│ Base de données    │
│ SELECT * FROM ...  │
└───────┬────────────┘
        │
        ▼
┌────────────────────┐
│ Parameter instance │
│ get()              │
└───────┬────────────┘
        │
        ▼
┌────────────────────┐
│ Conversion de type │
│ (int/str/bool/etc) │
└───────┬────────────┘
        │
        ▼
┌────────────────────┐
│ Valeur retournée   │
│ au code appelant   │
└────────────────────┘
```

### Création/mise à jour via load_param

```
┌─────────────────┐
│ Fichier JSON    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ load_param      │
│ Command         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ json.loads()    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Pour chaque     │
│ paramètre       │
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│ ParameterManager     │
│ create_or_update()   │
└────────┬─────────────┘
         │
    ┌────▼────┐
    │ Slug    │
    │ existe? │
    └────┬────┘
         │
    ┌────▼─────┐
    │   Non    │
    └────┬─────┘
         │
         ▼
┌──────────────────┐         ┌─────────────┐
│ Créer nouveau    │         │    Oui      │
│ paramètre        │         └──────┬──────┘
└────────┬─────────┘                │
         │                           ▼
         │                  ┌─────────────────┐
         │                  │ --no-update ?   │
         │                  └────┬────────────┘
         │                       │
         │                  ┌────▼─────┐
         │                  │   Non    │
         │                  └────┬─────┘
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         │              │ Mettre à jour   │
         │              │ paramètre       │
         │              └────┬────────────┘
         │                   │
         └───────────────────┴──────────────┐
                             │
                             ▼
                    ┌─────────────────┐
                    │ Sauvegarder     │
                    │ en BDD          │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Message de      │
                    │ confirmation    │
                    └─────────────────┘
```

### Affichage dans un template

```
┌─────────────────┐
│ Requête HTTP    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ Django middleware       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Context processors      │
│ (dont app_parameter)    │
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Parameter.objects        │
│ .filter(is_global=True)  │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Pour chaque paramètre:   │
│ context[slug] = str()    │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Context complet          │
│ (dict)                   │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Vue Django               │
│ (render)                 │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Template engine          │
│ {{ BLOG_TITLE }}         │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ HTML généré              │
└──────────────────────────┘
```

## Schéma de base de données

### Table : django_app_parameter_parameter

```sql
CREATE TABLE django_app_parameter_parameter (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(40) NOT NULL UNIQUE,
    value_type VARCHAR(3) NOT NULL DEFAULT 'STR',
    description TEXT NOT NULL DEFAULT '',
    value VARCHAR(250) NOT NULL DEFAULT '',
    is_global BOOLEAN NOT NULL DEFAULT FALSE,

    INDEX idx_slug (slug),
    INDEX idx_is_global (is_global),
    INDEX idx_value_type (value_type)
);
```

**Indexes** :
- `PRIMARY KEY (id)` : Clé primaire auto-incrémentée
- `UNIQUE (slug)` : Garantit l'unicité des slugs
- `INDEX (is_global)` : Optimise les requêtes du context processor
- `INDEX (value_type)` : Optimise les filtres dans l'admin

**Contraintes** :
- `slug` : Unique, max 40 caractères
- `name` : Max 100 caractères
- `value` : Max 250 caractères
- `value_type` : Choix limité (INT/STR/FLT/DCL/JSN/BOO)

## Gestion de la conversion de type

### Stratégie de stockage

**Principe** : Tout est stocké comme `VARCHAR(250)`

**Avantages** :
- Schéma simple et stable
- Pas de migrations pour ajouter des types
- Flexible pour différents types de données

**Inconvénients** :
- Limite de 250 caractères
- Pas de validation au niveau BDD
- Conversions à l'exécution

### Mécanisme de conversion

```python
class Parameter(models.Model):
    # Stockage uniforme
    value = models.CharField(max_length=250)
    value_type = models.CharField(max_length=3, choices=TYPES.choices)

    # Conversion à la demande
    def get(self):
        """Convertit selon value_type."""
        if self.value_type == self.TYPES.INT:
            return int(self.value)
        elif self.value_type == self.TYPES.FLT:
            return float(self.value)
        elif self.value_type == self.TYPES.DCL:
            return Decimal(self.value)
        elif self.value_type == self.TYPES.JSN:
            return json.loads(self.value)
        elif self.value_type == self.TYPES.BOO:
            return self.bool()
        else:
            return str(self.value)
```

**Gestion d'erreurs** :
- `ValueError` : Conversion int/float échoue
- `InvalidOperation` : Conversion Decimal échoue
- `JSONDecodeError` : Parsing JSON échoue

Ces erreurs **ne sont pas catchées** par le modèle, permettant au code appelant de les gérer.

## Génération des slugs

### Fonction parameter_slugify

```python
def parameter_slugify(content: str) -> str:
    """
    blog title → BLOG_TITLE
    sender e-mail → SENDER_E_MAIL
    """
    return slugify(content).upper().replace("-", "_")
```

**Étapes** :
1. `slugify()` de Django :
   - Convertit en minuscules
   - Remplace espaces par hyphens
   - Supprime caractères spéciaux
   - Convertit accents en ASCII
2. `.upper()` :
   - Convertit en majuscules
3. `.replace("-", "_")` :
   - Remplace hyphens par underscores

**Exemples de transformation** :

| Input | slugify() | upper() | replace() | Output |
|-------|-----------|---------|-----------|--------|
| "Blog Title" | "blog-title" | "BLOG-TITLE" | "BLOG_TITLE" | BLOG_TITLE |
| "sender e-mail" | "sender-e-mail" | "SENDER-E-MAIL" | "SENDER_E_MAIL" | SENDER_E_MAIL |
| "Café Français" | "cafe-francais" | "CAFE-FRANCAIS" | "CAFE_FRANCAIS" | CAFE_FRANCAIS |
| "Hello World!" | "hello-world" | "HELLO-WORLD" | "HELLO_WORLD" | HELLO_WORLD |

## Gestion des exceptions

### ImproperlyConfigured

**Choix de conception** : Utiliser `ImproperlyConfigured` plutôt que `DoesNotExist`

**Raison** :
- Un paramètre manquant = erreur de **configuration**
- Similaire à un paramètre manquant dans `settings.py`
- Indique un problème d'installation, pas de données

**Utilisation** :
```python
from django.core.exceptions import ImproperlyConfigured

def get_from_slug(self, slug):
    try:
        return self.get(slug=slug)
    except Parameter.DoesNotExist:
        raise ImproperlyConfigured(
            f"Parameter with slug '{slug}' does not exist"
        )
```

### Hiérarchie des exceptions

```
Exception
└── BaseException
    └── django.core.exceptions.ImproperlyConfigured
        └── Paramètre manquant

ValueError
└── Conversion int/float échoue

decimal.InvalidOperation
└── Conversion Decimal échoue

json.JSONDecodeError
└── Parsing JSON échoue
```

## Performance et optimisation

### Considérations de performance

**Requêtes BDD** :
- Chaque accès à `app_parameter.SLUG` = 1 requête SELECT
- Context processor = 1 requête pour tous les paramètres globaux
- Pas de cache intégré

**Impact** :
```python
# 3 requêtes BDD
title = app_parameter.BLOG_TITLE
email = app_parameter.CONTACT_EMAIL
max_size = app_parameter.MAX_UPLOAD_SIZE
```

### Stratégies d'optimisation

#### 1. Cache applicatif

```python
from django.core.cache import cache

def get_cached_param(slug, timeout=3600):
    cache_key = f"param_{slug}"
    value = cache.get(cache_key)
    if value is None:
        value = getattr(app_parameter, slug)
        cache.set(cache_key, value, timeout)
    return value
```

#### 2. Prefetch dans les vues

```python
# Au lieu de multiples accès
def my_view(request):
    # Charger une fois
    params = {
        p.slug: p.get()
        for p in Parameter.objects.filter(
            slug__in=['TITLE', 'EMAIL', 'MAX_SIZE']
        )
    }
    # Utiliser depuis le dict
    title = params['TITLE']
```

#### 3. Limiter les paramètres globaux

Le context processor s'exécute à **chaque requête**. Limitez le nombre de paramètres avec `is_global=True`.

```python
# Préférez
{% load my_tags %}
{% get_parameter "BLOG_TITLE" as title %}

# Plutôt que
{{ BLOG_TITLE }}  # Si peu utilisé
```

## Extensibilité

### Ajouter un nouveau type de données

**Étapes** :

1. **Ajouter le type dans TYPES** :
```python
class TYPES(models.TextChoices):
    # ... types existants
    DAT = "DAT", "Date"
```

2. **Migration** :
```bash
python manage.py makemigrations
```

3. **Ajouter la méthode de conversion** :
```python
def date(self):
    from datetime import datetime
    return datetime.strptime(self.value, "%Y-%m-%d").date()
```

4. **Ajouter au get()** :
```python
def get(self):
    # ... conversions existantes
    if self.value_type == self.TYPES.DAT:
        return self.date()
    return self.str()
```

5. **Ajouter au Manager** :
```python
def date(self, slug):
    return self.get_from_slug(slug).date()
```

### Personnaliser le comportement

#### Validation personnalisée

```python
from django.core.exceptions import ValidationError

class Parameter(models.Model):
    # ... champs existants

    def clean(self):
        """Validation personnalisée."""
        super().clean()

        # Valider selon le type
        if self.value_type == self.TYPES.INT:
            try:
                int(self.value)
            except ValueError:
                raise ValidationError({
                    'value': 'Valeur invalide pour un entier'
                })

        # Autres validations...
```

#### Signals pour audit

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Parameter)
def log_parameter_change(sender, instance, created, **kwargs):
    """Log les modifications de paramètres."""
    if created:
        logger.info(f"Paramètre créé : {instance.slug}")
    else:
        logger.info(f"Paramètre modifié : {instance.slug}")
```

## Tests

### Architecture des tests

**tests.py** (467 lignes, 100% de couverture)

**Organisation** :
```python
TestParameter           # Tests du modèle
├── test_default_slug
├── test_default_str
├── test_str
├── test_int
├── test_float
├── test_decimal
├── test_json
├── test_bool
└── test_dundo_str

TestParameterManager    # Tests du manager
├── test_fixtures
├── test_get_from_slug
├── test_create_or_update
├── test_create_only_name
└── test_access

TestLoadParamMC         # Tests de la commande
├── test_json_options
├── test_file_options
└── test_noupdate_options

Test_app_parameter      # Tests du proxy
├── test_read_param
└── test_set_param

TestContextProcessor    # Tests du context processor
└── test_context
```

**Fixtures** :
```python
@pytest.fixture
def params(db):
    return [
        Parameter(name="blog title", ...),
        Parameter(name="year of birth", ...),
        Parameter(name="a small json", ...)
    ]
```

### Couverture de tests

**100%** sur tous les composants :
- Modèle Parameter
- Manager ParameterManager
- Proxy AccessParameter
- Context processor
- Commande load_param
- Admin (par défaut Django)

## Dépendances et compatibilité

### Dépendances runtime

**Minimales** :
- Python 3.7+
- Django 3.2+ (pour BigAutoField)

**Implicites** :
- `django.db` (ORM)
- `django.contrib.admin`
- `django.utils.text.slugify`
- `json` (stdlib)
- `decimal` (stdlib)

### Compatibilité bases de données

**Testées** :
- SQLite (développement)
- PostgreSQL (recommandé production)
- MySQL / MariaDB

**Limitations** :
- VARCHAR(250) pour valeur
- SlugField(40) pour slug
- Comportement identique sur toutes les BDD

## Évolution et maintenance

### Historique des migrations

**0001_initial** (2021-09-11) :
- Création table Parameter
- Types : INT, STR, FLT, DCL, JSN

**0002_...** (2022-02-22) :
- Ajout champ `is_global`
- Labels en français

**0003_...** (2023-10-18) :
- Ajout type BOO (Boolean)

### Stratégie de versioning

**Semantic Versioning** :
- **Major** (1.x.x) : Breaking changes
- **Minor** (x.1.x) : Nouvelles fonctionnalités
- **Patch** (x.x.1) : Bug fixes

**Actuel** : v1.1.3

## Bonnes pratiques d'architecture

### ✅ Respect des conventions Django

- Utilise l'ORM Django standard
- Suit le pattern Model-Manager
- Admin configuration standard
- Context processor standard
- Management commands standard

### ✅ Séparation des responsabilités

- **Modèle** : Données et conversion
- **Manager** : Logique d'accès
- **Proxy** : Interface simple
- **Context processor** : Integration templates
- **Admin** : Interface de gestion

### ✅ Extensibilité

- Ajout de types facilité
- Personnalisation possible
- Hooks (signals) utilisables

### ✅ Testabilité

- 100% de couverture
- Tests unitaires et d'intégration
- Fixtures réutilisables

### ⚠️ Points d'attention

- **Performance** : Pas de cache intégré
- **Limite de taille** : 250 caractères
- **Validation** : Pas de validation stricte des valeurs
- **Concurrence** : Pas de locking pour modifications simultanées

## Diagrammes UML

### Diagramme de classes

```
┌─────────────────────────────┐
│      Parameter              │
├─────────────────────────────┤
│ - id: BigInt                │
│ - name: CharField(100)      │
│ - slug: SlugField(40)       │
│ - value: CharField(250)     │
│ - value_type: CharField(3)  │
│ - description: TextField    │
│ - is_global: BooleanField   │
├─────────────────────────────┤
│ + save()                    │
│ + __str__()                 │
│ + int(): int                │
│ + str(): str                │
│ + float(): float            │
│ + decimal(): Decimal        │
│ + json(): dict/list         │
│ + bool(): bool              │
│ + get(): Any                │
└──────────▲──────────────────┘
           │
           │ uses
           │
┌──────────┴──────────────────┐
│   ParameterManager          │
├─────────────────────────────┤
│ + get_from_slug(slug)       │
│ + int(slug): int            │
│ + str(slug): str            │
│ + float(slug): float        │
│ + decimal(slug): Decimal    │
│ + json(slug): dict/list     │
│ + bool(slug): bool          │
│ + create_or_update(dict)    │
└──────────▲──────────────────┘
           │
           │ uses
           │
┌──────────┴──────────────────┐
│   AccessParameter           │
├─────────────────────────────┤
│ + __getattr__(slug): Any    │
│ + __setattr__(name, value)  │
└─────────────────────────────┘
```

## Conclusion

Django App Parameter suit une architecture simple et modulaire qui respecte les conventions Django tout en restant extensible. La séparation claire des responsabilités et la couverture de tests complète garantissent sa fiabilité et sa maintenabilité.
