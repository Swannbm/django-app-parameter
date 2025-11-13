.PHONY: help install test test-cov test-all lint format clean build publish

help:  ## Afficher cette aide
	@echo "Commandes disponibles :"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Installer les dépendances de développement
	poetry install

test:  ## Lancer les tests
	poetry run pytest

test-cov:  ## Lancer les tests avec couverture
	poetry run pytest --cov=django_app_parameter --cov-report=term-missing --cov-report=html

test-all:  ## Lancer les tests avec toutes les versions (tox)
	tox

lint:  ## Vérifier le code (flake8)
	poetry run flake8 django_app_parameter/

format:  ## Formater le code (black)
	poetry run black django_app_parameter/

format-check:  ## Vérifier le formatage sans modifier
	poetry run black --check django_app_parameter/

clean:  ## Nettoyer les fichiers temporaires
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".tox" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true

build:  ## Construire le package
	poetry build

publish:  ## Publier sur PyPI (nécessite configuration)
	poetry publish

check:  ## Vérifier tout avant commit (format, lint, tests)
	@echo "🔍 Vérification du formatage..."
	poetry run black --check django_app_parameter/
	@echo "✅ Formatage OK\n"
	@echo "🔍 Vérification du linting..."
	poetry run flake8 django_app_parameter/
	@echo "✅ Linting OK\n"
	@echo "🔍 Lancement des tests..."
	poetry run pytest --cov=django_app_parameter --cov-fail-under=100
	@echo "✅ Tests OK\n"
	@echo "✅ Toutes les vérifications sont passées !"

dev:  ## Lancer un environnement de développement interactif
	poetry shell
