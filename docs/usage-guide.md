# Guide d'utilisation

Ce guide présente les différentes façons d'utiliser Django App Parameter avec des exemples pratiques.

## Table des matières

- [Accès aux paramètres](#accès-aux-paramètres)
- [Gestion des types de données](#gestion-des-types-de-données)
- [Utilisation dans les vues](#utilisation-dans-les-vues)
- [Utilisation dans les templates](#utilisation-dans-les-templates)
- [Gestion des paramètres via l'admin](#gestion-des-paramètres-via-ladmin)
- [Chargement en masse](#chargement-en-masse)
- [Patterns avancés](#patterns-avancés)

## Accès aux paramètres

### Pattern 1 : Proxy (recommandé)

Le moyen le plus simple et intuitif d'accéder aux paramètres :

```python
from django_app_parameter import app_parameter

# Accès direct avec conversion automatique de type
title = app_parameter.BLOG_TITLE  # → str
year = app_parameter.BIRTH_YEAR   # → int
rate = app_parameter.TAX_RATE     # → Decimal
config = app_parameter.API_CONFIG  # → dict (JSON)
enabled = app_parameter.FEATURE_ENABLED  # → bool
```

**Avantages** :
- Syntaxe concise
- Conversion automatique selon `value_type`
- Similaire à `django.conf.settings`
- Lisible et maintenable

**Inconvénients** :
- Lève une exception si le paramètre n'existe pas
- Pas de valeur par défaut possible

### Pattern 2 : Manager avec type explicite

Accès via le manager avec méthode de type explicite :

```python
from django_app_parameter.models import Parameter

# Méthodes typées explicites
title = Parameter.objects.str("BLOG_TITLE")
year = Parameter.objects.int("BIRTH_YEAR")
rate = Parameter.objects.decimal("TAX_RATE")
price = Parameter.objects.float("PRICE")
config = Parameter.objects.json("API_CONFIG")
enabled = Parameter.objects.bool("FEATURE_ENABLED")
```

**Avantages** :
- Type explicite dans le code
- Plus facile à déboguer
- IDE peut suggérer les types de retour

### Pattern 3 : Accès via l'objet Parameter

Accès complet à l'objet Parameter :

```python
from django_app_parameter.models import Parameter

# Récupérer l'objet complet
param = Parameter.objects.get_from_slug("BLOG_TITLE")

# Accès aux propriétés
print(param.name)         # "Blog Title"
print(param.slug)         # "BLOG_TITLE"
print(param.value_type)   # "STR"
print(param.description)  # Description du paramètre
print(param.is_global)    # True/False

# Conversion de type
value_as_str = param.str()
value_auto = param.get()  # Conversion automatique selon value_type
```

**Avantages** :
- Accès aux métadonnées
- Conversion manuelle possible
- Utile pour l'inspection

## Gestion des types de données

### Type STR (Chaîne de caractères)

Type par défaut. Stocke du texte brut.

```python
# Création
Parameter.objects.create(
    name="Site Title",
    value="Mon Super Site",
    value_type=Parameter.TYPES.STR
)

# Utilisation
title = app_parameter.SITE_TITLE
print(title)  # "Mon Super Site"
print(type(title))  # <class 'str'>
```

**Cas d'usage** :
- Titres, descriptions
- URLs, emails
- Messages, libellés
- Tout texte simple

### Type INT (Nombre entier)

Pour les nombres entiers sans décimales.

```python
# Création
Parameter.objects.create(
    name="Max Upload Size",
    value="5242880",  # 5 Mo en octets
    value_type=Parameter.TYPES.INT
)

# Utilisation
max_size = app_parameter.MAX_UPLOAD_SIZE
print(max_size)  # 5242880
print(type(max_size))  # <class 'int'>

# Calculs
if file.size > max_size:
    raise ValidationError("Fichier trop volumineux")
```

**Cas d'usage** :
- Tailles (octets)
- Limites, seuils
- Compteurs
- Années
- Quantités

### Type FLT (Float)

Pour les nombres à virgule flottante.

```python
# Création
Parameter.objects.create(
    name="PI Value",
    value="3.14159",
    value_type=Parameter.TYPES.FLT
)

# Utilisation
pi = app_parameter.PI_VALUE
print(pi)  # 3.14159
print(type(pi))  # <class 'float'>

# Calculs
circumference = 2 * pi * radius
```

**Cas d'usage** :
- Calculs scientifiques
- Coordonnées GPS
- Coefficients
- Ratios approximatifs

**Attention** : Pour l'argent, préférez DCL (Decimal) pour éviter les erreurs d'arrondi.

### Type DCL (Decimal)

Pour les nombres à virgule avec précision exacte.

```python
# Création
Parameter.objects.create(
    name="Tax Rate",
    value="20.00",
    value_type=Parameter.TYPES.DCL
)

# Utilisation
from decimal import Decimal

tax_rate = app_parameter.TAX_RATE
print(tax_rate)  # Decimal('20.00')
print(type(tax_rate))  # <class 'decimal.Decimal'>

# Calculs financiers
price = Decimal("99.99")
tax = price * (tax_rate / 100)
total = price + tax
```

**Cas d'usage** :
- Prix, montants financiers
- Taux de TVA, taxes
- Pourcentages précis
- Tout calcul nécessitant une précision exacte

**Avantage** : Évite les erreurs d'arrondi des floats (`0.1 + 0.2 != 0.3` en float).

### Type JSN (JSON)

Pour les structures de données complexes (dictionnaires, listes).

```python
# Création
Parameter.objects.create(
    name="API Config",
    value='{"endpoint": "https://api.example.com", "timeout": 30, "retry": 3}',
    value_type=Parameter.TYPES.JSN
)

# Utilisation
config = app_parameter.API_CONFIG
print(config)  # {'endpoint': 'https://api.example.com', 'timeout': 30, 'retry': 3}
print(type(config))  # <class 'dict'>

# Accès aux données
endpoint = config["endpoint"]
timeout = config.get("timeout", 10)
```

**Exemples de structures** :

Liste simple :
```json
["option1", "option2", "option3"]
```

Dictionnaire de configuration :
```json
{
    "email": {
        "from": "noreply@example.com",
        "reply_to": "support@example.com"
    },
    "features": {
        "beta": true,
        "maintenance": false
    }
}
```

**Cas d'usage** :
- Configuration multi-valeurs
- Listes d'options
- Paramètres structurés
- Mapping de valeurs

**Limite** : 250 caractères maximum. Pour des JSON volumineux, considérez un fichier séparé.

### Type BOO (Boolean)

Pour les valeurs booléennes (vrai/faux).

```python
# Création
Parameter.objects.create(
    name="Maintenance Mode",
    value="false",
    value_type=Parameter.TYPES.BOO
)

# Utilisation
maintenance = app_parameter.MAINTENANCE_MODE
print(maintenance)  # False
print(type(maintenance))  # <class 'bool'>

if maintenance:
    return HttpResponse("Site en maintenance")
```

**Valeurs considérées comme False** :
- `""` (chaîne vide)
- `"false"` (insensible à la casse)
- `"False"`
- `"0"`

**Toutes les autres valeurs** sont considérées comme True :
- `"true"`, `"True"`
- `"1"`
- `"yes"`, `"oui"`
- Toute autre chaîne non vide

**Cas d'usage** :
- Feature flags
- Mode maintenance
- Options on/off
- Activation de modules

## Utilisation dans les vues

### Vue basique

```python
from django.shortcuts import render
from django_app_parameter import app_parameter

def home(request):
    context = {
        'site_title': app_parameter.SITE_TITLE,
        'maintenance': app_parameter.MAINTENANCE_MODE,
    }
    return render(request, 'home.html', context)
```

### Vue avec gestion d'erreur

```python
from django.shortcuts import render
from django.core.exceptions import ImproperlyConfigured
from django_app_parameter import app_parameter

def blog_list(request):
    try:
        items_per_page = app_parameter.ITEMS_PER_PAGE
    except ImproperlyConfigured:
        items_per_page = 10  # Valeur par défaut

    # ... logique de pagination
```

### Vue avec feature flag

```python
from django.http import HttpResponse, Http404
from django_app_parameter import app_parameter

def beta_feature(request):
    if not app_parameter.ENABLE_BETA_FEATURE:
        raise Http404("Cette fonctionnalité n'est pas disponible")

    # Logique de la fonctionnalité beta
    return render(request, 'beta_feature.html')
```

### Vue basée sur une classe

```python
from django.views.generic import TemplateView
from django_app_parameter import app_parameter

class AboutView(TemplateView):
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = app_parameter.COMPANY_NAME
        context['contact_email'] = app_parameter.CONTACT_EMAIL
        context['phone'] = app_parameter.PHONE_NUMBER
        return context
```

### Middleware personnalisé

```python
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from django_app_parameter import app_parameter

class MaintenanceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Autoriser l'accès admin même en maintenance
        if request.path.startswith('/admin/'):
            return None

        if app_parameter.MAINTENANCE_MODE:
            return HttpResponse(
                app_parameter.MAINTENANCE_MESSAGE,
                status=503
            )

        return None
```

## Utilisation dans les templates

### Configuration requise

Ajoutez le context processor dans `settings.py` :

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

### Marquer un paramètre comme global

Via l'admin ou le code :

```python
param = Parameter.objects.get(slug="SITE_TITLE")
param.is_global = True
param.save()
```

Ou à la création :

```python
Parameter.objects.create(
    name="Site Title",
    value="Mon Site",
    is_global=True  # ← Important
)
```

### Utilisation dans les templates

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ SITE_TITLE }}</title>
    <meta name="description" content="{{ SITE_DESCRIPTION }}">
</head>
<body>
    <header>
        <h1>{{ SITE_TITLE }}</h1>
        <p>{{ SITE_TAGLINE }}</p>
    </header>

    <main>
        {% if MAINTENANCE_MODE %}
            <div class="alert alert-warning">
                {{ MAINTENANCE_MESSAGE }}
            </div>
        {% endif %}

        <!-- Contenu -->
    </main>

    <footer>
        <p>{{ FOOTER_TEXT }}</p>
        <p>Contact : {{ CONTACT_EMAIL }}</p>
    </footer>
</body>
</html>
```

**Important** : Dans les templates, tous les paramètres sont des chaînes de caractères, quel que soit leur `value_type`.

```html
<!-- Paramètre booléen : comparaison avec string -->
{% if MAINTENANCE_MODE == "true" %}
    <!-- En maintenance -->
{% endif %}

<!-- Ou plus simple (chaîne non vide = True) -->
{% if MAINTENANCE_MODE %}
    <!-- Fonctionne si value != "false" ou "0" ou "" -->
{% endif %}
```

## Gestion des paramètres via l'admin

### Créer un paramètre

1. Accédez à `/admin/django_app_parameter/parameter/`
2. Cliquez sur "Ajouter Parameter"
3. Remplissez :
   - **Nom** : Nom lisible (ex: "Blog Title")
   - **Type de donnée** : Sélectionnez le type
   - **Valeur** : Entrez la valeur
   - **Description** : Documentation (optionnel)
   - **Is global** : Cochez pour l'accès template
4. Enregistrez

Le slug sera généré automatiquement : `BLOG_TITLE`

### Modifier un paramètre

1. Accédez à la liste des paramètres
2. Cliquez sur le paramètre à modifier
3. Modifiez la valeur ou d'autres champs
4. Enregistrez

**Note** : Le slug est en lecture seule et ne peut pas être modifié après création.

### Rechercher un paramètre

Utilisez la barre de recherche pour trouver un paramètre par :
- Nom
- Slug
- Description
- Valeur

### Filtrer les paramètres

Utilisez les filtres sur le côté droit pour afficher :
- Par type de donnée (INT, STR, etc.)
- Paramètres globaux uniquement
- Paramètres non globaux

### Supprimer un paramètre

1. Sélectionnez le(s) paramètre(s) à supprimer
2. Dans le menu "Action", choisissez "Supprimer les parameters sélectionnés"
3. Confirmez la suppression

**Attention** : Si votre code référence ce paramètre, cela causera une erreur `ImproperlyConfigured`.

## Chargement en masse

### Format JSON

Créez un fichier JSON avec vos paramètres :

```json
[
    {
        "name": "Site Title",
        "value": "Mon Super Site",
        "value_type": "STR",
        "description": "Titre principal du site",
        "is_global": true
    },
    {
        "name": "Max Upload Size",
        "value": "10485760",
        "value_type": "INT",
        "description": "Taille max en octets (10 Mo)"
    },
    {
        "name": "Tax Rate",
        "value": "20.00",
        "value_type": "DCL",
        "description": "Taux de TVA"
    },
    {
        "slug": "CUSTOM_SLUG",
        "name": "Custom Parameter",
        "value": "custom value"
    }
]
```

**Champs disponibles** :
- `name` (requis) : Nom du paramètre
- `value` (optionnel, défaut: `""`) : Valeur
- `value_type` (optionnel, défaut: `"STR"`) : Type de données
- `description` (optionnel, défaut: `""`) : Description
- `is_global` (optionnel, défaut: `false`) : Disponibilité template
- `slug` (optionnel) : Slug personnalisé (sinon auto-généré)

### Commande load_param

#### Charger depuis un fichier

```bash
python manage.py load_param --file parameters.json
```

#### Charger depuis une chaîne JSON

```bash
python manage.py load_param --json '[{"name": "test", "value": "hello"}]'
```

#### Charger sans écraser les existants

```bash
python manage.py load_param --no-update --file required_params.json
```

Avec `--no-update` :
- Crée les paramètres manquants
- N'écrase PAS les paramètres existants
- Utile pour les paramètres requis dans un déploiement

#### Utilisation dans un script de déploiement

```bash
#!/bin/bash
# deploy.sh

echo "Applying migrations..."
python manage.py migrate

echo "Loading required parameters..."
python manage.py load_param --no-update --file config/required_parameters.json

echo "Loading default parameters..."
python manage.py load_param --file config/default_parameters.json

echo "Starting application..."
gunicorn myproject.wsgi
```

### Utilisation programmatique

```python
from django.core.management import call_command

# Dans une commande de management ou un script
call_command('load_param', file='parameters.json')
call_command('load_param', json='[{"name": "test", "value": "val"}]')
call_command('load_param', file='params.json', no_update=True)
```

## Patterns avancés

### Pattern : Cache des paramètres

Pour éviter trop de requêtes BDD :

```python
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django_app_parameter import app_parameter

class CachedParameter:
    """Wrapper avec cache pour les paramètres."""

    @staticmethod
    def get(slug, timeout=3600, default=None):
        """
        Récupère un paramètre avec cache.

        Args:
            slug: Slug du paramètre
            timeout: Durée du cache en secondes
            default: Valeur par défaut si paramètre manquant

        Returns:
            Valeur du paramètre (type converti automatiquement)
        """
        cache_key = f"app_param_{slug}"
        value = cache.get(cache_key)

        if value is None:
            try:
                value = getattr(app_parameter, slug)
                cache.set(cache_key, value, timeout)
            except ImproperlyConfigured:
                if default is not None:
                    return default
                raise

        return value

    @staticmethod
    def invalidate(slug):
        """Invalide le cache d'un paramètre."""
        cache_key = f"app_param_{slug}"
        cache.delete(cache_key)

# Utilisation
title = CachedParameter.get("SITE_TITLE")
max_size = CachedParameter.get("MAX_UPLOAD_SIZE", default=5242880)
```

### Pattern : Valeurs par défaut

Wrapper pour gérer les paramètres manquants :

```python
from django.core.exceptions import ImproperlyConfigured
from django_app_parameter import app_parameter

def get_parameter(slug, default=None):
    """
    Récupère un paramètre avec valeur par défaut.

    Args:
        slug: Slug du paramètre
        default: Valeur retournée si paramètre manquant

    Returns:
        Valeur du paramètre ou default
    """
    try:
        return getattr(app_parameter, slug)
    except ImproperlyConfigured:
        return default

# Utilisation
items_per_page = get_parameter("ITEMS_PER_PAGE", default=20)
```

### Pattern : Configuration groupée

Gérer des configurations liées via JSON :

```python
# Créer un paramètre JSON pour la config email
Parameter.objects.create(
    name="Email Config",
    value='''{
        "from": "noreply@example.com",
        "reply_to": "support@example.com",
        "footer": "Merci de votre confiance",
        "smtp": {
            "host": "smtp.example.com",
            "port": 587
        }
    }''',
    value_type=Parameter.TYPES.JSN
)

# Utilisation
email_config = app_parameter.EMAIL_CONFIG
from_address = email_config["from"]
smtp_host = email_config["smtp"]["host"]
```

### Pattern : Feature flags avec décorateur

```python
from functools import wraps
from django.http import Http404
from django_app_parameter import app_parameter

def feature_flag(slug):
    """
    Décorateur pour protéger une vue avec un feature flag.

    Usage:
        @feature_flag("ENABLE_BETA_FEATURE")
        def my_beta_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            try:
                enabled = getattr(app_parameter, slug)
                if not enabled:
                    raise Http404("Cette fonctionnalité n'est pas disponible")
            except Exception:
                raise Http404("Cette fonctionnalité n'est pas disponible")

            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator

# Utilisation
@feature_flag("ENABLE_BETA_DASHBOARD")
def beta_dashboard(request):
    return render(request, 'beta/dashboard.html')
```

### Pattern : Validation de paramètres

Valider les paramètres au démarrage de l'application :

```python
# myapp/apps.py
from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured

class MyAppConfig(AppConfig):
    name = 'myapp'

    def ready(self):
        """Vérifie que tous les paramètres requis existent."""
        from django_app_parameter import app_parameter

        required_params = [
            'SITE_TITLE',
            'CONTACT_EMAIL',
            'MAX_UPLOAD_SIZE',
        ]

        missing = []
        for slug in required_params:
            try:
                getattr(app_parameter, slug)
            except ImproperlyConfigured:
                missing.append(slug)

        if missing:
            raise ImproperlyConfigured(
                f"Paramètres manquants : {', '.join(missing)}"
            )
```

### Pattern : Paramètres par environnement

Charger différents paramètres selon l'environnement :

```python
# management/commands/setup_env.py
from django.core.management.base import BaseCommand
from django.conf import settings
from django_app_parameter.models import Parameter

class Command(BaseCommand):
    help = 'Configure les paramètres selon l\'environnement'

    def handle(self, *args, **options):
        env = getattr(settings, 'ENVIRONMENT', 'production')

        if env == 'development':
            self.setup_development()
        elif env == 'staging':
            self.setup_staging()
        else:
            self.setup_production()

    def setup_development(self):
        Parameter.objects.update_or_create(
            slug='DEBUG_MODE',
            defaults={
                'name': 'Debug Mode',
                'value': 'true',
                'value_type': 'BOO'
            }
        )

    def setup_staging(self):
        Parameter.objects.update_or_create(
            slug='DEBUG_MODE',
            defaults={
                'name': 'Debug Mode',
                'value': 'false',
                'value_type': 'BOO'
            }
        )

    def setup_production(self):
        Parameter.objects.update_or_create(
            slug='DEBUG_MODE',
            defaults={
                'name': 'Debug Mode',
                'value': 'false',
                'value_type': 'BOO'
            }
        )
```

## Prochaines étapes

- [Référence complète de l'API](api-reference.md)
- [Commande de gestion load_param](management-commands.md)
- [Bonnes pratiques](best-practices.md)
