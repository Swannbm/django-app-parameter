# FAQ - Questions fréquentes

Réponses aux questions les plus courantes sur Django App Parameter.

## Installation et configuration

### Quelle version de Python est requise ?

Python **3.7 ou supérieur**. Le package est testé sur Python 3.7, 3.8, 3.9, 3.10 et 3.11.

### Quelle version de Django est requise ?

Django **3.2 ou supérieur**. Le package utilise `BigAutoField` introduit dans Django 3.2.

### Le package fonctionne-t-il avec PostgreSQL/MySQL/SQLite ?

Oui, Django App Parameter fonctionne avec toutes les bases de données supportées par Django :
- PostgreSQL (recommandé pour la production)
- MySQL / MariaDB
- SQLite (développement)
- Oracle

### Comment désinstaller proprement le package ?

```bash
# 1. Sauvegarder les paramètres (optionnel)
python manage.py dumpdata django_app_parameter > parameters_backup.json

# 2. Supprimer les tables
python manage.py migrate django_app_parameter zero

# 3. Retirer de INSTALLED_APPS
# Supprimez 'django_app_parameter' de settings.py

# 4. Désinstaller
pip uninstall django-app-parameter
```

## Utilisation de base

### Comment créer un paramètre ?

**Via l'admin** :
1. Accédez à `/admin/django_app_parameter/parameter/`
2. Cliquez sur "Ajouter Parameter"
3. Remplissez le formulaire et enregistrez

**Via le code** :
```python
from django_app_parameter.models import Parameter

Parameter.objects.create(
    name="Site Title",
    value="Mon Site",
    value_type=Parameter.TYPES.STR
)
```

**Via la commande** :
```bash
python manage.py load_param --json '[{"name": "Site Title", "value": "Mon Site"}]'
```

### Comment accéder à un paramètre ?

```python
from django_app_parameter import app_parameter

# Accès simple avec conversion automatique
title = app_parameter.SITE_TITLE
```

### Quelle est la différence entre `app_parameter.SLUG` et `Parameter.objects.str("SLUG")` ?

Les deux fonctionnent, mais avec des différences subtiles :

```python
# app_parameter : Conversion automatique selon value_type
value = app_parameter.MY_PARAM  # int si value_type=INT, str si STR, etc.

# Manager : Type explicite
value = Parameter.objects.str("MY_PARAM")  # Toujours str
value = Parameter.objects.int("MY_PARAM")  # Toujours int
```

**Recommandation** : Utilisez `app_parameter` pour la simplicité, `Manager` pour le contrôle explicite.

### Comment savoir si un paramètre existe avant d'y accéder ?

```python
from django.core.exceptions import ImproperlyConfigured
from django_app_parameter import app_parameter

try:
    value = app_parameter.MAYBE_EXISTS
except ImproperlyConfigured:
    # Le paramètre n'existe pas
    value = "valeur par défaut"
```

Ou créez une fonction utilitaire :

```python
def get_parameter_or_default(slug, default=None):
    try:
        return getattr(app_parameter, slug)
    except ImproperlyConfigured:
        return default

# Utilisation
title = get_parameter_or_default("SITE_TITLE", "Mon Site")
```

## Types de données

### Quels types de données sont supportés ?

Six types sont supportés :

1. **STR** : Chaînes de caractères (défaut)
2. **INT** : Nombres entiers
3. **FLT** : Nombres à virgule flottante
4. **DCL** : Nombres décimaux (précision exacte)
5. **JSN** : Structures JSON (dict, list)
6. **BOO** : Booléens (true/false)

### Quelle est la différence entre FLT et DCL ?

**FLT (Float)** :
- Nombre à virgule flottante
- Précision approximative
- Pour calculs scientifiques

**DCL (Decimal)** :
- Nombre décimal exact
- Précision absolue
- Pour calculs financiers

```python
# Float : peut avoir des erreurs d'arrondi
0.1 + 0.2  # = 0.30000000000000004

# Decimal : précision exacte
Decimal("0.1") + Decimal("0.2")  # = Decimal("0.3")
```

**Recommandation** : Utilisez **DCL** pour les prix, taux, montants financiers.

### Comment stocker une liste ou un dictionnaire ?

Utilisez le type **JSN** (JSON) :

```python
# Créer un paramètre JSON
Parameter.objects.create(
    name="API Config",
    value='{"endpoint": "https://api.com", "timeout": 30}',
    value_type=Parameter.TYPES.JSN
)

# Accéder
config = app_parameter.API_CONFIG
print(config["endpoint"])  # "https://api.com"
```

### Quelle est la limite de taille pour une valeur ?

**250 caractères** maximum.

Pour des données plus volumineuses :
- Utilisez un fichier de configuration séparé
- Stockez dans une table Django dédiée
- Utilisez un service de stockage externe

### Comment stocker une date ?

Il n'y a pas de type DATE natif. Options :

**Option 1 : Stocker comme chaîne (ISO format)**
```python
Parameter.objects.create(
    name="Launch Date",
    value="2024-12-31",
    value_type=Parameter.TYPES.STR
)

# Utilisation
from datetime import datetime
date_str = app_parameter.LAUNCH_DATE
launch_date = datetime.strptime(date_str, "%Y-%m-%d").date()
```

**Option 2 : Timestamp Unix (INT)**
```python
import time

Parameter.objects.create(
    name="Launch Date",
    value=str(int(time.time())),
    value_type=Parameter.TYPES.INT
)

# Utilisation
from datetime import datetime
timestamp = app_parameter.LAUNCH_DATE
launch_date = datetime.fromtimestamp(timestamp)
```

## Paramètres globaux et templates

### Comment rendre un paramètre disponible dans tous les templates ?

1. **Activer le context processor** dans `settings.py` :
```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ...
                'django_app_parameter.context_processors.add_global_parameter_context',
            ],
        },
    },
]
```

2. **Marquer le paramètre comme global** :
```python
param = Parameter.objects.get(slug="SITE_TITLE")
param.is_global = True
param.save()
```

3. **Utiliser dans les templates** :
```html
<title>{{ SITE_TITLE }}</title>
```

### Les paramètres dans les templates sont-ils typés ?

**Non**. Dans les templates, **tous les paramètres sont des chaînes** de caractères, quel que soit leur `value_type`.

```python
# Paramètre INT
Parameter.objects.create(name="Count", value="42", value_type="INT")

# Dans Python
count = app_parameter.COUNT  # → 42 (int)

# Dans template
{{ COUNT }}  # → "42" (str)
```

Pour les booléens dans les templates :
```html
{% if MAINTENANCE_MODE %}
    <!-- Fonctionne si value != "false", "0" ou "" -->
{% endif %}
```

### Comment éviter trop de requêtes avec les paramètres globaux ?

Le context processor effectue **1 requête par requête HTTP** pour récupérer tous les paramètres globaux.

Pour optimiser :

1. **Limitez le nombre de paramètres globaux** (< 10 recommandé)

2. **Utilisez un template tag personnalisé** pour les paramètres non fréquents :

```python
# myapp/templatetags/parameter_tags.py
from django import template
from django_app_parameter import app_parameter

register = template.Library()

@register.simple_tag
def get_parameter(slug):
    return getattr(app_parameter, slug, "")
```

```html
{% load parameter_tags %}
{% get_parameter "RARE_PARAMETER" %}
```

## Performance

### Y a-t-il un cache intégré ?

**Non**, chaque accès à `app_parameter.SLUG` effectue une requête en base de données.

Pour ajouter un cache, voir [Bonnes pratiques - Performance](best-practices.md#performance).

### Combien de requêtes sont effectuées ?

```python
# 3 requêtes séparées
title = app_parameter.SITE_TITLE    # SELECT 1
email = app_parameter.CONTACT_EMAIL # SELECT 2
phone = app_parameter.PHONE_NUMBER  # SELECT 3
```

Pour optimiser, prefetch tous les paramètres nécessaires :

```python
from django_app_parameter.models import Parameter

# 1 seule requête
slugs = ['SITE_TITLE', 'CONTACT_EMAIL', 'PHONE_NUMBER']
params = {
    p.slug: p.get()
    for p in Parameter.objects.filter(slug__in=slugs)
}

title = params['SITE_TITLE']
email = params['CONTACT_EMAIL']
phone = params['PHONE_NUMBER']
```

### Est-ce que Django App Parameter ralentit mon application ?

Cela dépend de l'utilisation :

**Impact minimal** :
- Quelques paramètres (<10) accédés occasionnellement
- Paramètres globaux limités (<5)
- Cache implémenté pour paramètres fréquents

**Impact notable** :
- Dizaines de paramètres accédés à chaque requête
- Beaucoup de paramètres globaux (>20)
- Pas de cache

**Recommandation** : Implémentez un cache pour les paramètres fréquemment utilisés.

## Slug et nommage

### Comment sont générés les slugs ?

Automatiquement depuis le `name` via la fonction `parameter_slugify` :

1. `django.utils.text.slugify()` → minuscules, hyphens
2. `.upper()` → majuscules
3. `.replace("-", "_")` → underscores

```python
"Blog Title"      → "BLOG_TITLE"
"sender e-mail"   → "SENDER_E_MAIL"
"Café Français"   → "CAFE_FRANCAIS"
```

### Puis-je définir un slug personnalisé ?

Oui, mais **seulement à la création** :

```python
# Via create_or_update
Parameter.objects.create_or_update({
    "slug": "MY_CUSTOM_SLUG",
    "name": "My Parameter",
    "value": "value"
})

# Via load_param
python manage.py load_param --json '[{"slug": "CUSTOM", "name": "param", "value": "val"}]'
```

**Important** : Le slug ne peut **pas** être modifié après création (readonly dans l'admin).

### Puis-je renommer un paramètre ?

Renommer le `name` changera le slug lors de la prochaine sauvegarde, ce qui **cassera** les références dans le code.

**Mieux vaut** :
1. Créer un nouveau paramètre avec le nouveau nom
2. Mettre à jour le code pour utiliser le nouveau slug
3. Supprimer l'ancien paramètre

### Que se passe-t-il si deux paramètres ont le même slug ?

Le slug est **unique** (contrainte de base de données). Si vous tentez de créer un paramètre avec un slug existant :

```python
# Paramètre existant : BLOG_TITLE
Parameter.objects.create(name="Blog Title", value="test")
# → IntegrityError: UNIQUE constraint failed
```

`create_or_update()` gère ce cas en mettant à jour le paramètre existant.

## Sécurité

### Puis-je stocker des mots de passe dans les paramètres ?

**NON**, absolument pas. Les paramètres sont :
- Stockés en clair dans la BDD
- Visibles dans l'admin Django
- Potentiellement loggés

**Utilisez plutôt** :
- Variables d'environnement (`os.environ`)
- Django settings avec secrets
- Gestionnaire de secrets (AWS Secrets Manager, HashiCorp Vault)

### Qui peut modifier les paramètres ?

Par défaut, tous les utilisateurs avec accès à l'admin Django et les permissions appropriées.

**Recommandation** : Restreignez l'accès via les permissions Django (voir [Bonnes pratiques - Sécurité](best-practices.md#sécurité)).

### Les paramètres sont-ils validés ?

**Non**, il n'y a pas de validation automatique des valeurs au niveau du modèle.

**Bonnes pratiques** :
- Validez dans votre code lors de l'accès
- Utilisez des fonctions wrapper avec validation
- Vérifiez les paramètres critiques au démarrage de l'application

## Commande load_param

### Quelle est la différence entre --file et --json ?

**--file** : Charge depuis un fichier JSON
```bash
python manage.py load_param --file parameters.json
```

**--json** : Charge depuis une chaîne JSON
```bash
python manage.py load_param --json '[{"name": "test", "value": "val"}]'
```

### À quoi sert l'option --no-update ?

`--no-update` empêche la mise à jour des paramètres existants :

```bash
python manage.py load_param --no-update --file required.json
```

**Comportement** :
- Paramètres manquants → créés
- Paramètres existants → **ignorés** (valeurs conservées)

**Cas d'usage** : Définir des valeurs par défaut sans écraser les modifications en production.

### Comment charger des paramètres depuis plusieurs fichiers ?

Exécutez la commande plusieurs fois :

```bash
python manage.py load_param --file base.json
python manage.py load_param --file features.json
python manage.py load_param --file environment.json
```

Ou créez un script shell :

```bash
#!/bin/bash
for file in config/parameters/*.json; do
    python manage.py load_param --file "$file"
done
```

### Puis-je utiliser load_param dans un script Python ?

Oui, via `call_command` :

```python
from django.core.management import call_command

call_command('load_param', file='parameters.json')
call_command('load_param', json='[...]', no_update=True)
```

## Erreurs courantes

### ImproperlyConfigured: Parameter with slug 'XXX' does not exist

**Cause** : Le paramètre n'existe pas en base de données.

**Solutions** :
1. Créez le paramètre via l'admin ou le code
2. Utilisez une valeur par défaut :
```python
try:
    value = app_parameter.XXX
except ImproperlyConfigured:
    value = "default_value"
```

### ValueError: invalid literal for int() with base 10

**Cause** : Tentative de conversion d'une valeur non-numérique en int.

**Exemple** :
```python
# Paramètre avec value="abc"
count = Parameter.objects.int("PARAM")  # ValueError
```

**Solutions** :
1. Vérifiez la valeur dans l'admin
2. Gérez l'exception :
```python
try:
    count = Parameter.objects.int("PARAM")
except ValueError:
    count = 0  # Valeur par défaut
```

### JSONDecodeError: Expecting value

**Cause** : Valeur JSON invalide.

**Exemple** :
```python
# Paramètre avec value="{invalid json"
config = Parameter.objects.json("CONFIG")  # JSONDecodeError
```

**Solutions** :
1. Validez le JSON dans l'admin
2. Utilisez un validateur JSON en ligne
3. Gérez l'exception :
```python
import json

try:
    config = Parameter.objects.json("CONFIG")
except json.JSONDecodeError:
    config = {}  # Valeur par défaut
```

### You can't set an app parameter at run time

**Cause** : Tentative de modification via `app_parameter` :

```python
app_parameter.SITE_TITLE = "New Title"  # Exception!
```

**Solution** : Modifiez via l'ORM :
```python
param = Parameter.objects.get(slug="SITE_TITLE")
param.value = "New Title"
param.save()
```

### Table 'django_app_parameter_parameter' doesn't exist

**Cause** : Migrations non appliquées.

**Solution** :
```bash
python manage.py migrate django_app_parameter
```

## Avancé

### Comment ajouter un nouveau type de données ?

1. **Ajouter dans TYPES** :
```python
class TYPES(models.TextChoices):
    # ... types existants
    DAT = "DAT", "Date"
```

2. **Créer la migration** :
```bash
python manage.py makemigrations
python manage.py migrate
```

3. **Ajouter les méthodes de conversion** :
```python
def date(self):
    from datetime import datetime
    return datetime.strptime(self.value, "%Y-%m-%d").date()

def get(self):
    # ... conversions existantes
    if self.value_type == self.TYPES.DAT:
        return self.date()
```

4. **Ajouter au Manager** :
```python
def date(self, slug):
    return self.get_from_slug(slug).date()
```

### Comment tracer les modifications de paramètres ?

Utilisez les signals Django :

```python
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django_app_parameter.models import Parameter
import logging

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Parameter)
def log_parameter_change(sender, instance, **kwargs):
    if instance.pk:
        old = Parameter.objects.get(pk=instance.pk)
        if old.value != instance.value:
            logger.info(
                f"Parameter {instance.slug} changed: "
                f"{old.value} → {instance.value}"
            )
```

### Puis-je utiliser Django App Parameter avec Celery ?

Oui, mais attention aux caches. Si vous implémentez un cache :

```python
# tasks.py
from celery import shared_task
from myapp.parameters import CachedParameters

@shared_task
def my_task():
    # Les workers Celery auront leur propre cache
    value = CachedParameters.get("MY_PARAM")
```

**Recommandation** : Utilisez un cache partagé (Redis, Memcached) plutôt qu'un cache local.

### Comment tester du code qui utilise des paramètres ?

Créez les paramètres dans vos fixtures de test :

```python
# tests.py
import pytest
from django_app_parameter.models import Parameter

@pytest.fixture
def parameters(db):
    """Crée des paramètres de test."""
    Parameter.objects.create(
        name="Site Title",
        value="Test Site",
        value_type=Parameter.TYPES.STR
    )
    Parameter.objects.create(
        name="Max Size",
        value="1000",
        value_type=Parameter.TYPES.INT
    )

def test_my_view(client, parameters):
    response = client.get('/')
    # Le paramètre SITE_TITLE existe dans la BDD de test
    assert response.status_code == 200
```

## Comparaisons

### Django App Parameter vs django-constance

**django-app-parameter** :
- ✅ Plus simple et léger
- ✅ Paramètres illimités
- ✅ Commande de chargement en masse
- ❌ Pas de validation intégrée
- ❌ Pas de cache intégré
- ❌ Interface admin basique

**django-constance** :
- ✅ Validation des valeurs
- ✅ Cache Redis intégré
- ✅ Interface admin enrichie
- ❌ Configuration globale requise
- ❌ Nombre de paramètres limité

**Recommandation** :
- **django-app-parameter** : Projets simples, nombreux paramètres
- **django-constance** : Projets complexes, validation stricte

### Django App Parameter vs variables d'environnement

**Paramètres (app_parameter)** :
- ✅ Modifiables via l'admin (sans redémarrage)
- ✅ Interface utilisateur
- ✅ Historisation possible (avec signals)
- ❌ Ne pas utiliser pour les secrets

**Variables d'environnement** :
- ✅ Sécurisé pour les secrets
- ✅ Configuration par environnement
- ✅ Standard pour Docker/K8s
- ❌ Nécessite redémarrage pour modifier

**Recommandation** : Utilisez **les deux** :
- Env vars : Secrets, config environnement
- App parameters : Configuration métier modifiable

## Support et contribution

### Où signaler un bug ?

GitHub Issues : [github.com/Swannbm/django-app-parameter/issues](https://github.com/Swannbm/django-app-parameter/issues)

### Comment contribuer ?

1. Fork le repository
2. Créez une branche pour votre feature
3. Écrivez des tests
4. Assurez-vous que tous les tests passent
5. Soumettez une Pull Request

### Où trouver de l'aide ?

- [README officiel](https://github.com/Swannbm/django-app-parameter/blob/master/README.md)
- [Cette documentation](README.md)
- GitHub Issues pour les questions

## Ressources additionnelles

- [Guide d'installation](installation.md)
- [Guide d'utilisation](usage-guide.md)
- [Référence API](api-reference.md)
- [Bonnes pratiques](best-practices.md)
- [Architecture technique](architecture.md)
