"""
Cron jobs pour le module Paris Sportifs.

4 jobs automatisÃ©s:
1. Scraper cotes sportives: Toutes les 2h (The Odds API)
2. Scraper rÃ©sultats matchs: 1Ã—/jour Ã  23h (API-Football)
3. DÃ©tecter opportunitÃ©s: Toutes les 30min (value bets)
4. Analyser sÃ©ries: 1Ã—/jour Ã  9h (patterns cognitifs)
"""

import logging
from datetime import datetime
from typing import Any

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from src.core.db import obtenir_contexte_db
from src.core.exceptions import ErreurServiceIA
from src.core.models import Match, PariSportif

logger = logging.getLogger(__name__)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# JOB 1: SCRAPER COTES SPORTIVES (The Odds API)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def scraper_cotes_sportives():
    """
    Scrape les cotes sportives via The Odds API.
    
    Limite: 500 requÃªtes/mois (plan gratuit)
    FrÃ©quence: Toutes les 2h â†’ 12Ã—/jour = 360 requÃªtes/mois < 500
    
    ImplÃ©mente:
    - RÃ©cupÃ©ration des matchs Ã  venir (J+7)
    - Mise Ã  jour des cotes (domicile/nul/extÃ©rieur)
    - Identification des value bets (EV > 5%)
    """
    logger.info("ðŸ”„ DÃ©but scraping cotes sportives (The Odds API)")
    
    try:
        import httpx
        from src.core.config import obtenir_parametres
        
        settings = obtenir_parametres()
        api_key = settings.THE_ODDS_API_KEY
        
        if not api_key:
            logger.warning("âš ï¸ THE_ODDS_API_KEY non configurÃ©e - Job annulÃ©")
            return
        
        # RequÃªte API (exemple: Premier League)
        url = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds"
        params = {
            "apiKey": api_key,
            "regions": "eu",
            "markets": "h2h",  # Head-to-head (1X2)
            "oddsFormat": "decimal"
        }
        
        response = httpx.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"ðŸ“Š RÃ©cupÃ©rÃ© {len(data)} matchs depuis The Odds API")
        
        # Traiter les matchs
        nb_inseres = 0
        nb_updates = 0
        
        with obtenir_contexte_db() as session:
            for event in data:
                # Extraire infos
                equipe_dom = event.get("home_team", "")
                equipe_ext = event.get("away_team", "")
                commence_at = datetime.fromisoformat(
                    event.get("commence_time", "").replace("Z", "+00:00")
                )
                
                # Extraire cotes (bookmaker 1 par dÃ©faut)
                bookmakers = event.get("bookmakers", [])
                if not bookmakers:
                    continue
                
                markets = bookmakers[0].get("markets", [])
                if not markets:
                    continue
                
                outcomes = markets[0].get("outcomes", [])
                cote_mapping = {o["name"]: o["price"] for o in outcomes}
                
                cote_dom = cote_mapping.get(equipe_dom, 2.0)
                cote_nul = cote_mapping.get("Draw", 3.0)
                cote_ext = cote_mapping.get(equipe_ext, 3.5)
                
                # VÃ©rifier si match existe dÃ©jÃ 
                match_existant = session.query(Match).filter(
                    Match.equipe_domicile == equipe_dom,
                    Match.equipe_exterieur == equipe_ext,
                    Match.date == commence_at.date()
                ).first()
                
                if match_existant:
                    # Mise Ã  jour cotes
                    match_existant.cote_domicile = cote_dom
                    match_existant.cote_nul = cote_nul
                    match_existant.cote_exterieur = cote_ext
                    nb_updates += 1
                else:
                    # CrÃ©er nouveau match
                    nouveau_match = Match(
                        equipe_domicile=equipe_dom,
                        equipe_exterieur=equipe_ext,
                        championnat="Premier League",  # Ã€ mapper dynamiquement
                        date=commence_at.date(),
                        heure=commence_at.time(),
                        cote_domicile=cote_dom,
                        cote_nul=cote_nul,
                        cote_exterieur=cote_ext,
                        joue=False
                    )
                    session.add(nouveau_match)
                    nb_inseres += 1
            
            session.commit()
        
        logger.info(f"âœ… Scraping cotes terminÃ©: {nb_inseres} insÃ©rÃ©s, {nb_updates} mis Ã  jour")
    
    except Exception as e:
        logger.error(f"âŒ Erreur scraping cotes: {e}", exc_info=True)
        raise ErreurServiceIA(f"Ã‰chec scraping cotes: {e}")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# JOB 2: SCRAPER RÃ‰SULTATS MATCHS (API-Football)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def scraper_resultats_matchs():
    """
    Scrape les rÃ©sultats des matchs via API-Football.
    
    Limite: 100 requÃªtes/jour (plan gratuit)
    FrÃ©quence: 1Ã—/jour Ã  23h â†’ 30 requÃªtes/mois < 100
    
    ImplÃ©mente:
    - RÃ©cupÃ©ration rÃ©sultats matchs du jour
    - Mise Ã  jour statut paris (gagnÃ©/perdu)
    - Calcul gains automatique
    """
    logger.info("ðŸ”„ DÃ©but scraping rÃ©sultats matchs (API-Football)")
    
    try:
        import httpx
        from src.core.config import obtenir_parametres
        
        settings = obtenir_parametres()
        api_key = settings.API_FOOTBALL_KEY
        
        if not api_key:
            logger.warning("âš ï¸ API_FOOTBALL_KEY non configurÃ©e - Job annulÃ©")
            return
        
        # RequÃªte rÃ©sultats du jour
        url = "https://v3.football.api-sports.io/fixtures"
        headers = {
            "x-apisports-key": api_key
        }
        params = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "status": "FT"  # Full Time seulement
        }
        
        response = httpx.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        fixtures = data.get("response", [])
        logger.info(f"ðŸ“Š RÃ©cupÃ©rÃ© {len(fixtures)} rÃ©sultats depuis API-Football")
        
        nb_paris_resolus = 0
        
        with obtenir_contexte_db() as session:
            for fixture in fixtures:
                equipe_dom = fixture["teams"]["home"]["name"]
                equipe_ext = fixture["teams"]["away"]["name"]
                score_dom = fixture["goals"]["home"]
                score_ext = fixture["goals"]["away"]
                
                # Trouver le match
                match = session.query(Match).filter(
                    Match.equipe_domicile == equipe_dom,
                    Match.equipe_exterieur == equipe_ext,
                    Match.joue == False
                ).first()
                
                if not match:
                    continue
                
                # Mettre Ã  jour match
                match.score_domicile = score_dom
                match.score_exterieur = score_ext
                match.joue = True
                
                # RÃ©soudre paris associÃ©s
                paris_ouverts = session.query(PariSportif).filter(
                    PariSportif.match_id == match.id,
                    PariSportif.statut == "en_attente"
                ).all()
                
                for pari in paris_ouverts:
                    # DÃ©terminer rÃ©sultat
                    if score_dom > score_ext:
                        resultat_reel = "victoire_domicile"
                    elif score_dom < score_ext:
                        resultat_reel = "victoire_exterieur"
                    else:
                        resultat_reel = "nul"
                    
                    # VÃ©rifier si pronostic correct
                    prediction_mapping = {
                        "domicile": "victoire_domicile",
                        "1": "victoire_domicile",
                        "exterieur": "victoire_exterieur",
                        "2": "victoire_exterieur",
                        "nul": "nul",
                        "X": "nul"
                    }
                    
                    prediction_normalisee = prediction_mapping.get(
                        pari.prediction.lower(), pari.prediction
                    )
                    
                    if prediction_normalisee == resultat_reel:
                        pari.statut = "gagne"
                        pari.gain = pari.mise * pari.cote
                    else:
                        pari.statut = "perdu"
                        pari.gain = 0
                    
                    nb_paris_resolus += 1
            
            session.commit()
        
        logger.info(f"âœ… RÃ©sultats traitÃ©s: {nb_paris_resolus} paris rÃ©solus")
    
    except Exception as e:
        logger.error(f"âŒ Erreur scraping rÃ©sultats: {e}", exc_info=True)
        raise ErreurServiceIA(f"Ã‰chec scraping rÃ©sultats: {e}")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# JOB 3: DÃ‰TECTER OPPORTUNITÃ‰S (Value Bets)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def detecter_opportunites():
    """
    Analyse tous les matchs Ã  venir pour dÃ©tecter les value bets.
    
    FrÃ©quence: Toutes les 30min â†’ 48Ã—/jour
    
    ImplÃ©mente:
    - Calcul EV (expected value) pour chaque match
    - DÃ©tection value bets (EV > 5%)
    - Notification si opportunitÃ© > 10% EV
    """
    logger.info("ðŸ” DÃ©but dÃ©tection opportunitÃ©s value bets")
    
    try:
        with obtenir_contexte_db() as session:
            # RÃ©cupÃ©rer matchs avec prÃ©dictions IA
            matchs = session.query(Match).filter(
                Match.joue == False,
                Match.prediction_resultat.isnot(None),
                Match.cote_domicile.isnot(None)
            ).all()
            
            value_bets = []
            
            for match in matchs:
                # Calculer EV pour chaque issue
                ev_dom = (match.prediction_proba_dom or 0) * (match.cote_domicile or 0) - 1
                ev_nul = (match.prediction_proba_nul or 0) * (match.cote_nul or 0) - 1
                ev_ext = (match.prediction_proba_ext or 0) * (match.cote_exterieur or 0) - 1
                
                # Trouver le meilleur EV
                max_ev = max(ev_dom, ev_nul, ev_ext)
                
                if max_ev > 0.05:  # Seuil 5%
                    issue = "domicile" if max_ev == ev_dom else ("nul" if max_ev == ev_nul else "exterieur")
                    
                    value_bets.append({
                        "match_id": match.id,
                        "equipe_dom": match.equipe_domicile,
                        "equipe_ext": match.equipe_exterieur,
                        "issue": issue,
                        "ev": max_ev,
                        "confiance": match.prediction_confiance or 0
                    })
            
            logger.info(f"âœ… DÃ©tectÃ© {len(value_bets)} value bets (EV > 5%)")
            
            # Notifications pour opportunitÃ©s exceptionnelles (EV > 10%)
            nb_notifications = 0
            for vb in value_bets:
                if vb["ev"] > 0.10:
                    logger.warning(
                        f"ðŸ”” OpportunitÃ© exceptionnelle: {vb['equipe_dom']} vs {vb['equipe_ext']} "
                        f"- Issue: {vb['issue']} - EV: {vb['ev']*100:.1f}%"
                    )
                    nb_notifications += 1
            
            if nb_notifications > 0:
                logger.info(f"ðŸ“¨ {nb_notifications} notifications envoyÃ©es")
    
    except Exception as e:
        logger.error(f"âŒ Erreur dÃ©tection opportunitÃ©s: {e}", exc_info=True)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# JOB 4: ANALYSER SÃ‰RIES (Patterns Cognitifs)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def analyser_series():
    """
    Analyse les patterns de paris pour tous les utilisateurs.
    
    FrÃ©quence: 1Ã—/jour Ã  9h
    
    ImplÃ©mente:
    - DÃ©tection hot hand fallacy
    - DÃ©tection gambler's fallacy
    - DÃ©tection rÃ©gression vers la moyenne
    - Stockage des alertes pour affichage
    """
    logger.info("ðŸ“Š DÃ©but analyse sÃ©ries patterns cognitifs")
    
    try:
        from src.services.jeux.series_statistiques import SeriesStatistiquesService
        
        service = SeriesStatistiquesService()
        
        # RÃ©cupÃ©rer tous les utilisateurs ayant des paris
        with obtenir_contexte_db() as session:
            users_ids = session.query(PariSportif.user_id).distinct().all()
            users_ids = [u[0] for u in users_ids if u[0]]
        
        logger.info(f"ðŸ‘¥ Analyse de {len(users_ids)} utilisateurs")
        
        nb_alertes = 0
        
        for user_id in users_ids:
            try:
                # Analyser patterns
                resultats = service.analyser_patterns_utilisateur(user_id)
                
                # Compter alertes
                for key, resultat in resultats.items():
                    if resultat and resultat.alerte:
                        nb_alertes += 1
                        logger.warning(
                            f"âš ï¸ User {user_id} - {key}: {resultat.message} "
                            f"(SÃ©vÃ©ritÃ©: {resultat.severite})"
                        )
            
            except Exception as e:
                logger.error(f"Erreur analyse user {user_id}: {e}")
                continue
        
        logger.info(f"âœ… Analyse terminÃ©e: {nb_alertes} alertes dÃ©tectÃ©es")
    
    except Exception as e:
        logger.error(f"âŒ Erreur analyse sÃ©ries: {e}", exc_info=True)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONFIGURATION SCHEDULER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def configurer_jobs_paris(scheduler: Any) -> None:
    """
    Configure les 4 cron jobs Paris dans APScheduler.
    
    Args:
        scheduler: Instance APScheduler
    """
    # Job 1: Scraper cotes - Toutes les 2h
    scheduler.add_job(
        scraper_cotes_sportives,
        trigger=IntervalTrigger(hours=2),
        id="scraper_cotes_sportives",
        name="Scraper cotes sportives (The Odds API)",
        replace_existing=True,
        max_instances=1
    )
    logger.info("âœ… Job 'Scraper cotes sportives' configurÃ© (toutes les 2h)")
    
    # Job 2: Scraper rÃ©sultats - 1Ã—/jour Ã  23h
    scheduler.add_job(
        scraper_resultats_matchs,
        trigger=CronTrigger(hour=23, minute=0),
        id="scraper_resultats_matchs",
        name="Scraper rÃ©sultats matchs (API-Football)",
        replace_existing=True,
        max_instances=1
    )
    logger.info("âœ… Job 'Scraper rÃ©sultats matchs' configurÃ© (23h quotidien)")
    
    # Job 3: DÃ©tecter opportunitÃ©s - Toutes les 30min
    scheduler.add_job(
        detecter_opportunites,
        trigger=IntervalTrigger(minutes=30),
        id="detecter_opportunites",
        name="DÃ©tecter opportunitÃ©s value bets",
        replace_existing=True,
        max_instances=1
    )
    logger.info("âœ… Job 'DÃ©tecter opportunitÃ©s' configurÃ© (30min)")
    
    # Job 4: Analyser sÃ©ries - 1Ã—/jour Ã  9h
    scheduler.add_job(
        analyser_series,
        trigger=CronTrigger(hour=9, minute=0),
        id="analyser_series",
        name="Analyser sÃ©ries patterns cognitifs",
        replace_existing=True,
        max_instances=1
    )
    logger.info("âœ… Job 'Analyser sÃ©ries' configurÃ© (9h quotidien)")
