#!/usr/bin/env bash
# Script de déploiement - Module Famille
# Execute ce script pour configurer le module Famille

set -e

echo "============================================================"
echo "🏠 DÉPLOIEMENT MODULE FAMILLE"
echo "============================================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 Étape 1: Vérification des dépendances...${NC}"
python3 -c "from src.modules.famille import jules, sante, activites, shopping; print('✅ Imports OK')" || exit 1
echo ""

echo -e "${BLUE}📋 Étape 2: Génération de la migration SQL...${NC}"
python3 scripts/migration_famille.py
echo ""

echo -e "${BLUE}🧪 Étape 3: Lancement des tests...${NC}"
python3 -m pytest tests/test_famille.py -v --tb=short || echo "⚠️  Tests en erreur (non-bloquant)"
echo ""

echo -e "${YELLOW}⚠️  ÉTAPES MANUELLES À FAIRE:${NC}"
echo ""
echo "1️⃣  Supabase Migration:"
echo "   • Ouvrir: https://supabase.com/dashboard"
echo "   • Aller dans SQL Editor"
echo "   • Copier le contenu de: sql/001_add_famille_models.sql"
echo "   • Exécuter le script"
echo ""
echo "2️⃣  Vérification:"
echo "   • Vérifier que les 6 tables sont créées"
echo "   • Vérifier que les indices sont créés"
echo "   • Vérifier que les contraintes sont en place"
echo ""
echo "3️⃣  Test de l'app:"
echo "   • Lancer: streamlit run src/app.py"
echo "   • Aller dans: 👨‍👩‍👧‍👦 Famille → 🏠 Hub Famille"
echo "   • Tester chaque section"
echo ""

echo "============================================================"
echo "✅ DÉPLOIEMENT TERMINÉ!"
echo "============================================================"
echo ""
echo "📚 Documentation:"
echo "   • OVERVIEW_FAMILLE.md - Vue d'ensemble du module"
echo "   • sql/001_add_famille_models.sql - Migration SQL"
echo "   • tests/test_famille.py - Tests unitaires"
echo ""
