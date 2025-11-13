# Vue d'ensemble

## Qu'est-ce que Django App Parameter ?

Django App Parameter est une extension Django qui permet de stocker des paramètres d'application configurables dans la base de données. Ces paramètres peuvent être modifiés dynamiquement via l'interface d'administration Django, sans nécessiter de modifications du code ou de redémarrage du serveur.

## Problème résolu

Dans une application Django typique, les configurations sont souvent définies dans :
- **`settings.py`** : Configuration statique nécessitant un redéploiement pour toute modification
- **Variables d'environnement** : Configuration par environnement, difficile à modifier en production
- **Base de données personnalisée** : Nécessite de développer une solution sur mesure

Django App Parameter offre une solution clé en main pour les **paramètres modifiables à l'exécution** par les administrateurs.

## Caractéristiques principales

### 1. Stockage en base de données
Tous les paramètres sont stockés dans une table dédiée, accessibles via l'ORM Django standard.

### 2. Interface d'administration
Gestion complète des paramètres via l'admin Django :
- Création, modification, suppression
- Recherche et filtrage
- Interface utilisateur familière

### 3. Typage des valeurs
Support de 6 types de données avec conversion automatique :
- **INT** : Nombres entiers
- **STR** : Chaînes de caractères (par défaut)
- **FLT** : Nombres à virgule flottante (float)
- **DCL** : Nombres décimaux (Decimal, pour précision)
- **JSN** : Structures JSON (dictionnaires, listes)
- **BOO** : Booléens (true/false)

### 4. Accès simple et intuitif
Trois patterns d'accès disponibles :

**Pattern proxy (recommandé) :**
```python
from django_app_parameter import app_parameter
titre = app_parameter.BLOG_TITLE  # Conversion automatique selon le type
```

**Pattern manager (explicite) :**
```python
from django_app_parameter.models import Parameter
titre = Parameter.objects.str("BLOG_TITLE")
annee = Parameter.objects.int("YEAR")
```

**Pattern template (paramètres globaux) :**
```html
<title>{{ BLOG_TITLE }}</title>
```

### 5. Génération automatique de slugs
Les noms de paramètres sont automatiquement convertis en slugs uniques :
- `"blog title"` → `"BLOG_TITLE"`
- `"sender e-mail"` → `"SENDER_E_MAIL"`
- Majuscules, underscores, caractères ASCII uniquement

### 6. Chargement en masse
Commande de gestion pour charger plusieurs paramètres depuis JSON :
```bash
python manage.py load_param --file parameters.json
```

### 7. Aucune dépendance externe
Package minimaliste ne nécessitant que Django (3.2+).

### 8. Tests complets
Couverture de tests à 100% avec pytest.

## Cas d'usage typiques

### Configuration d'application
```python
app_parameter.API_ENDPOINT  # URL d'API externe
app_parameter.MAX_UPLOAD_SIZE  # Taille max des uploads
app_parameter.ITEMS_PER_PAGE  # Pagination
```

### Branding et contenu
```python
app_parameter.SITE_TITLE  # Titre du site
app_parameter.FOOTER_TEXT  # Texte du footer
app_parameter.CONTACT_EMAIL  # Email de contact
```

### Feature flags
```python
if app_parameter.MAINTENANCE_MODE:
    return HttpResponse("Site en maintenance")

if app_parameter.ENABLE_BETA_FEATURE:
    # Activer la fonctionnalité
```

### Règles métier
```python
tax_rate = app_parameter.TAX_RATE  # Taux de TVA
shipping_cost = app_parameter.SHIPPING_COST  # Frais de port
discount = app_parameter.PROMO_DISCOUNT  # Réduction promotionnelle
```

### Configuration email
```python
EMAIL_FROM = app_parameter.EMAIL_FROM_ADDRESS
EMAIL_REPLY_TO = app_parameter.EMAIL_REPLY_TO
```

## Architecture de base

```
┌─────────────────┐
│  Django Admin   │  ← Interface de gestion
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Parameter Model │  ← Stockage en BDD
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Manager / Proxy │  ← API d'accès
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Votre code     │  ← Utilisation
└─────────────────┘
```

## Modèle de données

Chaque paramètre est composé de :

| Champ | Type | Description |
|-------|------|-------------|
| `name` | CharField(100) | Nom lisible du paramètre |
| `slug` | SlugField(40) | Identifiant unique (auto-généré) |
| `value_type` | CharField(3) | Type de données (INT/STR/FLT/DCL/JSN/BOO) |
| `value` | CharField(250) | Valeur stockée (chaîne de caractères) |
| `description` | TextField | Description optionnelle |
| `is_global` | BooleanField | Disponible dans les templates si True |

## Workflow typique

1. **Création via l'admin** : Administrateur crée un paramètre avec un nom et une valeur
2. **Slug automatique** : Le système génère un slug unique (ex: "BLOG_TITLE")
3. **Stockage en BDD** : Valeur stockée comme chaîne de caractères
4. **Accès dans le code** : `app_parameter.BLOG_TITLE`
5. **Conversion de type** : Valeur automatiquement convertie selon `value_type`
6. **Utilisation** : Valeur typée utilisée dans la logique applicative

## Comparaison avec les alternatives

### vs. Django Settings

| Django Settings | App Parameter |
|----------------|---------------|
| Statique | Dynamique |
| Nécessite redéploiement | Modifiable à chaud |
| Type-safe avec IDE | Type-safe à l'exécution |
| Fichier Python | Interface admin |
| Gestion par environnement | Gestion par base de données |

**Recommandation** : Utilisez settings.py pour la configuration structurelle (DATABASES, MIDDLEWARE), app_parameter pour la configuration métier modifiable.

### vs. Variables d'environnement

| Env Variables | App Parameter |
|--------------|---------------|
| Par environnement | Par base de données |
| Configuration au déploiement | Configuration à l'exécution |
| Secrets et credentials | Paramètres applicatifs |
| Pas d'interface | Interface admin |

**Recommandation** : Utilisez les variables d'environnement pour les secrets (API keys, passwords), app_parameter pour les paramètres métier.

### vs. django-constance

| django-constance | app_parameter |
|-----------------|---------------|
| Plus de features (Redis, validation) | Plus simple et léger |
| Config globale | Paramètres illimités |
| Backend configurable | SQLite/PostgreSQL/MySQL |
| Plus mature | Plus récent |

**Recommandation** : django-constance pour des besoins avancés, app_parameter pour la simplicité.

## Limites connues

1. **Limite de 250 caractères** par valeur (considérez un stockage externe pour les grandes données JSON)
2. **Pas de validation de valeur** au niveau du modèle (validation à faire dans votre code)
3. **Requête BDD par accès** (pensez au caching pour les paramètres fréquemment utilisés)
4. **Pas de chiffrement** (ne stockez PAS de mots de passe ou clés API sensibles)
5. **Templates : toujours des chaînes** (les paramètres globaux sont convertis en str dans les templates)

## Philosophie de conception

Django App Parameter suit la philosophie Django :

- **Convention plutôt que configuration** : Fonctionne sans configuration supplémentaire
- **Batteries incluses** : Tout ce dont vous avez besoin est inclus
- **Simplicité** : API minimaliste et intuitive
- **Don't Repeat Yourself** : Réutilise les patterns Django existants
- **Explicit is better than implicit** : Types de données clairement définis

## Prochaines étapes

- [Installation et configuration](installation.md)
- [Guide d'utilisation avec exemples](usage-guide.md)
- [Référence complète de l'API](api-reference.md)
