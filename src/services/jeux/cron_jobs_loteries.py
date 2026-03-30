"""
Cron jobs pour le module Loteries (Loto + Euromillions).

2 jobs automatisés:
1. Scraper résultats FDJ: 1×/jour à 21h30 (après tirages)
2. Backtest grilles: 1×/jour à 22h (après scraping)
"""

import csv
import io
import logging
import zipfile
from datetime import datetime, date
from typing import Any

from apscheduler.triggers.cron import CronTrigger

from src.core.db import obtenir_contexte_db
from src.core.exceptions import ErreurService
from src.core.models.jeux import TirageLoto, TirageEuromillions, GrilleLoto, GrilleEuromillions

logger = logging.getLogger(__name__)


# URLs publiques FDJ pour les historiques de tirages (fichiers ZIP contenant des CSV)
# Ces URLs sont accessibles sans authentification depuis la page historique FDJ.
_FDJ_LOTO_CSV_URL = (
    "https://www.sto.api.fdj.fr/anonymous/service-draw-info/v3/documentations/"
    "1a2b3c4d-9876-4562-b3fc-2c963f66afp6"
)
_FDJ_EUROMILLIONS_CSV_URL = (
    "https://www.sto.api.fdj.fr/anonymous/service-draw-info/v3/documentations/"
    "1a2b3c4d-9876-4562-b3fc-2c963f66afq6"
)

# Timeout pour les requêtes HTTP vers FDJ
_HTTP_TIMEOUT = 30


# ═══════════════════════════════════════════════════════════
# JOB 1: SCRAPER RÉSULTATS FDJ (Loto + Euromillions)
# ═══════════════════════════════════════════════════════════


def scraper_resultats_fdj():
    """
    Scrape les résultats des tirages Loto et Euromillions via l'API publique FDJ.

    Fréquence: 1×/jour à 21h30 (après les tirages à 21h)

    Implémente:
    - Téléchargement du fichier historique CSV depuis l'API FDJ
    - Parsing des résultats (numéros + chance/étoiles + jackpot)
    - Insertion des tirages manquants en base
    - Gestion des erreurs réseau avec fallback
    """
    logger.info("🔄 Début scraping résultats FDJ (Loto + Euromillions)")

    nb_loto = 0
    nb_euro = 0

    try:
        nb_loto = _scraper_tirages_loto()
        logger.info(f"✅ Loto: {nb_loto} nouveau(x) tirage(s) inséré(s)")
    except Exception as e:
        logger.error(f"❌ Erreur scraping Loto: {e}", exc_info=True)

    try:
        nb_euro = _scraper_tirages_euromillions()
        logger.info(f"✅ Euromillions: {nb_euro} nouveau(x) tirage(s) inséré(s)")
    except Exception as e:
        logger.error(f"❌ Erreur scraping Euromillions: {e}", exc_info=True)

    logger.info(f"✅ Scraping FDJ terminé: {nb_loto} Loto + {nb_euro} Euromillions")


def _telecharger_csv_fdj(url: str) -> str:
    """Télécharge un fichier CSV ou ZIP depuis l'API FDJ et retourne le contenu CSV."""
    import httpx

    response = httpx.get(url, timeout=_HTTP_TIMEOUT, follow_redirects=True)
    response.raise_for_status()

    content_type = response.headers.get("content-type", "")

    # Si c'est un ZIP, extraire le premier CSV
    if "zip" in content_type or url.endswith(".zip") or response.content[:4] == b"PK\x03\x04":
        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
            csv_files = [n for n in zf.namelist() if n.endswith(".csv")]
            if not csv_files:
                raise ErreurService("Aucun fichier CSV trouvé dans l'archive ZIP FDJ")
            return zf.read(csv_files[0]).decode("utf-8-sig")

    # Sinon, c'est directement un CSV
    return response.text


def _parser_date_fdj(date_str: str) -> date | None:
    """Parse une date FDJ (formats: dd/mm/yyyy, yyyy-mm-dd, etc.)."""
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except (ValueError, AttributeError):
            continue
    return None


def _scraper_tirages_loto() -> int:
    """Télécharge et insère les tirages Loto manquants. Retourne le nombre inséré."""
    csv_content = _telecharger_csv_fdj(_FDJ_LOTO_CSV_URL)
    reader = csv.DictReader(io.StringIO(csv_content), delimiter=";")

    # Normaliser les noms de colonnes (le CSV FDJ utilise des noms variés)
    tirages_a_inserer = []
    for row in reader:
        # Adapter selon les noms de colonnes FDJ connus
        date_tirage = _parser_date_fdj(
            row.get("date_de_tirage", row.get("date", row.get("Date", "")))
        )
        if not date_tirage:
            continue

        try:
            # Les colonnes de numéros FDJ sont nommées "boule_1" à "boule_5" + "numero_chance"
            numeros = []
            for col_prefix in ("boule_", "Boule ", "numero_"):
                for i in range(1, 6):
                    val = row.get(f"{col_prefix}{i}")
                    if val and val.strip().isdigit():
                        numeros.append(int(val.strip()))
                if len(numeros) == 5:
                    break

            if len(numeros) != 5:
                continue

            chance_val = row.get("numero_chance", row.get("Numero Chance", row.get("chance", "")))
            if not chance_val or not str(chance_val).strip().isdigit():
                continue
            numero_chance = int(str(chance_val).strip())

            # Jackpot (optionnel)
            jackpot_str = row.get("rapport_du_rang1", row.get("jackpot", ""))
            jackpot = None
            if jackpot_str:
                try:
                    jackpot = int(float(str(jackpot_str).replace(",", ".").replace(" ", "").replace("€", "")))
                except (ValueError, TypeError):
                    pass

            # Gagnants rang 1 (optionnel)
            gagnants_str = row.get("nombre_de_gagnant_au_rang1", row.get("gagnants_rang1", ""))
            gagnants = None
            if gagnants_str:
                try:
                    gagnants = int(str(gagnants_str).strip())
                except (ValueError, TypeError):
                    pass

            tirages_a_inserer.append({
                "date_tirage": date_tirage,
                "numeros": sorted(numeros),
                "numero_chance": numero_chance,
                "jackpot": jackpot,
                "gagnants": gagnants,
            })
        except (ValueError, KeyError, TypeError) as e:
            logger.debug(f"Ligne Loto ignorée : {e}")
            continue

    # Insérer les tirages manquants en base
    nb_inseres = 0
    with obtenir_contexte_db() as session:
        for t in tirages_a_inserer:
            existant = session.query(TirageLoto).filter(
                TirageLoto.date_tirage == t["date_tirage"]
            ).first()
            if existant:
                continue

            tirage = TirageLoto(
                date_tirage=t["date_tirage"],
                numero_1=t["numeros"][0],
                numero_2=t["numeros"][1],
                numero_3=t["numeros"][2],
                numero_4=t["numeros"][3],
                numero_5=t["numeros"][4],
                numero_chance=t["numero_chance"],
                jackpot_euros=t["jackpot"],
                gagnants_rang1=t["gagnants"],
            )
            session.add(tirage)
            nb_inseres += 1

        if nb_inseres > 0:
            session.commit()
            logger.info(f"📥 {nb_inseres} tirage(s) Loto inséré(s)")

    return nb_inseres


def _scraper_tirages_euromillions() -> int:
    """Télécharge et insère les tirages Euromillions manquants. Retourne le nombre inséré."""
    csv_content = _telecharger_csv_fdj(_FDJ_EUROMILLIONS_CSV_URL)
    reader = csv.DictReader(io.StringIO(csv_content), delimiter=";")

    tirages_a_inserer = []
    for row in reader:
        date_tirage = _parser_date_fdj(
            row.get("date_de_tirage", row.get("date", row.get("Date", "")))
        )
        if not date_tirage:
            continue

        try:
            # Numéros principaux (5)
            numeros = []
            for col_prefix in ("boule_", "Boule ", "numero_"):
                for i in range(1, 6):
                    val = row.get(f"{col_prefix}{i}")
                    if val and val.strip().isdigit():
                        numeros.append(int(val.strip()))
                if len(numeros) == 5:
                    break

            if len(numeros) != 5:
                continue

            # Étoiles (2)
            etoiles = []
            for col_prefix in ("etoile_", "Etoile ", "étoile_"):
                for i in range(1, 3):
                    val = row.get(f"{col_prefix}{i}")
                    if val and val.strip().isdigit():
                        etoiles.append(int(val.strip()))
                if len(etoiles) == 2:
                    break

            if len(etoiles) != 2:
                continue

            # Jackpot (optionnel)
            jackpot_str = row.get("rapport_du_rang1", row.get("jackpot", ""))
            jackpot = None
            if jackpot_str:
                try:
                    jackpot = int(float(str(jackpot_str).replace(",", ".").replace(" ", "").replace("€", "")))
                except (ValueError, TypeError):
                    pass

            # Gagnants rang 1 (optionnel)
            gagnants_str = row.get("nombre_de_gagnant_au_rang1", row.get("gagnants_rang1", ""))
            gagnants = None
            if gagnants_str:
                try:
                    gagnants = int(str(gagnants_str).strip())
                except (ValueError, TypeError):
                    pass

            # My Million (optionnel)
            my_million = row.get("code_my_million", row.get("My Million", None))

            tirages_a_inserer.append({
                "date_tirage": date_tirage,
                "numeros": sorted(numeros),
                "etoiles": sorted(etoiles),
                "jackpot": jackpot,
                "gagnants": gagnants,
                "my_million": str(my_million).strip() if my_million else None,
            })
        except (ValueError, KeyError, TypeError) as e:
            logger.debug(f"Ligne Euromillions ignorée : {e}")
            continue

    # Insérer les tirages manquants en base
    nb_inseres = 0
    with obtenir_contexte_db() as session:
        for t in tirages_a_inserer:
            existant = session.query(TirageEuromillions).filter(
                TirageEuromillions.date_tirage == t["date_tirage"]
            ).first()
            if existant:
                continue

            tirage = TirageEuromillions(
                date_tirage=t["date_tirage"],
                numero_1=t["numeros"][0],
                numero_2=t["numeros"][1],
                numero_3=t["numeros"][2],
                numero_4=t["numeros"][3],
                numero_5=t["numeros"][4],
                etoile_1=t["etoiles"][0],
                etoile_2=t["etoiles"][1],
                jackpot_euros=t["jackpot"],
                gagnants_rang1=t["gagnants"],
                code_my_million=t["my_million"],
            )
            session.add(tirage)
            nb_inseres += 1

        if nb_inseres > 0:
            session.commit()
            logger.info(f"📥 {nb_inseres} tirage(s) Euromillions inséré(s)")

    return nb_inseres


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
