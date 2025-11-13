.PHONY: help check clean

help:  ## Afficher cette aide
	@echo "Commandes disponibles :"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

check:  ## Vérifier tout avant commit (ruff + pyright + tests)
	@echo "🔍 Vérification avec Ruff..."
	poetry run ruff check django_app_parameter/
	poetry run ruff format --check django_app_parameter/
	@echo "✅ Ruff OK\n"
	@echo "🔍 Vérification des types avec Pyright..."
	poetry run pyright django_app_parameter/
	@echo "✅ Pyright OK\n"
	@echo "🔍 Lancement des tests..."
	poetry run pytest --cov=django_app_parameter --cov-fail-under=100
	@echo "✅ Tests OK\n"
	@echo "✅ Toutes les vérifications sont passées !"

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
