# Installation et configuration

## Prérequis

- **Python** : 3.7 ou supérieur
- **Django** : 3.2 ou supérieur
- **Base de données** : PostgreSQL, MySQL, SQLite (toute BDD supportée par Django)

## Installation

### Via pip

```bash
pip install django-app-parameter
```

### Via Poetry

```bash
poetry add django-app-parameter
```

### Depuis les sources

```bash
git clone https://github.com/Swannbm/django-app-parameter.git
cd django-app-parameter
pip install -e .
```

## Configuration de base

### 1. Ajouter à INSTALLED_APPS

Éditez votre fichier `settings.py` :

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Vos applications
    'myapp',

    # Django App Parameter
    'django_app_parameter',
]
```

**Important** : Placez `django_app_parameter` après les applications Django de base pour garantir que l'admin soit disponible.

### 2. Appliquer les migrations

Créez les tables nécessaires dans votre base de données :

```bash
python manage.py migrate django_app_parameter
```

Cette commande crée la table `django_app_parameter_parameter` avec tous les champs nécessaires.

### 3. Créer un superutilisateur (si nécessaire)

Si vous n'avez pas encore de compte admin :

```bash
python manage.py createsuperuser
```

### 4. Vérification

Démarrez le serveur de développement :

```bash
python manage.py runserver
```

Accédez à l'interface admin : `http://127.0.0.1:8000/admin/`

Vous devriez voir une section "Django App Parameter" avec "Parameters".

## Configuration avancée (optionnelle)

### Activer les paramètres globaux dans les templates

Si vous souhaitez accéder aux paramètres directement dans vos templates Django, ajoutez le context processor :

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # Ajouter ce context processor
                'django_app_parameter.context_processors.add_global_parameter_context',
            ],
        },
    },
]
```

**Note** : Seuls les paramètres avec `is_global=True` seront disponibles dans les templates.

### Configuration du champ auto (Django 3.2+)

Django App Parameter utilise automatiquement `BigAutoField` pour les clés primaires. C'est configuré dans le fichier `apps.py` de l'extension :

```python
class DjangoAppParameterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_app_parameter"
```

Aucune configuration supplémentaire n'est nécessaire.

## Création de vos premiers paramètres

### Via l'interface admin

1. Accédez à `http://127.0.0.1:8000/admin/django_app_parameter/parameter/`
2. Cliquez sur "Ajouter Parameter"
3. Remplissez le formulaire :
   - **Nom** : "Blog Title" (nom lisible)
   - **Type de donnée** : "STR - Chaîne de caractères"
   - **Valeur** : "Mon Super Blog"
   - **Description** : "Titre principal du blog" (optionnel)
   - **Is global** : Cochez si vous voulez l'utiliser dans les templates
4. Cliquez sur "Enregistrer"

Le **slug** sera généré automatiquement : `BLOG_TITLE`

### Via le shell Django

```bash
python manage.py shell
```

```python
from django_app_parameter.models import Parameter

# Créer un paramètre simple
Parameter.objects.create(
    name="Site Title",
    value="Mon Application Django",
    value_type=Parameter.TYPES.STR,
    description="Titre du site affiché dans le header"
)

# Créer un paramètre numérique
Parameter.objects.create(
    name="Max Upload Size",
    value="5242880",  # 5 Mo en octets
    value_type=Parameter.TYPES.INT,
    description="Taille maximale des fichiers uploadés"
)

# Créer un paramètre booléen global
Parameter.objects.create(
    name="Maintenance Mode",
    value="false",
    value_type=Parameter.TYPES.BOO,
    is_global=True,
    description="Active le mode maintenance"
)
```

### Via la commande load_param

Créez un fichier `initial_parameters.json` :

```json
[
    {
        "name": "Blog Title",
        "value": "Mon Super Blog",
        "value_type": "STR",
        "is_global": true,
        "description": "Titre principal du blog"
    },
    {
        "name": "Max Upload Size",
        "value": "5242880",
        "value_type": "INT",
        "description": "Taille max upload en octets"
    },
    {
        "name": "Tax Rate",
        "value": "20.00",
        "value_type": "DCL",
        "description": "Taux de TVA en pourcentage"
    },
    {
        "name": "Maintenance Mode",
        "value": "false",
        "value_type": "BOO",
        "is_global": true,
        "description": "Active le mode maintenance"
    }
]
```

Chargez les paramètres :

```bash
python manage.py load_param --file initial_parameters.json
```

## Vérification de l'installation

### Test dans le shell

```bash
python manage.py shell
```

```python
from django_app_parameter import app_parameter

# Accéder au paramètre créé
print(app_parameter.BLOG_TITLE)  # Affiche: Mon Super Blog

# Vérifier le type
print(type(app_parameter.MAX_UPLOAD_SIZE))  # Affiche: <class 'int'>
```

Si cela fonctionne, votre installation est réussie !

### Test dans une vue

Créez une vue de test dans `myapp/views.py` :

```python
from django.http import HttpResponse
from django_app_parameter import app_parameter

def test_parameters(request):
    try:
        title = app_parameter.BLOG_TITLE
        return HttpResponse(f"Paramètre récupéré : {title}")
    except Exception as e:
        return HttpResponse(f"Erreur : {e}", status=500)
```

Ajoutez l'URL dans `myapp/urls.py` :

```python
from django.urls import path
from . import views

urlpatterns = [
    path('test-params/', views.test_parameters, name='test_parameters'),
]
```

Accédez à `http://127.0.0.1:8000/test-params/`

## Configuration pour la production

### 1. Migrations

Assurez-vous que les migrations sont appliquées lors du déploiement :

```bash
python manage.py migrate django_app_parameter
```

### 2. Chargement des paramètres requis

Créez un script de déploiement qui charge les paramètres obligatoires :

```bash
#!/bin/bash
# deploy.sh

# Appliquer les migrations
python manage.py migrate

# Charger les paramètres requis sans écraser les existants
python manage.py load_param --no-update --file config/required_parameters.json

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Démarrer l'application
gunicorn myproject.wsgi
```

### 3. Sécurité

**Important** : Ne stockez JAMAIS de données sensibles dans les paramètres :
- ❌ Mots de passe
- ❌ Clés API privées
- ❌ Tokens d'authentification
- ❌ Secrets de session

Utilisez plutôt :
- Variables d'environnement
- Services de gestion de secrets (AWS Secrets Manager, HashiCorp Vault)
- Django settings chiffrées

### 4. Caching (recommandé)

Pour les paramètres fréquemment utilisés, implémentez un cache :

```python
# myapp/utils.py
from django.core.cache import cache
from django_app_parameter import app_parameter

def get_cached_parameter(slug, timeout=3600):
    """
    Récupère un paramètre avec cache.

    Args:
        slug: Slug du paramètre
        timeout: Durée du cache en secondes (défaut: 1 heure)
    """
    cache_key = f"app_param_{slug}"
    value = cache.get(cache_key)

    if value is None:
        value = getattr(app_parameter, slug)
        cache.set(cache_key, value, timeout)

    return value
```

Utilisation :

```python
from myapp.utils import get_cached_parameter

# Première fois : requête BDD + mise en cache
title = get_cached_parameter("BLOG_TITLE")

# Fois suivantes (pendant 1h) : récupération depuis le cache
title = get_cached_parameter("BLOG_TITLE")
```

### 5. Permissions admin

Limitez l'accès aux paramètres aux administrateurs de confiance via les permissions Django :

```python
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django_app_parameter.models import Parameter

# Créer un groupe "Parameter Managers"
group, created = Group.objects.get_or_create(name="Parameter Managers")

# Ajouter les permissions
content_type = ContentType.objects.get_for_model(Parameter)
permissions = Permission.objects.filter(content_type=content_type)
group.permissions.set(permissions)

# Ajouter des utilisateurs au groupe
user.groups.add(group)
```

## Désinstallation

Si vous devez désinstaller l'extension :

1. **Sauvegarder les données** (optionnel) :
```bash
python manage.py dumpdata django_app_parameter > parameters_backup.json
```

2. **Supprimer les tables** :
```bash
python manage.py migrate django_app_parameter zero
```

3. **Retirer de INSTALLED_APPS** :
Supprimez `'django_app_parameter'` de votre `settings.py`

4. **Désinstaller le package** :
```bash
pip uninstall django-app-parameter
```

## Dépannage

### Erreur : "No module named 'django_app_parameter'"

**Solution** : Vérifiez que le package est installé :
```bash
pip list | grep django-app-parameter
```

Réinstallez si nécessaire :
```bash
pip install django-app-parameter
```

### Erreur : "Table 'django_app_parameter_parameter' doesn't exist"

**Solution** : Appliquez les migrations :
```bash
python manage.py migrate django_app_parameter
```

### Erreur : "ImproperlyConfigured: Parameter with slug 'XXX' does not exist"

**Solution** : Le paramètre n'existe pas en base. Créez-le via l'admin ou le shell.

### Les paramètres ne sont pas disponibles dans les templates

**Solution** : Vérifiez que :
1. Le context processor est configuré dans `settings.py`
2. Le paramètre a `is_global=True`
3. Vous utilisez `{{ SLUG }}` (pas `{{ app_parameter.SLUG }}`)

### Performance : trop de requêtes BDD

**Solution** : Implémentez un système de cache (voir section Production ci-dessus)

## Prochaines étapes

- [Guide d'utilisation avec exemples pratiques](usage-guide.md)
- [Référence complète de l'API](api-reference.md)
- [Commande de gestion load_param](management-commands.md)
