#!/bin/bash
# Script de vérification du fix SQLAlchemy Session

echo "════════════════════════════════════════════════════════════"
echo "  ✅ VÉRIFICATION DU FIX SQLAlchemy Session"
echo "════════════════════════════════════════════════════════════"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Vérifier la syntaxe
echo -e "${YELLOW}[1/4]${NC} Vérification de la syntaxe Python..."
python -m py_compile src/domains/cuisine/ui/planning.py 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Syntaxe OK${NC}"
else
    echo -e "${RED}❌ Erreur syntaxe${NC}"
    exit 1
fi

# 2. Vérifier les imports
echo ""
echo -e "${YELLOW}[2/4]${NC} Vérification des imports..."
python -c "
from src.services.planning import get_planning_service
from src.domains.cuisine.ui.planning import render_planning
print('✅ Imports OK')
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Imports OK${NC}"
else
    echo -e "${RED}❌ Erreur imports${NC}"
    exit 1
fi

# 3. Vérifier les modifications
echo ""
echo -e "${YELLOW}[3/4]${NC} Vérification des modifications..."

# Chercher la signature du fix
if grep -q "joinedload(Planning.repas)" src/services/planning.py; then
    echo -e "${GREEN}✅ joinedload() trouvé dans planning.py${NC}"
else
    echo -e "${RED}❌ joinedload() NOT FOUND${NC}"
    exit 1
fi

if grep -q "with obtenir_contexte_db()" src/domains/cuisine/ui/planning.py; then
    echo -e "${GREEN}✅ Context manager trouvé dans planning UI${NC}"
else
    echo -e "${RED}❌ Context manager NOT FOUND${NC}"
    exit 1
fi

# 4. Statistiques
echo ""
echo -e "${YELLOW}[4/4]${NC} Statistiques..."
JOINEDLOAD_COUNT=$(grep -c "joinedload" src/services/planning.py)
CONTEXT_COUNT=$(grep -c "with obtenir_contexte_db()" src/domains/cuisine/ui/planning.py)

echo -e "  joinedload() usage: ${GREEN}$JOINEDLOAD_COUNT${NC}"
echo -e "  context manager usage: ${GREEN}$CONTEXT_COUNT${NC}"

echo ""
echo "════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ TOUS LES TESTS PASSÉS!${NC}"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📖 Prochaines étapes:"
echo "  1. streamlit run src/app.py"
echo "  2. Naviguer vers 'Cuisine > Planning > Planning Actif'"
echo "  3. Vérifier qu'aucune erreur 'not bound to a Session' n'apparaît"
echo "  4. Tester les modifications (recettes, préparé, notes, dupliquer)"
echo ""
