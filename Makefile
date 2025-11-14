# ==========================
# Assistant MaTanne — Makefile
# ==========================

PYTHON := python
PIP := pip

# Dossiers principaux
SRC_DIR := assistant_matanne
DATA_DIR := data
DB_FILE := $(DATA_DIR)/app.db

# ==========================
# 🧱 Installation & Environnement
# ==========================

install:
	$(PIP) install --upgrade pip
	$(PIP) install -e .[dev]

format:
	black $(SRC_DIR)
	isort $(SRC_DIR)

check-format:
	black --check $(SRC_DIR)
	isort --check-only $(SRC_DIR)

lint:
	flake8 $(SRC_DIR)

# ==========================
# 🧠 Base de données
# ==========================

init_db:
	$(PYTHON) -m scripts.init_db

reset_db:
	rm -f $(DB_FILE)
	make init_db

seed_db:
	$(PYTHON) -m scripts.seed_data

backup_db:
	$(PYTHON) -m scripts.backup_db

export_courses:
	$(PYTHON) -m scripts.export_courses

import_recettes:
	$(PYTHON) -m scripts.import_recettes_pdf

# ==========================
# 🚀 Lancement application
# ==========================

run:
	streamlit run app.py

# ==========================
# 🧪 Tests
# ==========================

test:
	pytest -v --maxfail=1 --disable-warnings -q

# ==========================
# 🧹 Maintenance
# ==========================

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache

reset:
	make clean
	make reset_db

# ==========================
# 📦 Utilitaires
# ==========================

help:
	@echo "Commandes disponibles :"
	@echo "  make install        → Installe les dépendances et le projet"
	@echo "  make run            → Lance l’application Streamlit"
	@echo "  make init_db        → Initialise la base SQLite"
	@echo "  make reset_db       → Réinitialise la base de données"
	@echo "  make seed_db        → Ajoute des données de démonstration"
	@echo "  make backup_db      → Sauvegarde la base localement"
	@echo "  make export_courses → Export liste courses"
	@echo "  make import_recettes→ Import recettes depuis PDF"
	@echo "  make format         → Formate le code (Black + isort)"
	@echo "  make lint           → Vérifie la qualité du code"
	@echo "  make test           → Lance les tests"
	@echo "  make clean          → Nettoie les fichiers temporaires"
