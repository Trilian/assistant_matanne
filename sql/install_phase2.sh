#!/bin/bash
# Script pour exécuter la migration Phase 2 sur Supabase
# Usage: bash sql/install_phase2.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  PHASE 2: Installation tables modèles courses sur Supabase║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Vérifier que le fichier SQL existe
if [ ! -f "sql/006_add_modeles_courses.sql" ]; then
    echo "❌ Erreur: sql/006_add_modeles_courses.sql introuvable"
    echo "   Vérifier que vous êtes dans le dossier racine du projet"
    exit 1
fi

echo "📋 Instructions d'installation:"
echo ""
echo "1️⃣  Accédez à Supabase:"
echo "   → https://app.supabase.com"
echo ""
echo "2️⃣  Ouvrez l'onglet 'SQL Editor':"
echo "   → Cliquez sur 'New Query'"
echo ""
echo "3️⃣  Copiez le contenu du fichier:"
echo "   File: sql/006_add_modeles_courses.sql"
echo ""
echo "4️⃣  Collez dans l'éditeur SQL et cliquez 'RUN'"
echo ""
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "📄 Contenu du fichier SQL:"
echo ""
cat sql/006_add_modeles_courses.sql | head -30
echo ""
echo "... (voir fichier complet dans sql/006_add_modeles_courses.sql)"
echo ""
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "✅ Après exécution du SQL:"
echo "   - Tables 'modeles_courses' et 'articles_modeles' créées"
echo "   - 1 modèle de démo '🏠 Courses semaine' inséré"
echo "   - 4 articles de démo inclus"
echo ""
echo "🔍 Vérification:"
echo "   → Allez dans l'onglet 'Table Editor'"
echo "   → Vérifiez que 'modeles_courses' et 'articles_modeles' existent"
echo "   → Vérifiez que le modèle '🏠 Courses semaine' est présent"
echo ""
echo "💡 Pour les utilisateurs de terminal (psql):"
echo "   psql \"postgresql://user:password@host:5432/db\" < sql/006_add_modeles_courses.sql"
echo ""
