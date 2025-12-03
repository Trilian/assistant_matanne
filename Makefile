.PHONY: help install run test coverage lint format clean docker-build docker-run docker-db init-db seed backup

# Variables
PYTHON := poetry run python
STREAMLIT := poetry run streamlit
PYTEST := poetry run pytest
BLACK := poetry run black
RUFF := poetry run ruff
MYPY := poetry run mypy

# Couleurs pour l'affichage
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ Aide

help: ## Affiche cette aide
	@echo "$(GREEN)Assistant MaTanne v2 - Commandes disponibles$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(GREEN)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Installation

install: ## Installation complète (Poetry + dépendances + pre-commit)
	@echo "$(GREEN)📦 Installation des dépendances...$(NC)"
	poetry install
	poetry run pre-commit install
	@echo "$(GREEN)✅ Installation terminée$(NC)"

install-ollama: ## Installe Ollama (Linux/Mac uniquement)
	@echo "$(GREEN)🤖 Installation d'Ollama...$(NC)"
	curl -fsSL https://ollama.com/install.sh | sh
	ollama pull llama2
	@echo "$(GREEN)✅ Ollama installé$(NC)"

##@ Développement

run: ## Lance l'application Streamlit
	@echo "$(GREEN)🚀 Démarrage de l'application...$(NC)"
	$(STREAMLIT) run src/app.py

dev: ## Lance en mode développement (avec reload)
	@echo "$(GREEN)🔧 Mode développement...$(NC)"
	$(STREAMLIT) run src/app.py --server.runOnSave true

##@ Base de données

docker-db: ## Démarre PostgreSQL avec Docker
	@echo "$(GREEN)🐘 Démarrage PostgreSQL...$(NC)"
	docker compose up -d postgres
	@echo "$(YELLOW)⏳ Attente de 10 secondes...$(NC)"
	@sleep 10 || timeout /t 10
	@echo "$(GREEN)✅ PostgreSQL prêt$(NC)"

docker-db-stop: ## Arrête PostgreSQL
	@echo "$(RED)🛑 Arrêt PostgreSQL...$(NC)"
	docker compose down

init-db: ## Initialise la base de données (migrations)
	@echo "$(GREEN)🗄️  Initialisation de la base...$(NC)"
	$(PYTHON) -m alembic upgrade head
	@echo "$(GREEN)✅ Base initialisée$(NC)"

seed: ## Remplit la base avec des données de démo
	@echo "$(GREEN)🌱 Chargement des données de démo...$(NC)"
	$(PYTHON) scripts/seed_data.py
	@echo "$(GREEN)✅ Données chargées$(NC)"

reset-db: ## Réinitialise complètement la base
	@echo "$(RED)⚠️  Réinitialisation de la base...$(NC)"
	$(PYTHON) -m alembic downgrade base
	$(PYTHON) -m alembic upgrade head
	@echo "$(GREEN)✅ Base réinitialisée$(NC)"

backup: ## Sauvegarde la base de données
	@echo "$(GREEN)💾 Sauvegarde de la base...$(NC)"
	$(PYTHON) scripts/backup.py
	@echo "$(GREEN)✅ Sauvegarde terminée$(NC)"

##@ Tests

test: ## Lance tous les tests
	@echo "$(GREEN)🧪 Lancement des tests...$(NC)"
	$(PYTEST)

test-watch: ## Tests en mode watch (relance automatique)
	@echo "$(GREEN)👀 Tests en mode watch...$(NC)"
	$(PYTEST) -f

test-cuisine: ## Tests du module Cuisine
	@echo "$(GREEN)🍲 Tests Cuisine...$(NC)"
	$(PYTEST) tests/test_modules/test_cuisine.py -v

test-famille: ## Tests du module Famille
	@echo "$(GREEN)👶 Tests Famille...$(NC)"
	$(PYTEST) tests/test_modules/test_famille.py -v

test-maison: ## Tests du module Maison
	@echo "$(GREEN)🏡 Tests Maison...$(NC)"
	$(PYTEST) tests/test_modules/test_maison.py -v

test-agent: ## Tests de l'agent IA
	@echo "$(GREEN)🤖 Tests Agent IA...$(NC)"
	$(PYTEST) tests/test_core/test_ai_agent.py -v

test-integration: ## Tests d'intégration
	@echo "$(GREEN)🔗 Tests d'intégration...$(NC)"
	$(PYTEST) tests/test_integration/ -v

coverage: ## Tests avec rapport de couverture
	@echo "$(GREEN)📊 Tests avec couverture...$(NC)"
	$(PYTEST) --cov=src --cov-report=html --cov-report=term
	@echo "$(YELLOW)📂 Rapport disponible dans htmlcov/index.html$(NC)"

##@ Qualité du code

lint: ## Vérification du code (ruff + mypy)
	@echo "$(GREEN)🔍 Vérification du code...$(NC)"
	$(RUFF) check src tests
	$(MYPY) src

format: ## Formatage automatique du code
	@echo "$(GREEN)✨ Formatage du code...$(NC)"
	$(BLACK) src tests
	$(RUFF) check --fix src tests

format-check: ## Vérifie le formatage sans modifier
	@echo "$(GREEN)🔎 Vérification du formatage...$(NC)"
	$(BLACK) --check src tests
	$(RUFF) check src tests

##@ Docker

docker-build: ## Build l'image Docker
	@echo "$(GREEN)🐳 Build de l'image Docker...$(NC)"
	docker compose build

docker-run: ## Lance l'application avec Docker
	@echo "$(GREEN)🚀 Démarrage avec Docker...$(NC)"
	docker compose up

docker-run-detached: ## Lance en arrière-plan
	@echo "$(GREEN)🚀 Démarrage en arrière-plan...$(NC)"
	docker compose up -d

docker-stop: ## Arrête tous les containers
	@echo "$(RED)🛑 Arrêt des containers...$(NC)"
	docker compose down

docker-logs: ## Affiche les logs
	@echo "$(GREEN)📋 Logs...$(NC)"
	docker compose logs -f

docker-clean: ## Nettoie les containers et volumes
	@echo "$(RED)🧹 Nettoyage Docker...$(NC)"
	docker compose down -v
	docker system prune -f

##@ Déploiement

deploy-streamlit: ## Prépare pour Streamlit Cloud
	@echo "$(GREEN)☁️  Préparation déploiement Streamlit Cloud...$(NC)"
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	@echo "$(GREEN)✅ requirements.txt généré$(NC)"
	@echo "$(YELLOW)📝 N'oublie pas de configurer les secrets sur Streamlit Cloud$(NC)"

check-deploy: ## Vérifie que tout est prêt pour le déploiement
	@echo "$(GREEN)✅ Vérification pré-déploiement...$(NC)"
	@echo "$(YELLOW)1. Tests...$(NC)"
	$(PYTEST) --maxfail=1
	@echo "$(YELLOW)2. Lint...$(NC)"
	$(RUFF) check src
	@echo "$(YELLOW)3. Format...$(NC)"
	$(BLACK) --check src
	@echo "$(GREEN)✅ Prêt pour le déploiement$(NC)"

##@ Services

ollama-serve: ## Démarre Ollama (doit être installé)
	@echo "$(GREEN)🤖 Démarrage Ollama...$(NC)"
	ollama serve

ollama-pull: ## Télécharge le modèle IA
	@echo "$(GREEN)📥 Téléchargement du modèle llama2...$(NC)"
	ollama pull llama2

##@ Nettoyage

clean: ## Nettoie les fichiers temporaires
	@echo "$(RED)🧹 Nettoyage...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov .coverage
	@echo "$(GREEN)✅ Nettoyage terminé$(NC)"

clean-all: clean docker-clean ## Nettoyage complet (fichiers + Docker)
	@echo "$(GREEN)✅ Nettoyage complet terminé$(NC)"

##@ Utilitaires

shell: ## Ouvre un shell Python avec l'environnement
	@echo "$(GREEN)🐍 Shell Python...$(NC)"
	$(PYTHON)

db-shell: ## Ouvre psql sur la base de données
	@echo "$(GREEN)🐘 Shell PostgreSQL...$(NC)"
	docker-compose exec postgres psql -U matanne -d matanne

logs-db: ## Affiche les logs PostgreSQL
	@echo "$(GREEN)📋 Logs PostgreSQL...$(NC)"
	docker-compose logs -f postgres

version: ## Affiche les versions des outils
	@echo "$(GREEN)📌 Versions :$(NC)"
	@echo "Python: $$(poetry run python --version)"
	@echo "Poetry: $$(poetry --version)"
	@echo "Streamlit: $$($(STREAMLIT) --version)"
	@echo "PostgreSQL: $$(docker-compose exec postgres psql --version 2>/dev/null || echo 'Non démarré')"

##@ Développement avancé

pre-commit: ## Lance pre-commit sur tous les fichiers
	@echo "$(GREEN)🔧 Pre-commit...$(NC)"
	poetry run pre-commit run --all-files

update-deps: ## Met à jour les dépendances
	@echo "$(GREEN)📦 Mise à jour des dépendances...$(NC)"
	poetry update

security-check: ## Vérifie les failles de sécurité
	@echo "$(GREEN)🔒 Vérification sécurité...$(NC)"
	poetry run pip-audit

##@ Documentation

docs: ## Génère la documentation
	@echo "$(GREEN)📚 Génération documentation...$(NC)"
	@echo "$(YELLOW)TODO: Configurer Sphinx ou MkDocs$(NC)"

serve-docs: ## Serve la documentation localement
	@echo "$(GREEN)📖 Documentation locale...$(NC)"
	@echo "$(YELLOW)TODO: Configurer Sphinx ou MkDocs$(NC)"