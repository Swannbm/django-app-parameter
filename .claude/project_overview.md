# Django-App-Parameter - Vue d'ensemble du projet

## 🎯 Objectif du projet

Application Django qui stocke les paramètres d'application en base de données, permettant aux administrateurs de modifier les valeurs de configuration à la volée via l'interface Django admin, sans modifications de code, redéploiement ou redémarrage de service.

## 📊 Informations clés

- **Version actuelle**: 2.0.0
- **Licence**: CC0 1.0 Universal (Domaine Public)
- **Python**: 3.10+ (versions non-EOL uniquement)
- **Django**: 4.2 LTS et 5.2 LTS uniquement
- **Dépendances runtime**: Django uniquement (zéro dépendance externe)
- **Couverture de tests**: 100% (requis)

## 🏗️ Architecture

### Structure des répertoires

```
django-app-parameter/
├── django_app_parameter/       # Package principal de l'application
│   ├── models.py              # Modèles Parameter et ParameterValidator
│   ├── admin.py               # Configuration de l'admin Django
│   ├── utils.py               # Registre de validateurs et utilitaires
│   ├── context_processors.py # Processeur de contexte pour templates
│   └── management/commands/   # Commandes de management
│       ├── load_param.py      # Import de paramètres depuis JSON
│       └── dump_param.py      # Export de paramètres vers JSON
│
├── tests/                     # Suite de tests (100% de couverture)
│   ├── settings.py           # Configuration Django pour tests
│   ├── test_django_app_parameter.py  # Tests du modèle (2,063 lignes)
│   ├── test_admin.py                 # Tests de l'admin (787 lignes)
│   ├── test_admin_views.py           # Tests des vues admin (562 lignes)
│   ├── test_dump_param.py            # Tests commande export (363 lignes)
│   ├── test_utils.py                 # Tests utilitaires (308 lignes)
│   └── test_validators.py            # Tests validateurs (75 lignes)
│
├── demo_project/              # Projet Django de démo
│   ├── fixtures/             # Données d'exemple
│   ├── templates/            # Templates de démo
│   ├── setup_demo.sh         # Script de configuration
│   └── run_demo.sh          # Script de lancement
│
└── docs/                     # Documentation externe
    ├── overview.md
    ├── usage-guide.md
    ├── management-commands.md
    ├── installation.md
    └── faq.md
```

### Modèles de données

#### Parameter
- `name`: Nom lisible du paramètre
- `slug`: Identifiant unique auto-généré (ex: "BLOG_TITLE")
- `value_type`: Type de données (15 types disponibles)
- `value`: Valeur stockée (toujours en string, max 250 chars)
- `description`: Description optionnelle
- `is_global`: Si True, disponible dans les templates

#### ParameterValidator (v2.0.0)
- `parameter`: ForeignKey vers Parameter
- `validator_type`: Nom/clé du validateur
- `validator_params`: Paramètres JSON pour l'instanciation du validateur

### 15 types de données supportés

**Types de base:**
- `INT`: Entiers
- `STR`: Chaînes (par défaut)
- `FLT`: Nombres flottants
- `DCL`: Décimaux (pour calculs précis comme l'argent)
- `BOO`: Booléens

**Types date/heure:**
- `DAT`: Date (YYYY-MM-DD, ISO 8601)
- `DTM`: DateTime (format ISO 8601)
- `TIM`: Time (HH:MM:SS)
- `DUR`: Duration (stocké en secondes, retourne timedelta)

**Types validés:**
- `URL`: URL avec validation
- `EML`: Email avec validation
- `PCT`: Pourcentage (0-100, validé)

**Types structurés:**
- `JSN`: Structure JSON quelconque
- `LST`: Liste séparée par virgules
- `DCT`: Dictionnaire JSON
- `PTH`: Chemin de fichier (retourne objet Path)

## 🔑 Patterns d'accès

### 1. Pattern Proxy (Recommandé)
```python
from django_app_parameter import app_parameter
title = app_parameter.BLOG_TITLE  # Auto-converti au bon type
```

### 2. Méthodes du Manager
```python
from django_app_parameter.models import Parameter
title = Parameter.objects.str("BLOG_TITLE")
year = Parameter.objects.int("BIRTH_YEAR")
```

### 3. Objet Parameter direct
```python
param = Parameter.objects.get(slug="BLOG_TITLE")
value = param.get()  # Auto-conversion selon value_type
```

### 4. Accès dans les templates (paramètres globaux uniquement)
```html
<title>{{ BLOG_TITLE }}</title>
```

## ⚙️ Système de validateurs (v2.0.0)

### Validateurs intégrés disponibles
- Valeur: MinValueValidator, MaxValueValidator
- Longueur: MinLengthValidator, MaxLengthValidator
- Pattern: RegexValidator, validate_slug
- Format: EmailValidator, URLValidator, validate_ipv4_address, validate_ipv6_address
- Fichier: FileExtensionValidator

### Validateurs personnalisés
Définis dans settings:
```python
DJANGO_APP_PARAMETER = {
    'validators': {
        'even_number': 'myapp.validators.validate_even_number',
    }
}
```

## 🧪 Stack de tests

- **pytest** avec pytest-django
- **pytest-cov** pour la couverture
- **4,158 lignes de tests** au total
- **Base de données SQLite en mémoire** pour les tests
- **100% de couverture** requis (imposé dans CI)

## 🛠️ Outils de développement

### Qualité de code
- **Ruff**: Linter et formateur (remplace Black + Flake8 + isort)
- **Pyright**: Vérification de types (mode strict)
- **Coverage**: Rapport de couverture de tests

### Tests multi-versions (Tox)
- Python: 3.10, 3.11, 3.12, 3.13
- Django: 4.2 LTS, 5.2 LTS
- Total: 8 combinaisons testées

### Commandes Makefile
```bash
make check    # Exécute ruff, pyright et tests
make format   # Formate le code avec ruff
make clean    # Supprime les fichiers temporaires
make help     # Affiche les commandes disponibles
```

## 🎨 Patterns de conception utilisés

1. **Proxy Pattern**: Classe `AccessParameter` pour accès façon Django settings
2. **Manager Pattern**: `ParameterManager` avec méthodes spécifiques au domaine
3. **Strategy Pattern**: Conversion de types via dictionnaire de dispatch
4. **Registry Pattern**: Registre de validateurs dans `utils.py`
5. **Factory Pattern**: `ParameterValidator.get_validator()` instancie les validateurs

## 📝 Conventions notables

- **Génération de slug**: Auto-généré depuis le nom, uppercase avec `_`
- **Gestion des types**: Aliasing pour éviter conflits (`_str = str`, etc.)
- **Type hints**: Couverture complète avec conformité Pyright stricte
- **Gestion d'erreurs**: `ImproperlyConfigured` pour paramètres manquants
- **Stockage**: Toutes les valeurs stockées en string, converties à la récupération

## 🔐 Limitations actuelles

1. **Limite de 250 caractères** sur les valeurs
2. **Pas de chiffrement** (prévu pour une version future)
3. **Requête DB par accès** (considérer le caching pour haute fréquence)
4. **Templates: strings uniquement** pour les paramètres globaux

## 🚀 Fonctionnalités v2.0.0 (2025.11.14)

- Méthodes setters pour mises à jour programmatiques
- Système de validateurs avec 10+ validateurs intégrés
- Support de validateurs personnalisés via settings
- 10 nouveaux types de paramètres
- Commande dump_param pour export
- Projet de démo pour tests manuels
- Type hints complets avec Pyright
- Interface admin améliorée
