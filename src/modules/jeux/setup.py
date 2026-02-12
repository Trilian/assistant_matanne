"""
Script de mise en place du module Jeux (premier démarrage)

Usage:
    python src/domains/jeux/setup.py
"""

import sys
from pathlib import Path

# Ajouter au path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_module():
    """Met en place le module Jeux"""
    
    print("\n" + "🎲 "*40)
    print("SETUP MODULE JEUX")
    print("🎲 "*40 + "\n")
    
    # Step 1: Vérifier l'API
    print("1️⃣  Vérification de la configuration API...")
    try:
        from src.core.config import obtenir_parametres
        config = obtenir_parametres()
        
        api_key = config.get("FOOTBALL_DATA_API_KEY")
        if api_key:
            print(f"✅ Clé Football-Data trouvée: {api_key[:10]}...")
        else:
            print("⚠️  Clé Football-Data non trouvée")
            print("   → Ajouter dans .env.local: FOOTBALL_DATA_API_KEY=votre_token")
            print("   → Obtenir: https://www.football-data.org/client/register")
    except Exception as e:
        logger.error(f"Erreur config: {e}")
    
    # Step 2: Créer les tables BD
    print("\n2️⃣  Vérification base de données...")
    try:
        from src.core.database import obtenir_contexte_db
        from src.core.models import (
            Equipe, Match, PariSportif,
            TirageLoto, GrilleLoto, StatistiquesLoto, HistoriqueJeux
        )
        
        with obtenir_contexte_db() as session:
            # Vérifier si au moins une table existe
            try:
                count = session.query(Equipe).count()
                print(f"✅ Tables trouvées ({count} équipes en BD)")
            except Exception:
                print("⚠️  Tables non créées")
                print("   → Exécuter: python manage.py migrate")
                print("   → Ou: Exécuter sql/013_add_jeux_tables_manual.sql dans Supabase")
    
    except Exception as e:
        logger.error(f"Erreur BD: {e}")
    
    # Step 3: Charger les données initiales
    print("\n3️⃣  Initialisation des données...")
    try:
        from src.core.database import obtenir_contexte_db
        from src.core.models import Equipe, TirageLoto
        
        with obtenir_contexte_db() as session:
            # Insérer quelques équipes populaires si vide
            count = session.query(Equipe).count()
            
            if count == 0:
                print("   → Insertion des équipes Ligue 1...")
                
                equipes_data = [
                    ("Paris Saint-Germain", "Ligue 1", 38, 26, 5, 7, 92, 42, 83),
                    ("Olympique Lyonnais", "Ligue 1", 38, 21, 8, 9, 68, 38, 71),
                    ("Olympique Marseille", "Ligue 1", 38, 19, 10, 9, 58, 45, 67),
                    ("Stade Rennais", "Ligue 1", 38, 18, 7, 13, 56, 48, 61),
                    ("FC Nantes", "Ligue 1", 38, 16, 10, 12, 52, 46, 58),
                ]
                
                for nom, champ, mj, v, n, d, bm, be, pts in equipes_data:
                    equipe = Equipe(
                        nom=nom,
                        championnat=champ,
                        matchs_joues=mj,
                        victoires=v,
                        nuls=n,
                        defaites=d,
                        buts_marques=bm,
                        buts_encaisses=be,
                        points=pts
                    )
                    session.add(equipe)
                
                session.commit()
                print("✅ Équipes Ligue 1 insérées")
            else:
                print(f"✅ {count} équipes déjà en BD")
    
    except Exception as e:
        logger.error(f"Erreur insertion équipes: {e}")
    
    # Step 4: Tester l'API
    print("\n4️⃣  Test de connexion API Football-Data...")
    try:
        from src.domains.jeux.logic.api_football import charger_matchs_a_venir
        
        matchs = charger_matchs_a_venir("Ligue 1", jours=7)
        if matchs:
            print(f"✅ {len(matchs)} matchs chargés depuis l'API!")
        else:
            print("⚠️  Aucun match (clé API manquante ou pas de matchs)")
    except Exception as e:
        logger.error(f"Erreur API: {e}")
    
    # Step 5: Tester le scraper Loto
    print("\n5️⃣  Test Scraper FDJ Loto...")
    try:
        from src.domains.jeux.logic.scraper_loto import charger_tirages_loto
        
        tirages = charger_tirages_loto(limite=10)
        if tirages:
            print(f"✅ {len(tirages)} tirages Loto chargés!")
        else:
            print("⚠️  Aucun tirage (scraper temporairement indisponible)")
    except Exception as e:
        logger.warning(f"⚠️  Scraper Loto: {e}")
    
    # Résumé
    print("\n" + "="*70)
    print("✅ SETUP TERMINÉ")
    print("="*70)
    print("""
📌 Prochaines étapes:

1. Accéder à l'app:
   $ streamlit run src/app.py

2. Naviguer vers: 🎲 Jeux (sidebar)
   → ⚽ Paris Sportifs
   → 🎰 Loto

3. Configuration (si besoin):
   - Ajouter clé API Football-Data si manquante
   - Vérifier les tables BD sont créées

4. Documentation:
   → Lire: src/domains/jeux/README.md
   → Config APIs: APIS_CONFIGURATION.md

Bonne chance! 🍀
    """)


if __name__ == "__main__":
    try:
        setup_module()
    except Exception as e:
        print(f"❌ Erreur setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

