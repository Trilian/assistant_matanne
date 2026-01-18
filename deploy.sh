#!/bin/bash
# 🚀 Script de déploiement: Appliquer migrations + Restart Streamlit
# Usage: ./deploy.sh

set -e  # Exit on error

echo "🚀 Déploiement Inventaire Module - 3 Features"
echo "============================================="
echo ""

# 1. Vérifier dépendances
echo "✓ Vérification dépendances..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 required"
    exit 1
fi

if ! command -v alembic &> /dev/null; then
    echo "⚠️  Alembic non trouvé, essai avec python -m alembic..."
fi

# 2. Backup database local
echo ""
echo "✓ Backup database..."
if [ -f "instance/inventaire.db" ]; then
    cp instance/inventaire.db instance/inventaire.db.backup.$(date +%s)
    echo "  → Backup créé: instance/inventaire.db.backup.*"
else
    echo "  → Pas de DB local (Supabase mode)"
fi

# 3. Appliquer migrations
echo ""
echo "✓ Appliquer migrations Alembic..."
python3 -m alembic upgrade head
if [ $? -eq 0 ]; then
    echo "  ✅ Migrations appliquées"
else
    echo "  ❌ Erreur migrations. Checking SQL..."
    echo "  Si vous utilisez Supabase, lancez MIGRATIONS_SUPABASE.sql manuellement"
    echo "  dans: https://app.supabase.com/project/[project]/sql/new"
fi

# 4. Installer dépendances (si besoin)
echo ""
echo "✓ Vérifier dépendances Python..."
python3 -m pip install -q streamlit pydantic sqlalchemy 2>/dev/null || true

# 5. Redémarrer Streamlit
echo ""
echo "✓ Lancer Streamlit..."
echo ""
echo "============================================="
echo "🎉 Application lancée!"
echo "    http://localhost:8501"
echo ""
echo "📱 Navigate to:"
echo "    Cuisine → Inventaire"
echo ""
echo "📜 Tester les 3 features:"
echo "    1. 📜 Historique (onglet)"
echo "    2. 📸 Photos (onglet)"
echo "    3. 🔔 Notifications (onglet)"
echo "============================================="
echo ""

# Lance Streamlit
streamlit run src/app.py
