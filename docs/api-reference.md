# Référence API

Documentation complète de l'API Django App Parameter.

## Table des matières

- [Modèle Parameter](#modèle-parameter)
- [Manager ParameterManager](#manager-parametermanager)
- [Proxy AccessParameter](#proxy-accessparameter)
- [Context Processor](#context-processor)
- [Utilitaires](#utilitaires)
- [Exceptions](#exceptions)

## Modèle Parameter

**Module** : `django_app_parameter.models`

### Classe Parameter

```python
class Parameter(models.Model):
    """Modèle pour stocker des paramètres d'application configurables."""
```

#### Champs

##### name

```python
name = models.CharField("Nom", max_length=100)
```

Nom lisible du paramètre en français.

- **Type** : CharField
- **Max Length** : 100 caractères
- **Requis** : Oui
- **Exemple** : `"Blog Title"`, `"Max Upload Size"`

##### slug

```python
slug = models.SlugField(max_length=40, unique=True)
```

Identifiant unique du paramètre, généré automatiquement depuis `name`.

- **Type** : SlugField
- **Max Length** : 40 caractères
- **Unique** : Oui
- **Auto-généré** : Oui (via `parameter_slugify`)
- **Format** : Majuscules, underscores
- **Exemple** : `"BLOG_TITLE"`, `"MAX_UPLOAD_SIZE"`
- **Read-only** : Oui (dans l'admin)

##### value_type

```python
value_type = models.CharField(max_length=3, choices=TYPES.choices, default=TYPES.STR)
```

Type de données du paramètre.

- **Type** : CharField avec choices
- **Valeurs possibles** :
  - `"INT"` : Nombre entier
  - `"STR"` : Chaîne de caractères (défaut)
  - `"FLT"` : Float
  - `"DCL"` : Decimal
  - `"JSN"` : JSON
  - `"BOO"` : Booléen
- **Défaut** : `"STR"`

##### value

```python
value = models.CharField("Valeur", max_length=250)
```

Valeur du paramètre stockée comme chaîne de caractères.

- **Type** : CharField
- **Max Length** : 250 caractères
- **Note** : Conversion de type effectuée à la lecture

##### description

```python
description = models.TextField("Description", blank=True)
```

Description optionnelle du paramètre.

- **Type** : TextField
- **Optionnel** : Oui
- **Utilisation** : Documentation

##### is_global

```python
is_global = models.BooleanField(default=False)
```

Indique si le paramètre est disponible dans les templates.

- **Type** : BooleanField
- **Défaut** : `False`
- **Usage** : Si `True`, disponible via le context processor

#### Classe TYPES

```python
class TYPES(models.TextChoices):
    INT = "INT", "Nombre entier"
    STR = "STR", "Chaîne de caractères"
    FLT = "FLT", "Nombre à virgule Float"
    DCL = "DCL", "Nombre à virgule Decimal"
    JSN = "JSN", "JSON"
    BOO = "BOO", "Booléen"
```

Énumération des types de données supportés.

**Utilisation** :
```python
from django_app_parameter.models import Parameter

Parameter.objects.create(
    name="Year",
    value="2024",
    value_type=Parameter.TYPES.INT
)
```

#### Méthodes d'instance

##### \_\_str\_\_()

```python
def __str__(self):
    return self.name
```

Retourne le nom du paramètre.

**Retourne** : `str`

##### save()

```python
def save(self, *args, **kwargs):
    if not self.slug:
        self.slug = parameter_slugify(self.name)
    super().save(*args, **kwargs)
```

Génère automatiquement le slug si non fourni avant la sauvegarde.

**Processus** :
1. Vérifie si `slug` est vide
2. Si vide, génère le slug depuis `name`
3. Appelle `super().save()`

##### int()

```python
def int(self) -> int:
    return int(self.value)
```

Convertit la valeur en entier.

**Retourne** : `int`

**Lève** : `ValueError` si la conversion échoue

**Exemple** :
```python
param = Parameter.objects.get(slug="MAX_SIZE")
size = param.int()  # 5242880
```

##### str()

```python
def str(self) -> str:
    return str(self.value)
```

Convertit la valeur en chaîne de caractères.

**Retourne** : `str`

**Note** : Toujours réussit puisque `value` est déjà une chaîne.

##### float()

```python
def float(self) -> float:
    return float(self.value)
```

Convertit la valeur en float.

**Retourne** : `float`

**Lève** : `ValueError` si la conversion échoue

##### decimal()

```python
def decimal(self) -> Decimal:
    return Decimal(self.value)
```

Convertit la valeur en Decimal.

**Retourne** : `decimal.Decimal`

**Lève** : `InvalidOperation` si la conversion échoue

**Exemple** :
```python
param = Parameter.objects.get(slug="TAX_RATE")
rate = param.decimal()  # Decimal('20.00')
```

##### json()

```python
def json(self):
    return json.loads(self.value)
```

Parse la valeur comme JSON.

**Retourne** : `dict`, `list`, ou autre type JSON

**Lève** : `json.JSONDecodeError` si le JSON est invalide

**Exemple** :
```python
param = Parameter.objects.get(slug="CONFIG")
config = param.json()  # {'key': 'value'}
```

##### bool()

```python
def bool(self) -> bool:
    if not self.value or self.value.lower() in ["false", "0"]:
        return False
    return bool(self.value)
```

Convertit la valeur en booléen avec logique personnalisée.

**Retourne** : `bool`

**Logique** :
- `False` si :
  - Chaîne vide (`""`)
  - `"false"` (insensible à la casse)
  - `"0"`
- `True` pour toute autre valeur

**Exemple** :
```python
param = Parameter.objects.get(slug="ENABLED")
param.value = "false"
print(param.bool())  # False

param.value = "true"
print(param.bool())  # True

param.value = "yes"
print(param.bool())  # True
```

##### get()

```python
def get(self):
    if self.value_type == self.TYPES.INT:
        return self.int()
    if self.value_type == self.TYPES.FLT:
        return self.float()
    if self.value_type == self.TYPES.DCL:
        return self.decimal()
    if self.value_type == self.TYPES.JSN:
        return self.json()
    if self.value_type == self.TYPES.BOO:
        return self.bool()
    return self.str()
```

Convertit automatiquement la valeur selon `value_type`.

**Retourne** : Type correspondant à `value_type`

**Exemple** :
```python
# Paramètre INT
param = Parameter.objects.get(slug="YEAR")
value = param.get()  # int

# Paramètre STR
param = Parameter.objects.get(slug="TITLE")
value = param.get()  # str

# Paramètre BOO
param = Parameter.objects.get(slug="ENABLED")
value = param.get()  # bool
```

#### Manager par défaut

```python
objects = ParameterManager()
```

Le manager personnalisé `ParameterManager` avec méthodes additionnelles.

## Manager ParameterManager

**Module** : `django_app_parameter.models`

```python
class ParameterManager(models.Manager):
    """Manager personnalisé avec méthodes de typage."""
```

### Méthodes

#### get_from_slug()

```python
def get_from_slug(self, slug: str) -> Parameter:
```

Récupère un paramètre par son slug.

**Paramètres** :
- `slug` (str) : Slug du paramètre

**Retourne** : `Parameter`

**Lève** : `ImproperlyConfigured` si le paramètre n'existe pas

**Exemple** :
```python
from django_app_parameter.models import Parameter

param = Parameter.objects.get_from_slug("BLOG_TITLE")
print(param.name)  # "Blog Title"
```

**Différence avec `get()`** :
- `get()` lève `DoesNotExist` (erreur de données)
- `get_from_slug()` lève `ImproperlyConfigured` (erreur de configuration)

#### int()

```python
def int(self, slug: str) -> int:
```

Récupère un paramètre et le convertit en entier.

**Paramètres** :
- `slug` (str) : Slug du paramètre

**Retourne** : `int`

**Lève** :
- `ImproperlyConfigured` si le paramètre n'existe pas
- `ValueError` si la conversion échoue

**Exemple** :
```python
max_size = Parameter.objects.int("MAX_UPLOAD_SIZE")
print(type(max_size))  # <class 'int'>
```

#### str()

```python
def str(self, slug: str) -> str:
```

Récupère un paramètre et le convertit en chaîne.

**Paramètres** :
- `slug` (str) : Slug du paramètre

**Retourne** : `str`

**Exemple** :
```python
title = Parameter.objects.str("SITE_TITLE")
```

#### float()

```python
def float(self, slug: str) -> float:
```

Récupère un paramètre et le convertit en float.

**Paramètres** :
- `slug` (str) : Slug du paramètre

**Retourne** : `float`

**Lève** :
- `ImproperlyConfigured` si le paramètre n'existe pas
- `ValueError` si la conversion échoue

#### decimal()

```python
def decimal(self, slug: str) -> Decimal:
```

Récupère un paramètre et le convertit en Decimal.

**Paramètres** :
- `slug` (str) : Slug du paramètre

**Retourne** : `decimal.Decimal`

**Lève** :
- `ImproperlyConfigured` si le paramètre n'existe pas
- `InvalidOperation` si la conversion échoue

**Exemple** :
```python
from decimal import Decimal

tax_rate = Parameter.objects.decimal("TAX_RATE")
print(type(tax_rate))  # <class 'decimal.Decimal'>
```

#### json()

```python
def json(self, slug: str):
```

Récupère un paramètre et le parse comme JSON.

**Paramètres** :
- `slug` (str) : Slug du paramètre

**Retourne** : `dict`, `list`, ou autre type JSON

**Lève** :
- `ImproperlyConfigured` si le paramètre n'existe pas
- `JSONDecodeError` si le JSON est invalide

**Exemple** :
```python
config = Parameter.objects.json("API_CONFIG")
endpoint = config["endpoint"]
```

#### bool()

```python
def bool(self, slug: str) -> bool:
```

Récupère un paramètre et le convertit en booléen.

**Paramètres** :
- `slug` (str) : Slug du paramètre

**Retourne** : `bool`

**Lève** : `ImproperlyConfigured` si le paramètre n'existe pas

**Exemple** :
```python
enabled = Parameter.objects.bool("FEATURE_ENABLED")
if enabled:
    # Activer la fonctionnalité
```

#### create_or_update()

```python
def create_or_update(self, parameter: dict, update: bool = True) -> str:
```

Crée ou met à jour un paramètre depuis un dictionnaire.

**Paramètres** :
- `parameter` (dict) : Dictionnaire contenant les données du paramètre
  - `name` (requis) : Nom du paramètre
  - `slug` (optionnel) : Slug personnalisé
  - `value` (optionnel, défaut: `""`) : Valeur
  - `value_type` (optionnel, défaut: `"STR"`) : Type
  - `description` (optionnel, défaut: `""`) : Description
  - `is_global` (optionnel, défaut: `False`) : Global ou non
- `update` (bool) : Si `True`, met à jour les paramètres existants

**Retourne** : `str`
- `"Added"` : Paramètre créé
- `"Already exists"` : Paramètre existe, pas de mise à jour
- `"Already exists, updated"` : Paramètre existe et mis à jour

**Exemple** :
```python
from django_app_parameter.models import Parameter

# Créer un nouveau paramètre
result = Parameter.objects.create_or_update({
    "name": "Site Title",
    "value": "Mon Site",
    "value_type": "STR",
    "is_global": True
})
print(result)  # "Added"

# Tenter de créer à nouveau sans update
result = Parameter.objects.create_or_update({
    "name": "Site Title",
    "value": "Nouveau Titre"
}, update=False)
print(result)  # "Already exists"

# Mettre à jour
result = Parameter.objects.create_or_update({
    "name": "Site Title",
    "value": "Nouveau Titre"
}, update=True)
print(result)  # "Already exists, updated"
```

**Utilisation typique** :
```python
# Chargement de paramètres depuis JSON
import json

with open('parameters.json') as f:
    parameters = json.load(f)

for param in parameters:
    result = Parameter.objects.create_or_update(param)
    print(f"{param['name']}: {result}")
```

## Proxy AccessParameter

**Module** : `django_app_parameter`

```python
class AccessParameter:
    """Proxy pour accéder aux paramètres via app_parameter.SLUG."""
```

### Instance globale

```python
app_parameter = AccessParameter()
```

Instance singleton utilisée pour l'accès aux paramètres.

### Méthodes

#### \_\_getattr\_\_()

```python
def __getattr__(self, slug: str):
```

Récupère un paramètre par son slug avec conversion automatique.

**Paramètres** :
- `slug` (str) : Slug du paramètre

**Retourne** : Valeur convertie selon `value_type`

**Lève** : `ImproperlyConfigured` si le paramètre n'existe pas

**Exemple** :
```python
from django_app_parameter import app_parameter

# Accès direct
title = app_parameter.SITE_TITLE  # str
year = app_parameter.YEAR  # int
rate = app_parameter.TAX_RATE  # Decimal
config = app_parameter.API_CONFIG  # dict
enabled = app_parameter.FEATURE_ENABLED  # bool
```

**Fonctionnement interne** :
1. Récupère le paramètre depuis la BDD
2. Appelle `parameter.get()` pour la conversion de type
3. Retourne la valeur convertie

#### \_\_setattr\_\_()

```python
def __setattr__(self, name, value):
    raise Exception("You can't set an app parameter at run time")
```

Empêche la modification des paramètres via le proxy.

**Lève** : `Exception` toujours

**Exemple** :
```python
from django_app_parameter import app_parameter

# Ceci lève une exception
app_parameter.SITE_TITLE = "Nouveau Titre"  # Exception!
```

**Raison** : Les paramètres doivent être modifiés via l'admin ou l'ORM pour garantir la persistance en base de données.

## Context Processor

**Module** : `django_app_parameter.context_processors`

### add_global_parameter_context()

```python
def add_global_parameter_context(request) -> dict:
```

Context processor Django qui ajoute les paramètres globaux au contexte des templates.

**Paramètres** :
- `request` : Objet HttpRequest Django

**Retourne** : `dict` avec les paramètres globaux

**Exemple de retour** :
```python
{
    'SITE_TITLE': 'Mon Site',
    'CONTACT_EMAIL': 'contact@example.com',
    'MAINTENANCE_MODE': 'false'
}
```

**Configuration** :
```python
# settings.py
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                'django_app_parameter.context_processors.add_global_parameter_context',
            ],
        },
    },
]
```

**Fonctionnement** :
1. Récupère tous les paramètres avec `is_global=True`
2. Pour chaque paramètre, ajoute `{slug: valeur}` au dictionnaire
3. **Important** : Toutes les valeurs sont converties en chaînes via `.str()`

**Utilisation dans les templates** :
```html
<title>{{ SITE_TITLE }}</title>
{% if MAINTENANCE_MODE %}
    <div class="alert">Maintenance en cours</div>
{% endif %}
```

**Limitation** : Les valeurs sont toujours des chaînes dans les templates, quel que soit le `value_type`.

## Utilitaires

**Module** : `django_app_parameter.models`

### parameter_slugify()

```python
def parameter_slugify(content: str) -> str:
```

Génère un slug pour un paramètre.

**Paramètres** :
- `content` (str) : Texte à slugifier

**Retourne** : `str` - Slug généré

**Algorithme** :
1. Applique `django.utils.text.slugify()` (minuscules, hyphens)
2. Convertit en majuscules
3. Remplace les hyphens par des underscores

**Exemples** :
```python
from django_app_parameter.models import parameter_slugify

slug = parameter_slugify("Blog Title")
print(slug)  # "BLOG_TITLE"

slug = parameter_slugify("sender e-mail")
print(slug)  # "SENDER_E_MAIL"

slug = parameter_slugify("Hello World!")
print(slug)  # "HELLO_WORLD"

slug = parameter_slugify("café-français")
print(slug)  # "CAFE_FRANCAIS"
```

**Caractéristiques** :
- Supprime les caractères spéciaux
- Convertit les accents en ASCII
- Format final : UPPERCASE_WITH_UNDERSCORES

## Exceptions

### ImproperlyConfigured

**Module** : `django.core.exceptions`

Exception levée quand un paramètre requis n'existe pas.

**Utilisation** :
```python
from django.core.exceptions import ImproperlyConfigured
from django_app_parameter import app_parameter

try:
    value = app_parameter.NONEXISTENT_PARAM
except ImproperlyConfigured as e:
    print(f"Paramètre manquant : {e}")
    # Gérer l'erreur (valeur par défaut, logging, etc.)
```

**Pourquoi ImproperlyConfigured ?**

Cette exception est utilisée (plutôt que `Parameter.DoesNotExist`) pour indiquer qu'il s'agit d'une erreur de configuration de l'application, similaire à un paramètre manquant dans `settings.py`.

### ValueError

Exception Python standard levée lors des conversions de type échouées.

**Exemple** :
```python
# Paramètre avec value="abc"
try:
    number = Parameter.objects.int("INVALID_NUMBER")
except ValueError:
    print("Impossible de convertir en entier")
    number = 0
```

### JSONDecodeError

Exception levée lors du parsing JSON échoué.

**Exemple** :
```python
import json

# Paramètre avec value="invalid json{{"
try:
    config = Parameter.objects.json("BAD_JSON")
except json.JSONDecodeError as e:
    print(f"JSON invalide : {e}")
    config = {}
```

## Admin

**Module** : `django_app_parameter.admin`

### ParameterAdmin

```python
@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    model = Parameter
    list_display = ("name", "slug", "value", "value_type")
    list_filter = ("value_type", "is_global")
    readonly_fields = ("slug",)
    search_fields = ("name", "slug", "description", "value")
```

Configuration de l'interface d'administration.

**Fonctionnalités** :
- **list_display** : Colonnes affichées dans la liste
- **list_filter** : Filtres par type et statut global
- **readonly_fields** : Slug en lecture seule
- **search_fields** : Recherche dans nom, slug, description et valeur

## Types Python

Pour une meilleure documentation du code, voici les types retournés par chaque méthode :

```python
from typing import Union
from decimal import Decimal

# Méthodes Parameter
def int(self) -> int: ...
def str(self) -> str: ...
def float(self) -> float: ...
def decimal(self) -> Decimal: ...
def json(self) -> Union[dict, list, str, int, float, bool, None]: ...
def bool(self) -> bool: ...
def get(self) -> Union[int, str, float, Decimal, dict, list, bool]: ...

# Méthodes Manager
def get_from_slug(self, slug: str) -> Parameter: ...
def int(self, slug: str) -> int: ...
def str(self, slug: str) -> str: ...
def float(self, slug: str) -> float: ...
def decimal(self, slug: str) -> Decimal: ...
def json(self, slug: str) -> Union[dict, list]: ...
def bool(self, slug: str) -> bool: ...
def create_or_update(self, parameter: dict, update: bool = True) -> str: ...

# Proxy
def __getattr__(self, slug: str) -> Union[int, str, float, Decimal, dict, list, bool]: ...

# Context processor
def add_global_parameter_context(request) -> dict[str, str]: ...

# Utilitaire
def parameter_slugify(content: str) -> str: ...
```

## Exemples complets

### Exemple 1 : Accès avec gestion d'erreurs

```python
from django.core.exceptions import ImproperlyConfigured
from django_app_parameter import app_parameter

def get_config():
    """Récupère la configuration avec valeurs par défaut."""
    try:
        max_size = app_parameter.MAX_UPLOAD_SIZE
    except ImproperlyConfigured:
        max_size = 5242880  # 5 Mo par défaut

    try:
        items_per_page = app_parameter.ITEMS_PER_PAGE
    except (ImproperlyConfigured, ValueError):
        items_per_page = 20

    return {
        'max_upload_size': max_size,
        'items_per_page': items_per_page,
    }
```

### Exemple 2 : Création et mise à jour

```python
from django_app_parameter.models import Parameter

# Créer plusieurs paramètres
params = [
    {
        "name": "Site Title",
        "value": "Mon Site",
        "is_global": True
    },
    {
        "name": "Max Upload Size",
        "value": "10485760",
        "value_type": Parameter.TYPES.INT
    },
    {
        "name": "Tax Rate",
        "value": "20.00",
        "value_type": Parameter.TYPES.DCL
    }
]

for param in params:
    result = Parameter.objects.create_or_update(param)
    print(f"{param['name']}: {result}")
```

### Exemple 3 : Utilisation dans une vue

```python
from django.shortcuts import render
from django.core.exceptions import ImproperlyConfigured
from django_app_parameter import app_parameter

def product_list(request):
    # Configuration depuis les paramètres
    try:
        items_per_page = app_parameter.ITEMS_PER_PAGE
        tax_rate = app_parameter.TAX_RATE
        show_prices = app_parameter.SHOW_PRICES_PUBLIC
    except ImproperlyConfigured as e:
        # Logging et valeurs par défaut
        logger.warning(f"Missing parameter: {e}")
        items_per_page = 20
        tax_rate = Decimal("20.00")
        show_prices = True

    # Utilisation dans la logique
    products = Product.objects.all()[:items_per_page]

    if show_prices:
        for product in products:
            product.price_with_tax = product.price * (1 + tax_rate / 100)

    return render(request, 'products/list.html', {
        'products': products,
        'show_prices': show_prices,
    })
```
