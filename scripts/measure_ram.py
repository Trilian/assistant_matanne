"""
Mesure la consommation RAM de l'application FastAPI.
Simule le chargement complet comme en production sur Railway.
"""
import os
import sys
from pathlib import Path

# Ajouter la racine du projet au PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import psutil

def get_mem_mb():
    """Retourne la RSS en MB du process courant."""
    return psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

def main():
    print("=" * 60)
    print("MESURE RAM — Simulation Railway Free (limite 0.5 GB = 512 MB)")
    print("=" * 60)
    
    baseline = get_mem_mb()
    print(f"\n1. Python baseline:              {baseline:.1f} MB")
    
    # Charger la config
    try:
        from src.core.config import obtenir_parametres
        obtenir_parametres()
        after_config = get_mem_mb()
        print(f"2. + Config (Pydantic Settings):  {after_config:.1f} MB (+{after_config - baseline:.1f})")
    except Exception as e:
        after_config = get_mem_mb()
        print(f"2. Config ERREUR ({e}):           {after_config:.1f} MB")
    
    # Charger les modèles SQLAlchemy
    try:
        from src.core.models import Base
        after_models = get_mem_mb()
        print(f"3. + Modèles SQLAlchemy (22):     {after_models:.1f} MB (+{after_models - after_config:.1f})")
    except Exception as e:
        after_models = get_mem_mb()
        print(f"3. Modèles ERREUR ({e}):          {after_models:.1f} MB")
    
    # Charger l'app FastAPI complète (routes, middlewares, services imports)
    try:
        from src.api.main import app
        after_app = get_mem_mb()
        print(f"4. + App FastAPI complète:        {after_app:.1f} MB (+{after_app - after_models:.1f})")
    except Exception as e:
        after_app = get_mem_mb()
        print(f"4. App ERREUR ({e}):              {after_app:.1f} MB")
    
    # Charger les services (registre)
    try:
        from src.services.core.registry import ServiceRegistry
        # Juste l'import, pas l'instanciation
        after_services_import = get_mem_mb()
        print(f"5. + Import services/registry:    {after_services_import:.1f} MB (+{after_services_import - after_app:.1f})")
    except Exception as e:
        after_services_import = get_mem_mb()
        print(f"5. Services ERREUR ({e}):         {after_services_import:.1f} MB")
    
    # Charger le cache
    try:
        from src.core.caching import obtenir_cache
        cache = obtenir_cache()
        after_cache = get_mem_mb()
        print(f"6. + Cache multi-niveaux:         {after_cache:.1f} MB (+{after_cache - after_services_import:.1f})")
    except Exception as e:
        after_cache = get_mem_mb()
        print(f"6. Cache ERREUR ({e}):            {after_cache:.1f} MB")
    
    # Charger le client IA
    try:
        from src.core.ai import ClientIA
        after_ia_import = get_mem_mb()
        print(f"7. + Import ClientIA:             {after_ia_import:.1f} MB (+{after_ia_import - after_cache:.1f})")
    except Exception as e:
        after_ia_import = get_mem_mb()
        print(f"7. ClientIA ERREUR ({e}):         {after_ia_import:.1f} MB")
    
    # Charger APScheduler
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler()
        after_scheduler = get_mem_mb()
        print(f"8. + APScheduler:                 {after_scheduler:.1f} MB (+{after_scheduler - after_ia_import:.1f})")
    except Exception as e:
        after_scheduler = get_mem_mb()
        print(f"8. APScheduler ERREUR ({e}):      {after_scheduler:.1f} MB")
    
    total = get_mem_mb()
    print(f"\n{'=' * 60}")
    print(f"TOTAL RAM au démarrage:          {total:.1f} MB")
    print(f"Marge Railway Free (512 MB):     {512 - total:.1f} MB restants")
    print(f"{'=' * 60}")
    
    if total > 450:
        print("⚠️  ATTENTION: Proche de la limite 512 MB !")
        print("   Les optimisations mémoire (section 17.3) sont CRITIQUES.")
    elif total > 350:
        print("⚡ OK mais serré. Les optimisations mémoire sont recommandées.")
    else:
        print("✅ CONFORTABLE. Marge suffisante pour le cache L1 + runtime.")

if __name__ == "__main__":
    main()
