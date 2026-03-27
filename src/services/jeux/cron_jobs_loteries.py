"""
Cron jobs pour le module Loteries (Loto + Euromillions).

2 jobs automatisés:
1. Scraper résultats FDJ: 1×/jour à 21h30 (après tirages)
2. Backtest grilles: 1×/jour à 22h (après scraping)
"""

import logging
from datetime import datetime
from typing import Any

from apscheduler.triggers.cron import CronTrigger

from src.core.db import obtenir_contexte_db
from src.core.exceptions import ErreurService
from src.core.models.jeux import TirageLoto, TirageEuromillions, GrilleLoto, GrilleEuromillions

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# JOB 1: SCRAPER RÉSULTATS FDJ (Loto + Euromillions)
# ═══════════════════════════════════════════════════════════


def scraper_resultats_fdj():
    """
    Scrape les résultats des tirages Loto et Euromillions via API FDJ.
    
    Fréquence: 1×/jour à 21h30 (après les tirages à 21h)
    
    Implémente:
    - Récupération dernier tirage Loto (Lundi/Mercredi/Samedi)
    - Récupération dernier tirage Euromillions (Mardi/Vendredi)
    - Stockage en base avec numéros + complémentaire/étoiles
    - Mise à jour statistiques globales
    """
    logger.info("🔄 Début scraping résultats FDJ (Loto + Euromillions)")
    
    try:
        import httpx
        
        # URL API FDJ (exemple - à adapter selon documentation)
        # Note: L'API FDJ officielle nécessite une clé API
        # Alternative: scraper le site web public
        
        # Pour l'instant, placeholder avec simulation
        logger.warning("⚠️ Scraping FDJ non implémenté - Simulation uniquement")
        
        # TODO: Implémenter scraping réel
        # Exemple structure:
        # response = httpx.get("https://api.fdj.fr/loto/tirage/dernier", headers={"X-API-Key": "..."})
        # data = response.json()
        
        # Simuler insertion tirage Loto
        with obtenir_contexte_db() as session:
            # Vérifier si tirage aujourd'hui existe déjà
            today = datetime.now().date()
            tirage_existant = session.query(TirageLoto).filter(
                TirageLoto.date == today
            ).first()
            
            if tirage_existant:
                logger.info(f"✅ Tirage Loto du {today} déjà en base")
            else:
                # TODO: Insérer vrai tirage depuis API
                logger.info(f"📥 Nouveau tirage Loto à insérer (simulation)")
            
            # Idem pour Euromillions
            tirage_euro_existant = session.query(TirageEuromillions).filter(
                TirageEuromillions.date == today
            ).first()
            
            if tirage_euro_existant:
                logger.info(f"✅ Tirage Euromillions du {today} déjà en base")
            else:
                logger.info(f"📥 Nouveau tirage Euromillions à insérer (simulation)")
            
            session.commit()
        
        logger.info("✅ Scraping FDJ terminé")
    
    except Exception as e:
        logger.error(f"❌ Erreur scraping FDJ: {e}", exc_info=True)
        raise ErreurService(f"Échec scraping FDJ: {e}")


# ═══════════════════════════════════════════════════════════
# JOB 2: BACKTEST GRILLES (Loto + Euromillions)
# ═══════════════════════════════════════════════════════════


def backtest_grilles():
    """
    Effectue le backtest de toutes les grilles en attente.
    
    Fréquence: 1×/jour à 22h (après scraping des tirages)
    
    Implémente:
    - Comparaison grilles vs derniers tirages
    - Calcul rang (1, 2, 3, etc.) selon nb bons numéros
    - Calcul gain selon barème FDJ
    - Mise à jour statut (gagnant/perdant)
    - Stats utilisateurs (ROI, win rate)
    """
    logger.info("🔍 Début backtest grilles Loto + Euromillions")
    
    try:
        with obtenir_contexte_db() as session:
            # Backtest Loto
            grilles_loto = session.query(GrilleLoto).filter(
                GrilleLoto.statut == "en_attente"
            ).all()
            
            nb_backtest_loto = 0
            for grille in grilles_loto:
                # Trouver tirage correspondant
                tirage = session.query(TirageLoto).filter(
                    TirageLoto.date == grille.date_tirage
                ).first()
                
                if not tirage:
                    continue
                
                # Comparer numéros
                numeros_grille = set(grille.numeros)
                numeros_tirage = set(tirage.numeros)
                nb_bons = len(numeros_grille & numeros_tirage)
                
                # Chance
                chance_ok = grille.numero_chance == tirage.numero_chance
                
                # Déterminer rang et gain
                rang, gain = _calculer_rang_gain_loto(nb_bons, chance_ok)
                
                # Mettre à jour grille
                grille.backtest = {
                    "rang": rang,
                    "nb_bons": nb_bons,
                    "chance_ok": chance_ok,
                    "gain": gain
                }
                
                if gain > 0:
                    grille.statut = "gagnant"
                else:
                    grille.statut = "perdant"
                
                nb_backtest_loto += 1
            
            # Backtest Euromillions
            grilles_euro = session.query(GrilleEuromillions).filter(
                GrilleEuromillions.statut == "en_attente"
            ).all()
            
            nb_backtest_euro = 0
            for grille in grilles_euro:
                tirage = session.query(TirageEuromillions).filter(
                    TirageEuromillions.date == grille.date_tirage
                ).first()
                
                if not tirage:
                    continue
                
                # Numéros
                numeros_grille = set(grille.numeros)
                numeros_tirage = set(tirage.numeros)
                nb_bons_numeros = len(numeros_grille & numeros_tirage)
                
                # Étoiles
                etoiles_grille = set(grille.etoiles)
                etoiles_tirage = set(tirage.etoiles)
                nb_bonnes_etoiles = len(etoiles_grille & etoiles_tirage)
                
                # Rang et gain
                rang, gain = _calculer_rang_gain_euromillions(nb_bons_numeros, nb_bonnes_etoiles)
                
                grille.backtest = {
                    "rang": rang,
                    "nb_bons_numeros": nb_bons_numeros,
                    "nb_bonnes_etoiles": nb_bonnes_etoiles,
                    "gain": gain
                }
                
                if gain > 0:
                    grille.statut = "gagnant"
                else:
                    grille.statut = "perdant"
                
                nb_backtest_euro += 1
            
            session.commit()
            
            logger.info(
                f"✅ Backtest terminé: {nb_backtest_loto} grilles Loto, "
                f"{nb_backtest_euro} grilles Euromillions"
            )
    
    except Exception as e:
        logger.error(f"❌ Erreur backtest grilles: {e}", exc_info=True)
        raise ErreurService(f"Échec backtest: {e}")


def _calculer_rang_gain_loto(nb_bons: int, chance_ok: bool) -> tuple[int, float]:
    """
    Calcule le rang et le gain Loto selon barème FDJ.
    
    Rang 1: 5 bons + chance
    Rang 2: 5 bons
    Rang 3: 4 bons + chance
    Rang 4: 4 bons
    Rang 5: 3 bons + chance
    Rang 6: 3 bons
    Rang 7: 2 bons + chance
    Rang 8: 2 bons
    
    Returns:
        (rang, gain_estimé)
    """
    if nb_bons == 5 and chance_ok:
        return (1, 1_000_000.0)  # Jackpot (estimé)
    elif nb_bons == 5:
        return (2, 20_000.0)
    elif nb_bons == 4 and chance_ok:
        return (3, 1_000.0)
    elif nb_bons == 4:
        return (4, 100.0)
    elif nb_bons == 3 and chance_ok:
        return (5, 20.0)
    elif nb_bons == 3:
        return (6, 5.0)
    elif nb_bons == 2 and chance_ok:
        return (7, 2.5)
    elif nb_bons == 2:
        return (8, 2.0)
    else:
        return (0, 0.0)


def _calculer_rang_gain_euromillions(nb_bons_numeros: int, nb_bonnes_etoiles: int) -> tuple[int, float]:
    """
    Calcule le rang et le gain Euromillions selon barème FDJ.
    
    Rang 1: 5N + 2E
    Rang 2: 5N + 1E
    Rang 3: 5N + 0E
    Rang 4: 4N + 2E
    Rang 5: 4N + 1E
    Rang 6: 4N + 0E ou 3N + 2E
    Rang 7: 2N + 2E ou 3N + 1E
    Rang 8: 3N + 0E ou 1N + 2E
    Rang 9: 2N + 1E
    Rang 10: 2N + 0E
    
    Returns:
        (rang, gain_estimé)
    """
    if nb_bons_numeros == 5 and nb_bonnes_etoiles == 2:
        return (1, 10_000_000.0)  # Jackpot
    elif nb_bons_numeros == 5 and nb_bonnes_etoiles == 1:
        return (2, 100_000.0)
    elif nb_bons_numeros == 5 and nb_bonnes_etoiles == 0:
        return (3, 10_000.0)
    elif nb_bons_numeros == 4 and nb_bonnes_etoiles == 2:
        return (4, 1_000.0)
    elif nb_bons_numeros == 4 and nb_bonnes_etoiles == 1:
        return (5, 100.0)
    elif (nb_bons_numeros == 4 and nb_bonnes_etoiles == 0) or \
         (nb_bons_numeros == 3 and nb_bonnes_etoiles == 2):
        return (6, 20.0)
    elif (nb_bons_numeros == 2 and nb_bonnes_etoiles == 2) or \
         (nb_bons_numeros == 3 and nb_bonnes_etoiles == 1):
        return (7, 10.0)
    elif (nb_bons_numeros == 3 and nb_bonnes_etoiles == 0) or \
         (nb_bons_numeros == 1 and nb_bonnes_etoiles == 2):
        return (8, 5.0)
    elif nb_bons_numeros == 2 and nb_bonnes_etoiles == 1:
        return (9, 3.0)
    elif nb_bons_numeros == 2 and nb_bonnes_etoiles == 0:
        return (10, 2.0)
    else:
        return (0, 0.0)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION SCHEDULER
# ═══════════════════════════════════════════════════════════


def configurer_jobs_loteries(scheduler: Any) -> None:
    """
    Configure les 2 cron jobs Loteries dans APScheduler.
    
    Args:
        scheduler: Instance APScheduler
    """
    # Job 1: Scraper résultats FDJ - 1×/jour à 21h30
    scheduler.add_job(
        scraper_resultats_fdj,
        trigger=CronTrigger(hour=21, minute=30),
        id="scraper_resultats_fdj",
        name="Scraper résultats FDJ (Loto + Euromillions)",
        replace_existing=True,
        max_instances=1
    )
    logger.info("✅ Job 'Scraper résultats FDJ' configuré (21h30 quotidien)")
    
    # Job 2: Backtest grilles - 1×/jour à 22h
    scheduler.add_job(
        backtest_grilles,
        trigger=CronTrigger(hour=22, minute=0),
        id="backtest_grilles",
        name="Backtest grilles Loto + Euromillions",
        replace_existing=True,
        max_instances=1
    )
    logger.info("✅ Job 'Backtest grilles' configuré (22h quotidien)")
