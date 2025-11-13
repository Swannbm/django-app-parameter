# Commande de gestion load_param

Documentation complète de la commande de gestion `load_param` pour le chargement en masse de paramètres.

## Vue d'ensemble

La commande `load_param` permet de charger ou mettre à jour plusieurs paramètres depuis un fichier JSON ou une chaîne JSON. C'est particulièrement utile pour :

- Initialiser les paramètres lors du déploiement
- Définir les paramètres requis pour l'application
- Migrer des paramètres entre environnements
- Sauvegarder et restaurer des configurations

## Syntaxe

```bash
python manage.py load_param [options]
```

## Options

### --file

Charge les paramètres depuis un fichier JSON.

**Syntaxe** :
```bash
python manage.py load_param --file <chemin/vers/fichier.json>
```

**Exemple** :
```bash
python manage.py load_param --file parameters.json
python manage.py load_param --file /opt/app/config/required_params.json
```

### --json

Charge les paramètres depuis une chaîne JSON.

**Syntaxe** :
```bash
python manage.py load_param --json '<json_string>'
```

**Exemples** :
```bash
# Un seul paramètre
python manage.py load_param --json '[{"name": "Test", "value": "hello"}]'

# Plusieurs paramètres
python manage.py load_param --json '[
    {"name": "Site Title", "value": "Mon Site"},
    {"name": "Max Size", "value": "5242880", "value_type": "INT"}
]'
```

**Note** : Utilisez des guillemets simples autour du JSON pour éviter les conflits avec les guillemets du JSON.

### --no-update

Empêche la mise à jour des paramètres existants.

**Syntaxe** :
```bash
python manage.py load_param --no-update --file parameters.json
```

**Comportement** :
- Crée les paramètres qui n'existent pas
- Ignore les paramètres déjà existants (ne les met PAS à jour)
- Utile pour définir des valeurs par défaut sans écraser les modifications

**Exemple de cas d'usage** :
```bash
# Créer les paramètres requis sans écraser les valeurs en production
python manage.py load_param --no-update --file required_defaults.json
```

## Format JSON

### Structure de base

Le fichier JSON doit contenir un tableau d'objets représentant les paramètres :

```json
[
    {
        "name": "Nom du paramètre",
        "value": "valeur",
        "value_type": "STR",
        "description": "Description optionnelle",
        "is_global": false,
        "slug": "SLUG_OPTIONNEL"
    }
]
```

### Champs disponibles

| Champ | Type | Requis | Défaut | Description |
|-------|------|--------|--------|-------------|
| `name` | string | **Oui** | - | Nom lisible du paramètre |
| `value` | string | Non | `""` | Valeur du paramètre |
| `value_type` | string | Non | `"STR"` | Type de données (INT/STR/FLT/DCL/JSN/BOO) |
| `description` | string | Non | `""` | Description du paramètre |
| `is_global` | boolean | Non | `false` | Disponibilité dans les templates |
| `slug` | string | Non | auto | Slug personnalisé (sinon généré depuis `name`) |

### Exemples de formats

#### Paramètre minimal

```json
[
    {
        "name": "Site Title"
    }
]
```

Crée un paramètre avec :
- slug : `"SITE_TITLE"` (auto-généré)
- value : `""`
- value_type : `"STR"`

#### Paramètre complet

```json
[
    {
        "name": "Max Upload Size",
        "value": "10485760",
        "value_type": "INT",
        "description": "Taille maximale des fichiers uploadés en octets (10 Mo)",
        "is_global": false
    }
]
```

#### Paramètre avec slug personnalisé

```json
[
    {
        "slug": "MY_CUSTOM_SLUG",
        "name": "My Parameter",
        "value": "custom value"
    }
]
```

Le slug ne sera pas auto-généré, `"MY_CUSTOM_SLUG"` sera utilisé directement.

#### Tous les types de données

```json
[
    {
        "name": "String Parameter",
        "value": "Hello World",
        "value_type": "STR"
    },
    {
        "name": "Integer Parameter",
        "value": "42",
        "value_type": "INT"
    },
    {
        "name": "Float Parameter",
        "value": "3.14159",
        "value_type": "FLT"
    },
    {
        "name": "Decimal Parameter",
        "value": "19.99",
        "value_type": "DCL"
    },
    {
        "name": "Boolean Parameter",
        "value": "true",
        "value_type": "BOO"
    },
    {
        "name": "JSON Parameter",
        "value": "{\"key\": \"value\", \"number\": 123}",
        "value_type": "JSN"
    }
]
```

**Note** : Pour les valeurs JSON, échappez les guillemets avec `\"`.

#### Paramètres globaux (templates)

```json
[
    {
        "name": "Site Title",
        "value": "Mon Super Site",
        "is_global": true
    },
    {
        "name": "Footer Text",
        "value": "© 2024 Mon Entreprise",
        "is_global": true
    },
    {
        "name": "Contact Email",
        "value": "contact@example.com",
        "is_global": true
    }
]
```

Ces paramètres seront accessibles directement dans les templates :
```html
<title>{{ SITE_TITLE }}</title>
<footer>{{ FOOTER_TEXT }}</footer>
```

## Exemples d'utilisation

### Exemple 1 : Initialisation d'application

Créez `initial_params.json` :

```json
[
    {
        "name": "Site Title",
        "value": "Mon Application",
        "is_global": true
    },
    {
        "name": "Items Per Page",
        "value": "20",
        "value_type": "INT"
    },
    {
        "name": "Maintenance Mode",
        "value": "false",
        "value_type": "BOO",
        "is_global": true
    }
]
```

Chargez les paramètres :

```bash
python manage.py load_param --file initial_params.json
```

### Exemple 2 : Paramètres requis (sans écrasement)

Créez `required_params.json` :

```json
[
    {
        "name": "Max Upload Size",
        "value": "5242880",
        "value_type": "INT",
        "description": "Taille max upload par défaut (5 Mo)"
    },
    {
        "name": "Session Timeout",
        "value": "3600",
        "value_type": "INT",
        "description": "Timeout de session en secondes (1 heure)"
    }
]
```

Chargez sans écraser :

```bash
python manage.py load_param --no-update --file required_params.json
```

**Résultat** :
- Si les paramètres n'existent pas → créés avec les valeurs par défaut
- Si les paramètres existent → conservés tels quels

### Exemple 3 : Configuration par environnement

Créez différents fichiers par environnement :

**development.json** :
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

**production.json** :
```json
[
    {
        "name": "Debug Mode",
        "value": "false",
        "value_type": "BOO"
    },
    {
        "name": "API Endpoint",
        "value": "https://api.example.com"
    }
]
```

Chargez selon l'environnement :

```bash
# Développement
python manage.py load_param --file config/development.json

# Production
python manage.py load_param --file config/production.json
```

### Exemple 4 : Chargement rapide via --json

Pour des tests ou configurations simples :

```bash
# Un paramètre
python manage.py load_param --json '[{"name": "Test Param", "value": "test"}]'

# Plusieurs paramètres
python manage.py load_param --json '[
    {"name": "Param 1", "value": "value1"},
    {"name": "Param 2", "value": "value2", "value_type": "INT"}
]'
```

### Exemple 5 : Script de déploiement

Créez `deploy.sh` :

```bash
#!/bin/bash
set -e

echo "=== Déploiement de l'application ==="

# 1. Migrations
echo "Application des migrations..."
python manage.py migrate

# 2. Paramètres requis (ne pas écraser)
echo "Chargement des paramètres requis..."
python manage.py load_param --no-update --file config/required_params.json

# 3. Paramètres par défaut (peut écraser)
echo "Chargement des paramètres par défaut..."
python manage.py load_param --file config/default_params.json

# 4. Fichiers statiques
echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# 5. Démarrage
echo "Démarrage de l'application..."
gunicorn myproject.wsgi
```

Exécutez :

```bash
chmod +x deploy.sh
./deploy.sh
```

### Exemple 6 : Configuration multi-environnement

Structure de fichiers :

```
config/
├── base.json          # Paramètres communs à tous les environnements
├── development.json   # Spécifique au développement
├── staging.json       # Spécifique au staging
└── production.json    # Spécifique à la production
```

**base.json** :
```json
[
    {
        "name": "Items Per Page",
        "value": "20",
        "value_type": "INT"
    },
    {
        "name": "Max Upload Size",
        "value": "5242880",
        "value_type": "INT"
    }
]
```

**production.json** :
```json
[
    {
        "name": "Debug Mode",
        "value": "false",
        "value_type": "BOO"
    },
    {
        "name": "Maintenance Mode",
        "value": "false",
        "value_type": "BOO"
    }
]
```

Script de chargement :

```bash
#!/bin/bash
# load_config.sh

ENVIRONMENT=${1:-production}

echo "Chargement de la configuration pour : $ENVIRONMENT"

# Paramètres de base (sans écrasement)
python manage.py load_param --no-update --file config/base.json

# Paramètres d'environnement (avec écrasement)
python manage.py load_param --file "config/${ENVIRONMENT}.json"

echo "Configuration chargée avec succès"
```

Utilisation :

```bash
./load_config.sh development
./load_config.sh production
```

## Utilisation programmatique

### Depuis un script Python

```python
from django.core.management import call_command

# Charger depuis un fichier
call_command('load_param', file='parameters.json')

# Charger depuis une chaîne JSON
json_string = '[{"name": "Test", "value": "hello"}]'
call_command('load_param', json=json_string)

# Avec l'option no-update
call_command('load_param', file='params.json', no_update=True)
```

### Dans une commande de management personnalisée

```python
# myapp/management/commands/setup.py
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Configure l\'application'

    def handle(self, *args, **options):
        self.stdout.write('Configuration de l\'application...')

        # Charger les paramètres
        call_command('load_param', file='config/required.json', no_update=True)

        self.stdout.write(self.style.SUCCESS('Configuration terminée'))
```

### Dans un signal Django

```python
# myapp/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.core.management import call_command

@receiver(post_migrate)
def load_default_parameters(sender, **kwargs):
    """Charge les paramètres par défaut après les migrations."""
    if sender.name == 'myapp':
        call_command('load_param', no_update=True, file='config/defaults.json')
```

## Comportement détaillé

### Logique de création/mise à jour

1. **Génération du slug** :
   - Si `slug` fourni dans le JSON → utilise ce slug
   - Sinon → génère depuis `name` via `parameter_slugify()`

2. **Vérification de l'existence** :
   - Recherche un paramètre avec ce slug
   - Si trouvé → paramètre existant
   - Sinon → nouveau paramètre

3. **Action selon le mode** :

   **Sans `--no-update` (défaut)** :
   - Nouveau paramètre → créé
   - Paramètre existant → **mis à jour** avec les nouvelles valeurs

   **Avec `--no-update`** :
   - Nouveau paramètre → créé
   - Paramètre existant → **ignoré** (valeurs actuelles conservées)

### Messages de retour

La commande affiche le résultat pour chaque paramètre :

```
Parameter "Site Title": Added
Parameter "Max Size": Already exists, updated
Parameter "Tax Rate": Already exists
```

**Messages possibles** :
- `"Added"` : Paramètre créé
- `"Already exists, updated"` : Paramètre mis à jour
- `"Already exists"` : Paramètre existant, pas de mise à jour (avec `--no-update`)

### Gestion des erreurs

**Fichier non trouvé** :
```bash
python manage.py load_param --file missing.json
# CommandError: File 'missing.json' not found
```

**JSON invalide** :
```bash
python manage.py load_param --json '{invalid json}'
# CommandError: Invalid JSON: ...
```

**Options mutuellement exclusives** :
```bash
python manage.py load_param --file params.json --json '[...]'
# CommandError: Use either --file or --json, not both
```

**Aucune option fournie** :
```bash
python manage.py load_param
# CommandError: You must provide either --file or --json
```

## Bonnes pratiques

### 1. Version les fichiers de configuration

Stockez vos fichiers JSON de paramètres dans le contrôle de version :

```
myproject/
├── config/
│   ├── required_params.json      # Paramètres obligatoires
│   ├── default_params.json       # Valeurs par défaut
│   ├── development.json          # Env développement
│   ├── staging.json              # Env staging
│   └── production.json           # Env production
├── manage.py
└── ...
```

### 2. Utilisez --no-update pour les paramètres requis

Garantit que les paramètres existent sans écraser les modifications en production :

```bash
python manage.py load_param --no-update --file config/required_params.json
```

### 3. Documentez vos paramètres

Utilisez le champ `description` pour documenter chaque paramètre :

```json
{
    "name": "Max Upload Size",
    "value": "10485760",
    "value_type": "INT",
    "description": "Taille maximale des fichiers uploadés en octets. 10485760 = 10 Mo. Modifiable via l'admin."
}
```

### 4. Séparez les paramètres sensibles

**Ne stockez JAMAIS de secrets dans les paramètres** :
- ❌ Mots de passe
- ❌ Clés API privées
- ❌ Tokens

Utilisez plutôt des variables d'environnement ou un gestionnaire de secrets.

### 5. Testez vos fichiers JSON

Validez vos fichiers avant de les déployer :

```bash
# Valider le JSON
python -m json.tool config/parameters.json

# Tester le chargement
python manage.py load_param --file config/parameters.json --no-update
```

### 6. Automatisez le chargement

Intégrez le chargement dans vos scripts de déploiement :

```bash
# Dans votre CI/CD
- python manage.py migrate
- python manage.py load_param --no-update --file config/required.json
- python manage.py collectstatic --noinput
```

### 7. Sauvegardez vos paramètres

Exportez vos paramètres avant des modifications importantes :

```bash
# Export (Django dumpdata)
python manage.py dumpdata django_app_parameter.Parameter --indent 2 > backup_params.json

# Restauration si nécessaire
python manage.py loaddata backup_params.json
```

## Dépannage

### Problème : "File not found"

**Cause** : Le chemin du fichier est incorrect.

**Solution** : Utilisez un chemin absolu ou relatif correct :

```bash
# Chemin relatif depuis la racine du projet
python manage.py load_param --file config/parameters.json

# Chemin absolu
python manage.py load_param --file /opt/app/config/parameters.json
```

### Problème : "Invalid JSON"

**Cause** : Le JSON n'est pas valide.

**Solution** : Validez votre JSON :

```bash
# Valider avec Python
python -m json.tool parameters.json

# Ou utilisez un validateur en ligne
```

Erreurs courantes :
- Virgule finale : `[{"name": "test"},]` ← Invalide
- Guillemets simples : `{'name': 'test'}` ← Invalide, utilisez `"`
- Guillemets non échappés : `{"value": "{"key": "val"}"}` ← Invalide

### Problème : Les paramètres ne sont pas mis à jour

**Cause** : Option `--no-update` active.

**Solution** : Supprimez `--no-update` pour permettre les mises à jour :

```bash
python manage.py load_param --file parameters.json
```

### Problème : Slug en conflit

**Cause** : Deux paramètres génèrent le même slug.

**Exemple** :
- "Test Param" → `TEST_PARAM`
- "test-param" → `TEST_PARAM` (conflit)

**Solution** : Utilisez des slugs personnalisés :

```json
[
    {
        "slug": "TEST_PARAM_1",
        "name": "Test Param",
        "value": "value1"
    },
    {
        "slug": "TEST_PARAM_2",
        "name": "test-param",
        "value": "value2"
    }
]
```

## Référence complète

### Signature de la commande

```python
class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            help="Path to JSON file containing parameters"
        )
        parser.add_argument(
            "--json",
            type=str,
            help="JSON string containing parameters"
        )
        parser.add_argument(
            "--no-update",
            action="store_true",
            help="Do not update existing parameters"
        )
```

### Codes de retour

- `0` : Succès
- `1` : Erreur (fichier non trouvé, JSON invalide, etc.)

### Logging

La commande utilise le système de logging Django :

**Niveau INFO** :
- Affiche le résultat pour chaque paramètre

**Niveau DEBUG** :
- Détails supplémentaires sur le traitement

Activez le logging dans `settings.py` :

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django_app_parameter': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

## Exemples de fichiers complets

### Fichier de base minimaliste

```json
[
    {
        "name": "Site Title",
        "value": "Mon Site",
        "is_global": true
    },
    {
        "name": "Contact Email",
        "value": "contact@example.com",
        "is_global": true
    }
]
```

### Fichier de configuration complète

```json
[
    {
        "name": "Site Title",
        "value": "Mon Application Django",
        "value_type": "STR",
        "description": "Titre principal du site affiché dans le header",
        "is_global": true
    },
    {
        "name": "Max Upload Size",
        "value": "10485760",
        "value_type": "INT",
        "description": "Taille maximale des fichiers uploadés en octets (10 Mo)",
        "is_global": false
    },
    {
        "name": "Items Per Page",
        "value": "25",
        "value_type": "INT",
        "description": "Nombre d'éléments par page dans les listes paginées"
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
        "description": "Active le mode maintenance sur tout le site",
        "is_global": true
    },
    {
        "name": "Email Config",
        "value": "{\"from\": \"noreply@example.com\", \"reply_to\": \"support@example.com\"}",
        "value_type": "JSN",
        "description": "Configuration des emails"
    }
]
```

## Prochaines étapes

- [Guide d'utilisation pratique](usage-guide.md)
- [Référence API complète](api-reference.md)
- [Bonnes pratiques](best-practices.md)
