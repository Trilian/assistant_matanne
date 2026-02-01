"""
Script de test des APIs pour le module Jeux

Usage:
    python tests/test_jeux_apis.py
"""

import sys
from pathlib import Path

# Ajouter le projet au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_football_api():
    """Test Football-Data API"""
    print("\n" + "="*60)
    print("🏆 TEST FOOTBALL-DATA.ORG API")
    print("="*60)
    
    try:
        from src.domains.jeux.logic.api_football import (
            charger_matchs_a_venir,
            charger_classement,
            chercher_equipe
        )
        
        print("\n1️⃣  Chargement des matchs Ligue 1 (7 jours)...")
        matchs = charger_matchs_a_venir("Ligue 1", jours=7)
        
        if matchs:
            print(f"✅ {len(matchs)} matchs trouvés!")
            for i, m in enumerate(matchs[:3], 1):
                print(f"   {i}. {m['equipe_domicile']} vs {m['equipe_exterieur']} ({m['date']})")
        else:
            print("⚠️  Aucun match trouvé (clé API non configurée ou pas de matchs)")
        
        print("\n2️⃣  Chargement du classement Ligue 1...")
        classement = charger_classement("Ligue 1")
        
        if classement:
            print(f"✅ {len(classement)} équipes chargées!")
            for i, e in enumerate(classement[:5], 1):
                print(f"   {i}. {e['nom']} ({e['points']} pts)")
        else:
            print("⚠️  Aucune donnée (API indisponible)")
        
        print("\n3️⃣  Recherche d'équipe (PSG)...")
        psg = chercher_equipe("Paris")
        if psg:
            print(f"✅ Trouvé: {psg['nom']} ({psg['pays']})")
        else:
            print("⚠️  Équipe non trouvée")
        
        return True
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_loto_scraper():
    """Test Scraper FDJ Loto"""
    print("\n" + "="*60)
    print("🎰 TEST SCRAPER FDJ LOTO")
    print("="*60)
    
    try:
        from src.domains.jeux.logic.scraper_loto import (
            charger_tirages_loto,
            obtenir_statistiques_loto
        )
        
        print("\n1️⃣  Chargement des 20 derniers tirages...")
        tirages = charger_tirages_loto(limite=20)
        
        if tirages:
            print(f"✅ {len(tirages)} tirages chargés!")
            for i, t in enumerate(tirages[:3], 1):
                print(f"   {i}. {t['date']}: {t['numeros']} + {t['numero_chance']}")
        else:
            print("⚠️  Aucun tirage trouvé")
        
        print("\n2️⃣  Calcul des statistiques...")
        stats = obtenir_statistiques_loto(limite=50)
        
        if stats:
            print(f"✅ Stats calculées sur {stats.get('nombre_tirages', '?')} tirages")
            numeros_chauds = stats.get('numeros_chauds', [])
            if numeros_chauds:
                print(f"   Numéros chauds: {numeros_chauds[:5]}")
        else:
            print("⚠️  Stats indisponibles")
        
        return True
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_helpers():
    """Test des helpers UI"""
    print("\n" + "="*60)
    print("🖥️  TEST HELPERS UI")
    print("="*60)
    
    try:
        from src.domains.jeux.logic.ui_helpers import (
            charger_matchs_avec_fallback,
            charger_classement_avec_fallback,
            charger_tirages_loto_avec_fallback
        )
        
        print("\n1️⃣  Helper matchs avec fallback...")
        matchs, source = charger_matchs_avec_fallback("Ligue 1", jours=7)
        print(f"✅ {len(matchs)} matchs depuis {source}")
        
        print("\n2️⃣  Helper classement avec fallback...")
        classement, source = charger_classement_avec_fallback("Ligue 1")
        print(f"✅ {len(classement)} équipes depuis {source}")
        
        print("\n3️⃣  Helper tirages Loto avec fallback...")
        tirages, source = charger_tirages_loto_avec_fallback(limite=20)
        print(f"✅ {len(tirages)} tirages depuis {source}")
        
        return True
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Exécute tous les tests"""
    print("\n" + "🎲 "*30)
    print("TESTS INTÉGRATION API - MODULE JEUX")
    print("🎲 "*30)
    
    resultats = {
        "Football-Data API": test_football_api(),
        "FDJ Loto Scraper": test_loto_scraper(),
        "UI Helpers": test_ui_helpers(),
    }
    
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    
    for test_name, result in resultats.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = sum(resultats.values())
    print(f"\n{total}/{len(resultats)} tests réussis")
    
    return all(resultats.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
