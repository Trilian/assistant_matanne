"""
Module Service pour Paris Sportifs avec intégration API Football-Data
"""

from typing import List, Dict, Any, Optional
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


def charger_matchs_depuis_api(championnat: str, jours: int = 7) -> List[Dict[str, Any]]:
    """
    Charge les matchs depuis Football-Data API et convertit au format local
    
    Args:
        championnat: Nom du championnat
        jours: Nombre de jours à chercher
        
    Returns:
        Liste des matchs au format application
    """
    try:
        from src.domains.jeux.logic.api_football import charger_matchs_a_venir
        
        matchs_api = charger_matchs_a_venir(championnat, jours)
        
        # Convertir au format attendu par paris.py
        matchs_convertis = []
        for m in matchs_api:
            matchs_convertis.append({
                "api_id": m.get("id"),
                "date": m.get("date"),
                "heure": m.get("heure"),
                "championnat": m.get("championnat"),
                "dom_nom": m.get("equipe_domicile"),
                "ext_nom": m.get("equipe_exterieur"),
                "cote_dom": 1.8,  # À récupérer depuis odds si disponibles
                "cote_nul": 3.5,
                "cote_ext": 4.2,
                "source": "Football-Data API"
            })
        
        logger.info(f"✅ {len(matchs_convertis)} matchs chargés depuis API")
        return matchs_convertis
    
    except Exception as e:
        logger.error(f"❌ Erreur chargement API: {e}")
        return []


def charger_classement_depuis_api(championnat: str) -> List[Dict[str, Any]]:
    """
    Charge le classement d'un championnat depuis l'API
    
    Args:
        championnat: Nom du championnat
        
    Returns:
        Liste des équipes avec leurs stats
    """
    try:
        from src.domains.jeux.logic.api_football import charger_classement
        
        equipes = charger_classement(championnat)
        logger.info(f"✅ Classement {championnat} chargé: {len(equipes)} équipes")
        return equipes
    
    except Exception as e:
        logger.error(f"❌ Erreur chargement classement: {e}")
        return []


def charger_historique_equipe_depuis_api(nom_equipe: str) -> List[Dict[str, Any]]:
    """
    Charge l'historique des matchs d'une équipe
    
    Args:
        nom_equipe: Nom de l'équipe
        
    Returns:
        Liste des matchs récents
    """
    try:
        from src.domains.jeux.logic.api_football import charger_historique_equipe
        
        matchs = charger_historique_equipe(nom_equipe, limite=10)
        logger.info(f"✅ Historique {nom_equipe}: {len(matchs)} matchs")
        return matchs
    
    except Exception as e:
        logger.error(f"❌ Erreur chargement historique: {e}")
        return []


def synchroniser_matchs_api_vers_bd(championnat: str, jours: int = 7):
    """
    Synchronise les matchs de l'API vers la base de données
    
    À appeler régulièrement pour maintenir les données à jour
    """
    try:
        from src.core.database import get_db_context
        from src.core.models import Equipe, Match
        from src.domains.jeux.logic.api_football import charger_matchs_a_venir
        
        matchs_api = charger_matchs_a_venir(championnat, jours)
        
        with get_db_context() as session:
            for m_data in matchs_api:
                # Chercher/créer les équipes
                equipe_dom = session.query(Equipe).filter_by(
                    nom=m_data.get("equipe_domicile")
                ).first()
                
                if not equipe_dom:
                    equipe_dom = Equipe(
                        nom=m_data.get("equipe_domicile"),
                        championnat=championnat,
                        matchs_joues=0,
                        victoires=0,
                        nuls=0,
                        defaites=0,
                        buts_marques=0,
                        buts_encaisses=0,
                        points=0
                    )
                    session.add(equipe_dom)
                    session.flush()
                
                equipe_ext = session.query(Equipe).filter_by(
                    nom=m_data.get("equipe_exterieur")
                ).first()
                
                if not equipe_ext:
                    equipe_ext = Equipe(
                        nom=m_data.get("equipe_exterieur"),
                        championnat=championnat,
                        matchs_joues=0,
                        victoires=0,
                        nuls=0,
                        defaites=0,
                        buts_marques=0,
                        buts_encaisses=0,
                        points=0
                    )
                    session.add(equipe_ext)
                    session.flush()
                
                # Vérifier si le match existe
                match_existing = session.query(Match).filter_by(
                    api_id=m_data.get("id"),
                    championnat=championnat
                ).first()
                
                if not match_existing:
                    match = Match(
                        api_id=m_data.get("id"),
                        date_match=m_data.get("date"),
                        heure=m_data.get("heure"),
                        championnat=championnat,
                        equipe_domicile_id=equipe_dom.id,
                        equipe_exterieur_id=equipe_ext.id,
                        cote_domicile=1.8,  # À optimiser avec les odds réels
                        cote_nul=3.5,
                        cote_exterieur=4.2,
                        statut_match="SCHEDULED",
                        joue=False,
                        source="Football-Data API"
                    )
                    session.add(match)
            
            session.commit()
            logger.info(f"✅ BD synchronisée avec API pour {championnat}")
            return True
    
    except Exception as e:
        logger.error(f"❌ Erreur synchronisation BD: {e}")
        return False


def synchroniser_resultats_matches_api(championnat: str):
    """
    Met à jour les résultats des matchs joués
    """
    try:
        from src.core.database import get_db_context
        from src.core.models import Match
        from src.domains.jeux.logic.api_football import charger_matchs_a_venir
        
        # Charger les matchs "FINISHED" depuis l'API
        matchs_api = charger_matchs_a_venir(
            championnat,
            jours=30,  # Chercher les 30 derniers jours
            statut="FINISHED"
        )
        
        with get_db_context() as session:
            for m_data in matchs_api:
                match = session.query(Match).filter_by(
                    api_id=m_data.get("id")
                ).first()
                
                if match and not match.joue:
                    match.score_domicile = m_data.get("score_domicile")
                    match.score_exterieur = m_data.get("score_exterieur")
                    match.joue = True
                    match.statut_match = "FINISHED"
                    session.add(match)
            
            session.commit()
            logger.info(f"✅ Résultats mis à jour pour {championnat}")
            return True
    
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour résultats: {e}")
        return False
