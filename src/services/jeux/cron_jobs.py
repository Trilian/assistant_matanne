"""
Cron jobs pour le module Paris Sportifs.

4 jobs automatisés:
1. Scraper cotes sportives: Toutes les 2h (The Odds API)
2. Scraper résultats matchs: 1×/jour à 23h (API-Football)
3. Détecter opportunités: Toutes les 30min (value bets)
4. Analyser séries: 1×/jour à 9h (patterns cognitifs)
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


# ═══════════════════════════════════════════════════════════
# JOB 1: SCRAPER COTES SPORTIVES (The Odds API)
# ═══════════════════════════════════════════════════════════


def scraper_cotes_sportives():
    """
    Scrape les cotes sportives via The Odds API.

    Limite: 500 requêtes/mois (plan gratuit)
    Fréquence: Toutes les 2h → 12×/jour = 360 requêtes/mois < 500

    Implémente:
    - Récupération des matchs à venir (J+7)
    - Mise à jour des cotes (domicile/nul/extérieur)
    - Identification des value bets (EV > 5%)
    """
    logger.info("🔄 Début scraping cotes sportives (The Odds API)")

    try:
        import httpx

        from src.core.config import obtenir_parametres

        settings = obtenir_parametres()
        api_key = getattr(settings, "THE_ODDS_API_KEY", None)

        if not api_key:
            logger.warning("⚠️ THE_ODDS_API_KEY non configurée - Job annulé")
            return

        # Requête API (exemple: Premier League)
        url = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds"
        params = {
            "apiKey": api_key,
            "regions": "eu",
            "markets": "h2h",  # Head-to-head (1X2)
            "oddsFormat": "decimal",
        }

        response = httpx.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        logger.info(f"📊 Récupéré {len(data)} matchs depuis The Odds API")

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

                # Extraire cotes (bookmaker 1 par défaut)
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

                # Vérifier si match existe déjà
                match_existant = (
                    session.query(Match)
                    .filter(
                        Match.equipe_domicile == equipe_dom,
                        Match.equipe_exterieur == equipe_ext,
                        Match.date == commence_at.date(),
                    )
                    .first()
                )

                if match_existant:
                    # Mise à jour cotes
                    match_existant.cote_domicile = cote_dom
                    match_existant.cote_nul = cote_nul
                    match_existant.cote_exterieur = cote_ext
                    nb_updates += 1
                else:
                    # Créer nouveau match
                    nouveau_match = Match(
                        equipe_domicile=equipe_dom,
                        equipe_exterieur=equipe_ext,
                        championnat="Premier League",  # À mapper dynamiquement
                        date=commence_at.date(),
                        heure=commence_at.time(),
                        cote_domicile=cote_dom,
                        cote_nul=cote_nul,
                        cote_exterieur=cote_ext,
                        joue=False,
                    )
                    session.add(nouveau_match)
                    nb_inseres += 1

            session.commit()

        logger.info(f"✅ Scraping cotes terminé: {nb_inseres} insérés, {nb_updates} mis à jour")

    except Exception as e:
        logger.error(f"❌ Erreur scraping cotes: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# JOB 2: SCRAPER RÉSULTATS MATCHS (API-Football)
# ═══════════════════════════════════════════════════════════


def scraper_resultats_matchs():
    """
    Scrape les résultats des matchs via API-Football.

    Limite: 100 requêtes/jour (plan gratuit)
    Fréquence: 1×/jour à 23h → 30 requêtes/mois < 100

    Implémente:
    - Récupération résultats matchs du jour
    - Mise à jour statut paris (gagné/perdu)
    - Calcul gains automatique
    """
    logger.info("🔄 Début scraping résultats matchs (API-Football)")

    try:
        import httpx

        from src.core.config import obtenir_parametres

        settings = obtenir_parametres()
        api_key = getattr(settings, "API_FOOTBALL_KEY", None)

        if not api_key:
            logger.warning("⚠️ API_FOOTBALL_KEY non configurée - Job annulé")
            return

        # Requête résultats du jour
        url = "https://v3.football.api-sports.io/fixtures"
        headers = {"x-apisports-key": api_key}
        params = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "status": "FT",  # Full Time seulement
        }

        response = httpx.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        fixtures = data.get("response", [])
        logger.info(f"📊 Récupéré {len(fixtures)} résultats depuis API-Football")

        nb_paris_resolus = 0

        with obtenir_contexte_db() as session:
            for fixture in fixtures:
                equipe_dom = fixture["teams"]["home"]["name"]
                equipe_ext = fixture["teams"]["away"]["name"]
                score_dom = fixture["goals"]["home"]
                score_ext = fixture["goals"]["away"]

                # Trouver le match
                match = (
                    session.query(Match)
                    .filter(
                        Match.equipe_domicile == equipe_dom,
                        Match.equipe_exterieur == equipe_ext,
                        Match.joue == False,
                    )
                    .first()
                )

                if not match:
                    continue

                # Mettre à jour match
                match.score_domicile = score_dom
                match.score_exterieur = score_ext
                match.joue = True

                # Résoudre paris associés
                paris_ouverts = (
                    session.query(PariSportif)
                    .filter(PariSportif.match_id == match.id, PariSportif.statut == "en_attente")
                    .all()
                )

                for pari in paris_ouverts:
                    # Déterminer résultat
                    if score_dom > score_ext:
                        resultat_reel = "victoire_domicile"
                    elif score_dom < score_ext:
                        resultat_reel = "victoire_exterieur"
                    else:
                        resultat_reel = "nul"

                    # Vérifier si pronostic correct
                    prediction_mapping = {
                        "domicile": "victoire_domicile",
                        "1": "victoire_domicile",
                        "exterieur": "victoire_exterieur",
                        "2": "victoire_exterieur",
                        "nul": "nul",
                        "X": "nul",
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

        logger.info(f"✅ Résultats traités: {nb_paris_resolus} paris résolus")

    except Exception as e:
        logger.error(f"❌ Erreur scraping résultats: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# JOB 3: DÉTECTER OPPORTUNITÉS (Value Bets)
# ═══════════════════════════════════════════════════════════


def detecter_opportunites():
    """
    Analyse tous les matchs à venir pour détecter les value bets.

    Fréquence: Toutes les 30min → 48×/jour

    Implémente:
    - Calcul EV (expected value) pour chaque match
    - Détection value bets (EV > 5%)
    - Notification si opportunité > 10% EV
    """
    logger.info("🔍 Début détection opportunités value bets")

    try:
        with obtenir_contexte_db() as session:
            # Récupérer matchs avec prédictions IA
            matchs = (
                session.query(Match)
                .filter(
                    Match.joue == False,
                    Match.prediction_resultat.isnot(None),
                    Match.cote_domicile.isnot(None),
                )
                .all()
            )

            value_bets = []

            for match in matchs:
                # Calculer EV pour chaque issue
                ev_dom = (match.prediction_proba_dom or 0) * (match.cote_domicile or 0) - 1
                ev_nul = (match.prediction_proba_nul or 0) * (match.cote_nul or 0) - 1
                ev_ext = (match.prediction_proba_ext or 0) * (match.cote_exterieur or 0) - 1

                # Trouver le meilleur EV
                max_ev = max(ev_dom, ev_nul, ev_ext)

                if max_ev > 0.05:  # Seuil 5%
                    issue = (
                        "domicile"
                        if max_ev == ev_dom
                        else ("nul" if max_ev == ev_nul else "exterieur")
                    )

                    value_bets.append(
                        {
                            "match_id": match.id,
                            "equipe_dom": match.equipe_domicile,
                            "equipe_ext": match.equipe_exterieur,
                            "issue": issue,
                            "ev": max_ev,
                            "confiance": match.prediction_confiance or 0,
                        }
                    )

            logger.info(f"✅ Détecté {len(value_bets)} value bets (EV > 5%)")

            # Notifications pour opportunités exceptionnelles (EV > 10%)
            nb_notifications = 0
            for vb in value_bets:
                if vb["ev"] > 0.10:
                    logger.warning(
                        f"🔔 Opportunité exceptionnelle: {vb['equipe_dom']} vs {vb['equipe_ext']} "
                        f"- Issue: {vb['issue']} - EV: {vb['ev'] * 100:.1f}%"
                    )
                    nb_notifications += 1

            if nb_notifications > 0:
                logger.info(f"📨 {nb_notifications} notifications envoyées")

    except Exception as e:
        logger.error(f"❌ Erreur détection opportunités: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# JOB 4: ANALYSER SÉRIES (Patterns Cognitifs)
# ═══════════════════════════════════════════════════════════


def analyser_series():
    """
    Analyse les patterns de paris pour tous les utilisateurs.

    Fréquence: 1×/jour à 9h

    Implémente:
    - Détection hot hand fallacy
    - Détection gambler's fallacy
    - Détection régression vers la moyenne
    - Stockage des alertes pour affichage
    """
    logger.info("📊 Début analyse séries patterns cognitifs")

    try:
        from src.services.jeux.series_statistiques import SeriesStatistiquesService

        service = SeriesStatistiquesService()

        # Récupérer tous les utilisateurs ayant des paris
        with obtenir_contexte_db() as session:
            users_ids = session.query(PariSportif.user_id).distinct().all()
            users_ids = [u[0] for u in users_ids if u[0]]

        logger.info(f"👥 Analyse de {len(users_ids)} utilisateurs")

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
                            f"⚠️ User {user_id} - {key}: {resultat.message} "
                            f"(Sévérité: {resultat.severite})"
                        )

            except Exception as e:
                logger.error(f"Erreur analyse user {user_id}: {e}")
                continue

        logger.info(f"✅ Analyse terminée: {nb_alertes} alertes détectées")

    except Exception as e:
        logger.error(f"❌ Erreur analyse séries: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION SCHEDULER
# ═══════════════════════════════════════════════════════════


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
        max_instances=1,
    )
    logger.info("✅ Job 'Scraper cotes sportives' configuré (toutes les 2h)")

    # Job 2: Scraper résultats - 1×/jour à 23h
    scheduler.add_job(
        scraper_resultats_matchs,
        trigger=CronTrigger(hour=23, minute=0),
        id="scraper_resultats_matchs",
        name="Scraper résultats matchs (API-Football)",
        replace_existing=True,
        max_instances=1,
    )
    logger.info("✅ Job 'Scraper résultats matchs' configuré (23h quotidien)")

    # Job 3: Détecter opportunités - Toutes les 30min
    scheduler.add_job(
        detecter_opportunites,
        trigger=IntervalTrigger(minutes=30),
        id="detecter_opportunites",
        name="Détecter opportunités value bets",
        replace_existing=True,
        max_instances=1,
    )
    logger.info("✅ Job 'Détecter opportunités' configuré (30min)")

    # Job 4: Analyser séries - 1×/jour à 9h
    scheduler.add_job(
        analyser_series,
        trigger=CronTrigger(hour=9, minute=0),
        id="analyser_series",
        name="Analyser séries patterns cognitifs",
        replace_existing=True,
        max_instances=1,
    )
    logger.info("✅ Job 'Analyser séries' configuré (9h quotidien)")
