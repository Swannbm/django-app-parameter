# Django App Parameter - Documentation

Documentation complète pour l'extension Django **django-app-parameter**.

## Pour les utilisateurs

Si vous souhaitez **utiliser** Django App Parameter dans votre projet :

1. [Vue d'ensemble](overview.md) - Introduction et concepts de base
2. [Installation](installation.md) - Guide d'installation et configuration
3. [Guide d'utilisation](usage-guide.md) - Exemples d'utilisation pratiques
4. [Référence API](api-reference.md) - Documentation complète de l'API
5. [Commande de gestion](management-commands.md) - Commande `load_param`
6. [FAQ](faq.md) - Questions fréquentes

## Pour les développeurs

Si vous souhaitez **contribuer** au développement :

7. [Tests](testing.md) - Guide des tests et couverture
8. [Architecture technique](architecture.md) - Structure interne et design
9. [Bonnes pratiques](best-practices.md) - Recommandations et patterns
10. [Guide de publication](publishing.md) - Publier une nouvelle version sur PyPI

Voir aussi [CONTRIBUTING.md](../CONTRIBUTING.md) pour le workflow de contribution.

## À propos

Django App Parameter est une extension légère pour Django qui permet de stocker et gérer des paramètres d'application configurables en base de données. Ces paramètres peuvent être modifiés via l'interface d'administration Django sans nécessiter de redéploiement ou de redémarrage du serveur.

**Version actuelle:** 1.1.3
**Licence:** CC0 1.0 Universal (Domaine public)
**Support Python:** 3.7+
**Repository:** [github.com/Swannbm/django-app-parameter](https://github.com/Swannbm/django-app-parameter)
**Couverture de tests:** 100%

## Démarrage rapide

```bash
# Installation
pip install django-app-parameter

# Configuration dans settings.py
INSTALLED_APPS += ['django_app_parameter']

# Migration de la base de données
python manage.py migrate

# Utilisation dans le code
from django_app_parameter import app_parameter

titre = app_parameter.BLOG_TITLE
```

Consultez le [guide d'installation](installation.md) pour des instructions détaillées.
