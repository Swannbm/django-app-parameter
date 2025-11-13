# Bonnes pratiques

Guide des meilleures pratiques pour utiliser Django App Parameter efficacement et en toute sécurité.

## Table des matières

- [Sécurité](#sécurité)
- [Performance](#performance)
- [Organisation](#organisation)
- [Nommage](#nommage)
- [Documentation](#documentation)
- [Déploiement](#déploiement)
- [Maintenance](#maintenance)

## Sécurité

### ❌ NE JAMAIS stocker de données sensibles

**Données à ÉVITER** :
- Mots de passe
- Clés API privées
- Tokens d'authentification
- Secrets de session
- Credentials de base de données
- Clés de chiffrement

**Pourquoi ?**
- Stockage en clair dans la BDD
- Visible dans l'admin Django
- Logs potentiels
- Backups non chiffrés

**Alternative** :
```python
# ❌ MAUVAIS
Parameter.objects.create(
    name="API Secret Key",
    value="sk_live_abc123xyz"  # JAMAIS ça !
)

# ✅ BON : Utilisez les variables d'environnement
import os
API_SECRET = os.environ.get('API_SECRET_KEY')

# ✅ BON : Utilisez Django settings
from django.conf import settings
API_SECRET = settings.API_SECRET_KEY
```

### Limiter les permissions admin

Restreignez l'accès à la modification des paramètres :

```python
# myapp/admin.py
from django.contrib import admin
from django_app_parameter.models import Parameter
from django_app_parameter.admin import ParameterAdmin

# Désenregistrer l'admin par défaut
admin.site.unregister(Parameter)

# Réenregistrer avec permissions restreintes
@admin.register(Parameter)
class RestrictedParameterAdmin(ParameterAdmin):
    def has_delete_permission(self, request, obj=None):
        # Seuls les superusers peuvent supprimer
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Groupe "Parameter Managers" peut modifier
        return (
            request.user.is_superuser or
            request.user.groups.filter(name='Parameter Managers').exists()
        )
```

### Valider les valeurs critiques

Pour les paramètres critiques, ajoutez une validation :

```python
# myapp/utils.py
from django.core.exceptions import ImproperlyConfigured
from django_app_parameter import app_parameter

def get_validated_parameter(slug, validator=None):
    """
    Récupère un paramètre avec validation optionnelle.

    Args:
        slug: Slug du paramètre
        validator: Fonction de validation (value) -> bool

    Returns:
        Valeur validée

    Raises:
        ImproperlyConfigured: Si paramètre manquant ou invalide
    """
    try:
        value = getattr(app_parameter, slug)
    except ImproperlyConfigured:
        raise ImproperlyConfigured(f"Paramètre requis manquant : {slug}")

    if validator and not validator(value):
        raise ImproperlyConfigured(
            f"Paramètre {slug} a une valeur invalide : {value}"
        )

    return value

# Utilisation
def validate_positive(value):
    return isinstance(value, int) and value > 0

max_size = get_validated_parameter(
    "MAX_UPLOAD_SIZE",
    validator=validate_positive
)
```

### Audit des modifications

Tracez les modifications de paramètres :

```python
# myapp/signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django_app_parameter.models import Parameter
import logging

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Parameter)
def log_parameter_change(sender, instance, **kwargs):
    """Logge les modifications de paramètres."""
    if instance.pk:  # Modification (pas création)
        try:
            old = Parameter.objects.get(pk=instance.pk)
            if old.value != instance.value:
                logger.warning(
                    f"Parameter {instance.slug} changed: "
                    f"{old.value} → {instance.value}"
                )
        except Parameter.DoesNotExist:
            pass

@receiver(post_save, sender=Parameter)
def log_parameter_creation(sender, instance, created, **kwargs):
    """Logge les créations de paramètres."""
    if created:
        logger.info(f"Parameter created: {instance.slug} = {instance.value}")
```

## Performance

### Utiliser un cache pour les paramètres fréquents

```python
# myapp/parameters.py
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django_app_parameter import app_parameter

class CachedParameters:
    """Gestionnaire de paramètres avec cache."""

    CACHE_TIMEOUT = 3600  # 1 heure

    @classmethod
    def get(cls, slug, default=None, timeout=None):
        """
        Récupère un paramètre avec cache.

        Args:
            slug: Slug du paramètre
            default: Valeur par défaut si manquant
            timeout: Durée du cache (défaut: 1h)

        Returns:
            Valeur du paramètre (cachée)
        """
        timeout = timeout or cls.CACHE_TIMEOUT
        cache_key = f"param_{slug}"

        # Tenter depuis le cache
        value = cache.get(cache_key)
        if value is not None:
            return value

        # Récupérer depuis la BDD
        try:
            value = getattr(app_parameter, slug)
        except ImproperlyConfigured:
            if default is not None:
                return default
            raise

        # Mettre en cache
        cache.set(cache_key, value, timeout)
        return value

    @classmethod
    def invalidate(cls, slug):
        """Invalide le cache d'un paramètre."""
        cache_key = f"param_{slug}"
        cache.delete(cache_key)

    @classmethod
    def invalidate_all(cls):
        """Invalide tous les paramètres en cache."""
        # Nécessite un pattern de clés ou prefix
        cache.delete_pattern("param_*")

# Utilisation
from myapp.parameters import CachedParameters

# Première fois : BDD + mise en cache
title = CachedParameters.get("BLOG_TITLE")

# Fois suivantes (pendant 1h) : depuis le cache
title = CachedParameters.get("BLOG_TITLE")

# Avec valeur par défaut
max_size = CachedParameters.get("MAX_SIZE", default=5242880)

# Invalider après modification
CachedParameters.invalidate("BLOG_TITLE")
```

### Signal pour invalidation automatique

```python
# myapp/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_app_parameter.models import Parameter
from myapp.parameters import CachedParameters

@receiver(post_save, sender=Parameter)
def invalidate_cache_on_save(sender, instance, **kwargs):
    """Invalide le cache quand un paramètre est modifié."""
    CachedParameters.invalidate(instance.slug)

@receiver(post_delete, sender=Parameter)
def invalidate_cache_on_delete(sender, instance, **kwargs):
    """Invalide le cache quand un paramètre est supprimé."""
    CachedParameters.invalidate(instance.slug)
```

### Limiter les paramètres globaux

Le context processor s'exécute à **chaque requête**. Limitez le nombre de paramètres avec `is_global=True`.

```python
# ❌ MAUVAIS : Trop de paramètres globaux
# 50 paramètres avec is_global=True
# → 1 requête avec 50 résultats à chaque requête

# ✅ BON : Seulement ce qui est vraiment global
# 3-5 paramètres avec is_global=True (titre, footer, etc.)
# → Requête rapide à chaque requête

# ✅ MEILLEUR : Template tag personnalisé pour les autres
{% load parameter_tags %}
{% get_parameter "SPECIFIC_VALUE" as value %}
```

Template tag personnalisé :

```python
# myapp/templatetags/parameter_tags.py
from django import template
from django.core.exceptions import ImproperlyConfigured
from myapp.parameters import CachedParameters

register = template.Library()

@register.simple_tag
def get_parameter(slug, default=None):
    """
    Récupère un paramètre dans un template (avec cache).

    Usage: {% get_parameter "BLOG_TITLE" %}
    """
    try:
        return CachedParameters.get(slug, default=default)
    except ImproperlyConfigured:
        return default
```

### Prefetch pour multiples paramètres

Si vous avez besoin de plusieurs paramètres dans une vue :

```python
# ❌ MAUVAIS : N requêtes
def my_view(request):
    title = app_parameter.BLOG_TITLE      # Requête 1
    email = app_parameter.CONTACT_EMAIL    # Requête 2
    max_size = app_parameter.MAX_SIZE      # Requête 3
    # ...

# ✅ BON : 1 requête pour tous
def my_view(request):
    slugs = ['BLOG_TITLE', 'CONTACT_EMAIL', 'MAX_SIZE']
    params = {
        p.slug: p.get()
        for p in Parameter.objects.filter(slug__in=slugs)
    }

    title = params['BLOG_TITLE']
    email = params['CONTACT_EMAIL']
    max_size = params['MAX_SIZE']
```

## Organisation

### Structure de paramètres recommandée

Organisez vos paramètres par catégorie :

```python
# config/parameters/
├── base.json           # Paramètres de base (tous environnements)
├── branding.json       # Branding (logo, couleurs, etc.)
├── features.json       # Feature flags
├── limits.json         # Limites et quotas
├── email.json          # Configuration email
└── integrations.json   # Intégrations tierces
```

**base.json** :
```json
[
    {
        "name": "Site Title",
        "value": "Mon Application",
        "is_global": true,
        "description": "Titre principal du site"
    },
    {
        "name": "Items Per Page",
        "value": "20",
        "value_type": "INT",
        "description": "Nombre d'items par page dans les listes"
    }
]
```

**features.json** :
```json
[
    {
        "name": "Enable Beta Dashboard",
        "value": "false",
        "value_type": "BOO",
        "description": "Active le nouveau tableau de bord (beta)"
    },
    {
        "name": "Maintenance Mode",
        "value": "false",
        "value_type": "BOO",
        "is_global": true,
        "description": "Active le mode maintenance sur tout le site"
    }
]
```

### Préfixes pour les slugs

Utilisez des préfixes pour grouper les paramètres :

```python
# Préfixes par catégorie
SITE_TITLE              # Site général
SITE_DESCRIPTION
SITE_LOGO_URL

EMAIL_FROM              # Email
EMAIL_REPLY_TO
EMAIL_FOOTER

FEATURE_BETA_DASHBOARD  # Features
FEATURE_NEW_UI
FEATURE_ANALYTICS

LIMIT_MAX_UPLOAD_SIZE   # Limites
LIMIT_MAX_ITEMS
LIMIT_RATE_PER_MINUTE

API_ENDPOINT            # Intégrations
API_TIMEOUT
API_RETRY_COUNT
```

### Constantes pour les slugs

Définissez des constantes pour éviter les typos :

```python
# myapp/constants.py
class ParameterSlugs:
    """Slugs de paramètres de l'application."""

    # Site
    SITE_TITLE = "SITE_TITLE"
    SITE_DESCRIPTION = "SITE_DESCRIPTION"

    # Email
    EMAIL_FROM = "EMAIL_FROM"
    EMAIL_REPLY_TO = "EMAIL_REPLY_TO"

    # Features
    FEATURE_BETA_DASHBOARD = "FEATURE_BETA_DASHBOARD"
    MAINTENANCE_MODE = "MAINTENANCE_MODE"

    # Limites
    MAX_UPLOAD_SIZE = "MAX_UPLOAD_SIZE"
    ITEMS_PER_PAGE = "ITEMS_PER_PAGE"

# Utilisation
from myapp.constants import ParameterSlugs
from django_app_parameter import app_parameter

title = getattr(app_parameter, ParameterSlugs.SITE_TITLE)
```

## Nommage

### Conventions de nommage

**Pour les noms (name)** :
- Utilisez des noms descriptifs en anglais
- Capitalisez chaque mot : "Blog Title", "Max Upload Size"
- Soyez concis mais clair

**Pour les slugs** (auto-générés) :
- Tout en majuscules : `BLOG_TITLE`
- Underscores pour séparer : `MAX_UPLOAD_SIZE`
- Pas d'espaces ni caractères spéciaux

**Exemples de bons noms** :
```python
✅ "Site Title"              → SITE_TITLE
✅ "Max Upload Size"         → MAX_UPLOAD_SIZE
✅ "Email From Address"      → EMAIL_FROM_ADDRESS
✅ "Enable Beta Features"    → ENABLE_BETA_FEATURES

❌ "title"                   → Pas assez descriptif
❌ "maximum_upload_size"     → Pas de capitalisation
❌ "email-from"              → Format inconsistant
```

### Descriptions complètes

Documentez chaque paramètre avec une description détaillée :

```python
Parameter.objects.create(
    name="Max Upload Size",
    value="10485760",
    value_type=Parameter.TYPES.INT,
    description="""
    Taille maximale des fichiers uploadés en octets.

    Valeur actuelle: 10485760 (10 Mo)
    Valeurs recommandées:
    - 5242880 (5 Mo) : Pour des images
    - 10485760 (10 Mo) : Pour des documents
    - 52428800 (50 Mo) : Pour des vidéos

    Note: Cette valeur doit être inférieure à
    DJANGO_MAX_UPLOAD_SIZE dans settings.py
    """.strip()
)
```

## Documentation

### Documenter les paramètres requis

Maintenez une liste des paramètres obligatoires :

```python
# docs/required_parameters.md

## Paramètres requis

Liste des paramètres qui DOIVENT exister pour le bon fonctionnement de l'application.

### Site

| Slug | Type | Description | Exemple |
|------|------|-------------|---------|
| SITE_TITLE | STR | Titre du site | "Mon Application" |
| CONTACT_EMAIL | STR | Email de contact | "contact@example.com" |

### Limites

| Slug | Type | Description | Exemple |
|------|------|-------------|---------|
| MAX_UPLOAD_SIZE | INT | Taille max upload (octets) | 10485760 |
| ITEMS_PER_PAGE | INT | Items par page | 20 |

### Features

| Slug | Type | Description | Exemple |
|------|------|-------------|---------|
| MAINTENANCE_MODE | BOO | Mode maintenance | false |
```

### Valider au démarrage

Vérifiez que les paramètres requis existent :

```python
# myapp/apps.py
from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured

class MyAppConfig(AppConfig):
    name = 'myapp'

    def ready(self):
        """Vérifie les paramètres requis au démarrage."""
        self.check_required_parameters()

    def check_required_parameters(self):
        """Vérifie que tous les paramètres requis existent."""
        from django_app_parameter import app_parameter

        required = [
            ('SITE_TITLE', str),
            ('CONTACT_EMAIL', str),
            ('MAX_UPLOAD_SIZE', int),
            ('ITEMS_PER_PAGE', int),
            ('MAINTENANCE_MODE', bool),
        ]

        missing = []
        invalid_type = []

        for slug, expected_type in required:
            try:
                value = getattr(app_parameter, slug)
                if not isinstance(value, expected_type):
                    invalid_type.append(
                        f"{slug} (attendu: {expected_type.__name__}, "
                        f"reçu: {type(value).__name__})"
                    )
            except ImproperlyConfigured:
                missing.append(slug)

        errors = []
        if missing:
            errors.append(f"Paramètres manquants: {', '.join(missing)}")
        if invalid_type:
            errors.append(f"Paramètres de type invalide: {', '.join(invalid_type)}")

        if errors:
            raise ImproperlyConfigured(
                "Erreur de configuration des paramètres:\n" + "\n".join(errors)
            )
```

## Déploiement

### Script de déploiement

Créez un script standardisé :

```bash
#!/bin/bash
# deploy.sh
set -e  # Arrêter en cas d'erreur

echo "=== Déploiement de l'application ==="

# 1. Migrations
echo "➜ Application des migrations..."
python manage.py migrate

# 2. Paramètres requis (ne pas écraser)
echo "➜ Chargement des paramètres requis..."
python manage.py load_param --no-update --file config/parameters/base.json

# 3. Paramètres par environnement
ENVIRONMENT=${ENVIRONMENT:-production}
echo "➜ Chargement des paramètres pour: $ENVIRONMENT"

if [ -f "config/parameters/${ENVIRONMENT}.json" ]; then
    python manage.py load_param --file "config/parameters/${ENVIRONMENT}.json"
else
    echo "⚠ Aucun fichier de paramètres pour $ENVIRONMENT"
fi

# 4. Collecte des fichiers statiques
echo "➜ Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# 5. Vérification
echo "➜ Vérification de la configuration..."
python manage.py check

echo "✓ Déploiement terminé avec succès"
```

### Paramètres par environnement

**config/parameters/development.json** :
```json
[
    {
        "name": "Debug Mode",
        "value": "true",
        "value_type": "BOO"
    },
    {
        "name": "API Endpoint",
        "value": "http://localhost:8000/api"
    }
]
```

**config/parameters/production.json** :
```json
[
    {
        "name": "Debug Mode",
        "value": "false",
        "value_type": "BOO"
    },
    {
        "name": "API Endpoint",
        "value": "https://api.production.com"
    }
]
```

### Sauvegarde des paramètres

Exportez régulièrement :

```bash
# Sauvegarder tous les paramètres
python manage.py dumpdata django_app_parameter.Parameter \
    --indent 2 \
    --output backups/parameters_$(date +%Y%m%d).json

# Restaurer si nécessaire
python manage.py loaddata backups/parameters_20240101.json
```

## Maintenance

### Nettoyer les paramètres obsolètes

Identifiez et supprimez les paramètres inutilisés :

```python
# scripts/check_unused_parameters.py
from django_app_parameter.models import Parameter
import os
import re

def find_parameter_usage(slug):
    """Recherche l'utilisation d'un paramètre dans le code."""
    pattern = re.compile(rf'\b{slug}\b')
    found_in = []

    for root, dirs, files in os.walk('.'):
        # Ignorer certains dossiers
        dirs[:] = [d for d in dirs if d not in ['.git', 'venv', '__pycache__']]

        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                        if pattern.search(content):
                            found_in.append(filepath)
                except Exception:
                    pass

    return found_in

# Vérifier chaque paramètre
for param in Parameter.objects.all():
    usage = find_parameter_usage(param.slug)
    if not usage:
        print(f"⚠ Paramètre potentiellement inutilisé: {param.slug}")
    else:
        print(f"✓ {param.slug} utilisé dans {len(usage)} fichier(s)")
```

### Versioning des paramètres

Suivez l'évolution avec Git :

```bash
# Exporter régulièrement
python manage.py dumpdata django_app_parameter.Parameter \
    --indent 2 > config/current_parameters.json

# Commiter
git add config/current_parameters.json
git commit -m "Update parameters snapshot"
```

### Migration de paramètres

Pour renommer ou restructurer :

```python
# management/commands/migrate_parameters.py
from django.core.management.base import BaseCommand
from django_app_parameter.models import Parameter

class Command(BaseCommand):
    help = 'Migre les anciens paramètres vers la nouvelle structure'

    def handle(self, *args, **options):
        # Renommer un paramètre
        try:
            param = Parameter.objects.get(slug="OLD_NAME")
            param.name = "New Name"  # Changera le slug
            param.save()
            self.stdout.write(
                self.style.SUCCESS(f'Renamed: OLD_NAME → {param.slug}')
            )
        except Parameter.DoesNotExist:
            pass

        # Fusionner des paramètres
        # Diviser un paramètre JSON en plusieurs
        # etc.
```

## Anti-patterns à éviter

### ❌ Stocker du code dans les paramètres

```python
# ❌ MAUVAIS
Parameter.objects.create(
    name="Custom Function",
    value="lambda x: x * 2",  # NE FAITES PAS ÇA
    value_type="STR"
)
```

### ❌ Paramètres trop volumineux

```python
# ❌ MAUVAIS : JSON de 5000 caractères
# Limite : 250 caractères

# ✅ BON : Utilisez un fichier séparé ou une table dédiée
```

### ❌ Logique métier dans les paramètres

```python
# ❌ MAUVAIS
if app_parameter.COMPLEX_BUSINESS_RULE == "type_a_and_user_premium":
    # Logique complexe...

# ✅ BON : Logique dans le code, paramètres pour les données
user_is_premium = check_premium_status(user)
feature_enabled = app_parameter.ENABLE_FEATURE
if user_is_premium and feature_enabled:
    # Logique...
```

### ❌ Dépendances entre paramètres

```python
# ❌ MAUVAIS : Paramètres interdépendants
# FEATURE_A dépend de FEATURE_B qui dépend de FEATURE_C

# ✅ BON : Paramètres indépendants ou logique dans le code
```

## Checklist de bonnes pratiques

### Sécurité
- [ ] Aucune donnée sensible dans les paramètres
- [ ] Permissions admin restreintes
- [ ] Audit logging configuré
- [ ] Validation des valeurs critiques

### Performance
- [ ] Cache implémenté pour paramètres fréquents
- [ ] Nombre de paramètres globaux limité (< 10)
- [ ] Prefetch pour accès multiples
- [ ] Invalidation de cache après modifications

### Organisation
- [ ] Paramètres groupés par catégorie
- [ ] Préfixes cohérents pour les slugs
- [ ] Fichiers JSON par environnement
- [ ] Documentation des paramètres requis

### Déploiement
- [ ] Script de déploiement standardisé
- [ ] Chargement avec `--no-update` pour les requis
- [ ] Sauvegarde régulière des paramètres
- [ ] Vérification au démarrage de l'application

### Maintenance
- [ ] Versioning dans Git
- [ ] Nettoyage des paramètres obsolètes
- [ ] Tests de régression
- [ ] Documentation à jour

## Ressources

- [Documentation Django](https://docs.djangoproject.com/)
- [Django security best practices](https://docs.djangoproject.com/en/stable/topics/security/)
- [Django caching](https://docs.djangoproject.com/en/stable/topics/cache/)

## Prochaines étapes

- [FAQ - Questions fréquentes](faq.md)
- [Architecture technique](architecture.md)
- [Guide des tests](testing.md)
