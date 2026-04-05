"""
Service de statistiques personnelles pour le module Jeux.

Calcule ROI, win rate, patterns gagnants pour Paris Sportifs, Loto et Euromillions.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db
from src.core.exceptions import ErreurServiceIA
from src.core.models.jeux import PariSportif, GrilleLoto, GrilleEuromillions
from src.services.core.analytics import obtenir_analytics
from src.services.jeux.bankroll_manager import get_bankroll_manager

logger = logging.getLogger(__name__)

# Constantes de statuts pour les requêtes SQLAlchemy
_STATUTS_RESOLUS: list[str] = ["gagnant", "perdant", "gagne", "perdu"]
_STATUTS_GAGNANTS: list[str] = ["gagnant", "gagne"]


def _has_attr(model: type, attr: str) -> bool:
    """Compatibility helper for model field drift across refactors."""
    return hasattr(model, attr)


class StatsPersonnellesService:
    """
    Service d'analyse des performances personnelles.
    
    Fonctionnalités:
    - ROI global (Return on Investment)
    - Win rate par type de jeu
    - Meilleurs patterns (stratégies, types paris)
    - Évolution mensuelle
    - Analyse comparative
    """
    
    @avec_session_db
    def calculer_roi_global(self, user_id: int, jours: int = 30, session: Session | None = None) -> dict[str, Any]:
        """
        Calcule le ROI global sur tous les jeux.
        
        ROI = (Gains totaux - Mises totales) / Mises totales × 100
        
        Args:
            user_id: ID utilisateur
            jours: Période d'analyse (défaut: 30 jours)
            session: Session DB (injectée par décorateur)
        
        Returns:
            {
                "roi": float,  # Pourcentage
                "gains_totaux": float,
                "mises_totales": float,
                "benefice_net": float,
                "nb_paris": int,
                "nb_grilles": int
            }
        """
        logger.info(f"📊 Calcul ROI global pour user {user_id} sur {jours} jours")
        
        date_debut = datetime.now() - timedelta(days=jours)
        
        try:
            # Paris sportifs
            filtres_paris = []
            if _has_attr(PariSportif, "user_id"):
                filtres_paris.append(PariSportif.user_id == user_id)
            if _has_attr(PariSportif, "date_pari"):
                filtres_paris.append(PariSportif.date_pari >= date_debut)
            if _has_attr(PariSportif, "statut"):
                filtres_paris.append(PariSportif.statut.in_(["gagnant", "perdant", "gagne", "perdu"]))

            paris_query = session.query(PariSportif)
            if filtres_paris:
                paris_query = paris_query.filter(*filtres_paris)
            paris = paris_query.all()
            
            gains_paris = sum(float(p.gain) for p in paris if p.gain)
            mises_paris = sum(float(getattr(p, "mise", 0) or 0) for p in paris)
            
            # Loto
            filtres_loto = []
            if _has_attr(GrilleLoto, "user_id"):
                filtres_loto.append(GrilleLoto.user_id == user_id)
            if _has_attr(GrilleLoto, "date_creation"):
                filtres_loto.append(GrilleLoto.date_creation >= date_debut)
            if _has_attr(GrilleLoto, "statut"):
                filtres_loto.append(GrilleLoto.statut.in_(["gagnant", "perdant", "gagne", "perdu"]))
            grilles_loto_query = session.query(GrilleLoto)
            if filtres_loto:
                grilles_loto_query = grilles_loto_query.filter(*filtres_loto)
            grilles_loto = grilles_loto_query.all()
            
            gains_loto = sum(g.backtest.get("gain", 0) for g in grilles_loto if g.backtest)
            mises_loto = len(grilles_loto) * 2.2  # Prix 1 grille Loto
            
            # Euromillions
            filtres_euro = []
            if _has_attr(GrilleEuromillions, "user_id"):
                filtres_euro.append(GrilleEuromillions.user_id == user_id)
            if _has_attr(GrilleEuromillions, "date_creation"):
                filtres_euro.append(GrilleEuromillions.date_creation >= date_debut)
            if _has_attr(GrilleEuromillions, "statut"):
                filtres_euro.append(GrilleEuromillions.statut.in_(["gagnant", "perdant", "gagne", "perdu"]))
            grilles_euro_query = session.query(GrilleEuromillions)
            if filtres_euro:
                grilles_euro_query = grilles_euro_query.filter(*filtres_euro)
            grilles_euro = grilles_euro_query.all()
            
            gains_euro = sum(g.backtest.get("gain", 0) for g in grilles_euro if g.backtest)
            mises_euro = len(grilles_euro) * 2.5  # Prix 1 grille Euromillions
            
            # Agrégation
            gains_totaux = gains_paris + gains_loto + gains_euro
            mises_totales = mises_paris + mises_loto + mises_euro
            
            roi = get_bankroll_manager().calculer_roi(mises_totales, gains_totaux)
            
            benefice_net = gains_totaux - mises_totales
            
            result = {
                "roi": round(roi, 2),
                "gains_totaux": round(gains_totaux, 2),
                "mises_totales": round(mises_totales, 2),
                "benefice_net": round(benefice_net, 2),
                "nb_paris": len(paris),
                "nb_grilles": len(grilles_loto) + len(grilles_euro),
                "periode_jours": jours
            }
            
            logger.info(f"✅ ROI calculé: {roi:.2f}% (bénéfice {benefice_net:.2f}€)")
            return result
        
        except Exception as e:
            logger.error(f"❌ Erreur calcul ROI: {e}", exc_info=True)
            raise ErreurServiceIA(f"Échec calcul ROI: {e}")
    
    @avec_session_db
    def calculer_win_rate(self, user_id: int, jours: int = 30, session: Session | None = None) -> dict[str, Any]:
        """
        Calcule le win rate (taux de réussite) par type de jeu.
        
        Args:
            user_id: ID utilisateur
            jours: Période d'analyse
            session: Session DB
        
        Returns:
            {
                "win_rate_global": float,  # Pourcentage
                "win_rate_paris": float,
                "win_rate_loto": float,
                "win_rate_euromillions": float,
                "nb_gagnants": int,
                "nb_total": int
            }
        """
        logger.info(f"📈 Calcul win rate pour user {user_id}")
        
        date_debut = datetime.now() - timedelta(days=jours)
        
        try:
            # Paris
            filtres_paris = []
            if _has_attr(PariSportif, "user_id"):
                filtres_paris.append(PariSportif.user_id == user_id)
            if _has_attr(PariSportif, "date_pari"):
                filtres_paris.append(PariSportif.date_pari >= date_debut)

            paris_total_query = session.query(func.count(PariSportif.id))
            if filtres_paris:
                paris_total_query = paris_total_query.filter(*filtres_paris)
            if _has_attr(PariSportif, "statut"):
                paris_total_query = paris_total_query.filter(
                    PariSportif.statut.in_(_STATUTS_RESOLUS)
                )
            paris_total = paris_total_query.scalar() or 0

            paris_gagnants_query = session.query(func.count(PariSportif.id))
            if filtres_paris:
                paris_gagnants_query = paris_gagnants_query.filter(*filtres_paris)
            if _has_attr(PariSportif, "statut"):
                paris_gagnants_query = paris_gagnants_query.filter(
                    PariSportif.statut.in_(_STATUTS_GAGNANTS)
                )
            else:
                paris_gagnants_query = paris_gagnants_query.filter(PariSportif.gain.isnot(None))
            paris_gagnants = paris_gagnants_query.scalar() or 0
            
            # Loto
            filtres_loto = []
            if _has_attr(GrilleLoto, "user_id"):
                filtres_loto.append(GrilleLoto.user_id == user_id)
            if _has_attr(GrilleLoto, "date_creation"):
                filtres_loto.append(GrilleLoto.date_creation >= date_debut)

            loto_total_query = session.query(func.count(GrilleLoto.id))
            if filtres_loto:
                loto_total_query = loto_total_query.filter(*filtres_loto)
            if _has_attr(GrilleLoto, "statut"):
                loto_total_query = loto_total_query.filter(
                    GrilleLoto.statut.in_(_STATUTS_RESOLUS)
                )
            loto_total = loto_total_query.scalar() or 0

            loto_gagnants_query = session.query(func.count(GrilleLoto.id))
            if filtres_loto:
                loto_gagnants_query = loto_gagnants_query.filter(*filtres_loto)
            if _has_attr(GrilleLoto, "statut"):
                loto_gagnants_query = loto_gagnants_query.filter(
                    GrilleLoto.statut.in_(_STATUTS_GAGNANTS)
                )
            else:
                loto_gagnants_query = loto_gagnants_query.filter(GrilleLoto.gain.isnot(None))
            loto_gagnants = loto_gagnants_query.scalar() or 0
            
            # Euromillions
            filtres_euro = []
            if _has_attr(GrilleEuromillions, "user_id"):
                filtres_euro.append(GrilleEuromillions.user_id == user_id)
            if _has_attr(GrilleEuromillions, "date_creation"):
                filtres_euro.append(GrilleEuromillions.date_creation >= date_debut)

            euro_total_query = session.query(func.count(GrilleEuromillions.id))
            if filtres_euro:
                euro_total_query = euro_total_query.filter(*filtres_euro)
            if _has_attr(GrilleEuromillions, "statut"):
                euro_total_query = euro_total_query.filter(
                    GrilleEuromillions.statut.in_(_STATUTS_RESOLUS)
                )
            euro_total = euro_total_query.scalar() or 0

            euro_gagnants_query = session.query(func.count(GrilleEuromillions.id))
            if filtres_euro:
                euro_gagnants_query = euro_gagnants_query.filter(*filtres_euro)
            if _has_attr(GrilleEuromillions, "statut"):
                euro_gagnants_query = euro_gagnants_query.filter(
                    GrilleEuromillions.statut.in_(_STATUTS_GAGNANTS)
                )
            else:
                euro_gagnants_query = euro_gagnants_query.filter(GrilleEuromillions.gain.isnot(None))
            euro_gagnants = euro_gagnants_query.scalar() or 0
            
            # Calculs
            nb_total = paris_total + loto_total + euro_total
            nb_gagnants = paris_gagnants + loto_gagnants + euro_gagnants
            
            win_rate_global = (nb_gagnants / nb_total * 100) if nb_total > 0 else 0.0
            win_rate_paris = (paris_gagnants / paris_total * 100) if paris_total > 0 else 0.0
            win_rate_loto = (loto_gagnants / loto_total * 100) if loto_total > 0 else 0.0
            win_rate_euro = (euro_gagnants / euro_total * 100) if euro_total > 0 else 0.0
            
            result = {
                "win_rate_global": round(win_rate_global, 2),
                "win_rate_paris": round(win_rate_paris, 2),
                "win_rate_loto": round(win_rate_loto, 2),
                "win_rate_euromillions": round(win_rate_euro, 2),
                "nb_gagnants": nb_gagnants,
                "nb_total": nb_total,
                "periode_jours": jours
            }
            
            logger.info(f"✅ Win rate: {win_rate_global:.2f}% ({nb_gagnants}/{nb_total})")
            return result
        
        except Exception as e:
            logger.error(f"❌ Erreur calcul win rate: {e}", exc_info=True)
            raise ErreurServiceIA(f"Échec calcul win rate: {e}")
    
    @avec_session_db
    def analyser_patterns_gagnants(self, user_id: int, jours: int = 90, session: Session | None = None) -> dict[str, Any]:
        """
        Analyse les patterns les plus rentables.
        
        Args:
            user_id: ID utilisateur
            jours: Période d'analyse
            session: Session DB
        
        Returns:
            {
                "meilleur_type_pari": str,  # "1", "N", "2"
                "meilleure_strategie_loto": str,
                "meilleure_strategie_euro": str,
                "roi_par_type": dict,
                "recommandations": list[str]
            }
        """
        logger.info(f"🔍 Analyse patterns gagnants pour user {user_id}")
        
        date_debut = datetime.now() - timedelta(days=jours)
        
        try:
            # Paris sportifs par type
            types_paris = session.query(
                PariSportif.type_pari,
                func.count(PariSportif.id).label("nb"),
                func.sum(PariSportif.gain).label("gains"),
                func.sum(PariSportif.mise).label("mises")
            ).filter(
                PariSportif.user_id == user_id,
                PariSportif.date_pari >= date_debut,
                PariSportif.statut.in_(["gagnant", "perdant", "gagne", "perdu"])
            ).group_by(PariSportif.type_pari).all()
            
            roi_par_type = {}
            meilleur_type = None
            meilleur_roi = -100
            
            for type_pari, nb, gains, mises in types_paris:
                if mises and mises > 0:
                    roi = ((gains or 0) - mises) / mises * 100
                    roi_par_type[type_pari] = {"roi": round(roi, 2), "nb": nb}
                    
                    if roi > meilleur_roi:
                        meilleur_roi = roi
                        meilleur_type = type_pari
            
            # Stratégies Loto (skip gracieux si champs legacy absents)
            strategies_loto = []
            if all(_has_attr(GrilleLoto, attr) for attr in ("strategie", "backtest", "user_id", "date_creation")):
                loto_statut_filter = (
                    [GrilleLoto.statut.in_(["gagnant", "gagne"])] if _has_attr(GrilleLoto, "statut") else []
                )
                strategies_loto = session.query(
                    GrilleLoto.strategie,
                    func.count(GrilleLoto.id).label("nb"),
                    func.sum(func.cast(GrilleLoto.backtest["gain"].astext, float)).label("gains")
                ).filter(
                    GrilleLoto.user_id == user_id,
                    GrilleLoto.date_creation >= date_debut,
                    GrilleLoto.backtest.isnot(None),
                    *loto_statut_filter,
                ).group_by(GrilleLoto.strategie).all()
            
            meilleure_strat_loto = None
            max_gains_loto = 0
            
            for strat, nb, gains in strategies_loto:
                if gains and gains > max_gains_loto:
                    max_gains_loto = gains
                    meilleure_strat_loto = strat
            
            # Stratégies Euromillions (skip gracieux si champs legacy absents)
            strategies_euro = []
            if all(
                _has_attr(GrilleEuromillions, attr)
                for attr in ("strategie", "backtest", "user_id", "date_creation")
            ):
                euro_statut_filter = (
                    [GrilleEuromillions.statut.in_(["gagnant", "gagne"])] if _has_attr(GrilleEuromillions, "statut") else []
                )
                strategies_euro = session.query(
                    GrilleEuromillions.strategie,
                    func.count(GrilleEuromillions.id).label("nb"),
                    func.sum(func.cast(GrilleEuromillions.backtest["gain"].astext, float)).label("gains")
                ).filter(
                    GrilleEuromillions.user_id == user_id,
                    GrilleEuromillions.date_creation >= date_debut,
                    GrilleEuromillions.backtest.isnot(None),
                    *euro_statut_filter,
                ).group_by(GrilleEuromillions.strategie).all()
            
            meilleure_strat_euro = None
            max_gains_euro = 0
            
            for strat, nb, gains in strategies_euro:
                if gains and gains > max_gains_euro:
                    max_gains_euro = gains
                    meilleure_strat_euro = strat
            
            # Recommandations
            recommandations = []
            
            if meilleur_type:
                recommandations.append(
                    f"Prioriser les paris '{meilleur_type}' (ROI {meilleur_roi:.2f}%)"
                )
            
            if meilleure_strat_loto:
                recommandations.append(
                    f"Stratégie Loto la plus rentable: {meilleure_strat_loto}"
                )
            
            if meilleure_strat_euro:
                recommandations.append(
                    f"Stratégie Euromillions la plus rentable: {meilleure_strat_euro}"
                )
            
            result = {
                "meilleur_type_pari": meilleur_type,
                "meilleure_strategie_loto": meilleure_strat_loto,
                "meilleure_strategie_euro": meilleure_strat_euro,
                "roi_par_type": roi_par_type,
                "recommandations": recommandations,
                "periode_jours": jours
            }
            
            logger.info(f"✅ Patterns analysés: {len(recommandations)} recommandations")
            return result
        
        except Exception as e:
            logger.error(f"❌ Erreur analyse patterns: {e}", exc_info=True)
            raise ErreurServiceIA(f"Échec analyse patterns: {e}")
    
    @avec_session_db
    def obtenir_evolution_mensuelle(self, user_id: int, mois: int = 6, session: Session | None = None) -> dict[str, Any]:
        """
        Calcule l'évolution mensuelle du ROI et du bénéfice.
        
        Args:
            user_id: ID utilisateur
            mois: Nombre de mois à analyser
            session: Session DB
        
        Returns:
            {
                "evolution": [
                    {
                        "mois": "2024-01",
                        "roi": float,
                        "benefice": float,
                        "gains": float,
                        "mises": float
                    },
                    ...
                ]
            }
        """
        logger.info(f"📆 Calcul évolution mensuelle pour user {user_id}")
        
        evolution = []
        date_reference = datetime.now()
        
        try:
            for i in range(mois):
                # Calculer début/fin du mois
                mois_courant = date_reference.month - i
                annee_courante = date_reference.year
                
                while mois_courant <= 0:
                    mois_courant += 12
                    annee_courante -= 1
                
                date_debut = datetime(annee_courante, mois_courant, 1)
                
                # Fin du mois
                if mois_courant == 12:
                    date_fin = datetime(annee_courante + 1, 1, 1)
                else:
                    date_fin = datetime(annee_courante, mois_courant + 1, 1)
                
                # Calcul ROI pour ce mois
                paris = session.query(PariSportif).filter(
                    PariSportif.user_id == user_id,
                    PariSportif.date_pari >= date_debut,
                    PariSportif.date_pari < date_fin,
                    PariSportif.statut.in_(["gagnant", "perdant", "gagne", "perdu"])
                ).all()
                
                gains_paris = sum(p.gain for p in paris if p.gain)
                mises_paris = sum(p.mise for p in paris)
                
                # Loto
                filtres_loto = []
                if _has_attr(GrilleLoto, "user_id"):
                    filtres_loto.append(GrilleLoto.user_id == user_id)
                if _has_attr(GrilleLoto, "date_creation"):
                    filtres_loto.append(GrilleLoto.date_creation >= date_debut)
                    filtres_loto.append(GrilleLoto.date_creation < date_fin)
                if _has_attr(GrilleLoto, "statut"):
                    filtres_loto.append(GrilleLoto.statut.in_(["gagnant", "perdant", "gagne", "perdu"]))

                grilles_loto_query = session.query(GrilleLoto)
                if filtres_loto:
                    grilles_loto_query = grilles_loto_query.filter(*filtres_loto)
                grilles_loto = grilles_loto_query.all()
                
                gains_loto = sum(g.backtest.get("gain", 0) for g in grilles_loto if g.backtest)
                mises_loto = len(grilles_loto) * 2.2
                
                # Euromillions
                filtres_euro = []
                if _has_attr(GrilleEuromillions, "user_id"):
                    filtres_euro.append(GrilleEuromillions.user_id == user_id)
                if _has_attr(GrilleEuromillions, "date_creation"):
                    filtres_euro.append(GrilleEuromillions.date_creation >= date_debut)
                    filtres_euro.append(GrilleEuromillions.date_creation < date_fin)
                if _has_attr(GrilleEuromillions, "statut"):
                    filtres_euro.append(
                        GrilleEuromillions.statut.in_(["gagnant", "perdant", "gagne", "perdu"])
                    )

                grilles_euro_query = session.query(GrilleEuromillions)
                if filtres_euro:
                    grilles_euro_query = grilles_euro_query.filter(*filtres_euro)
                grilles_euro = grilles_euro_query.all()
                
                gains_euro = sum(g.backtest.get("gain", 0) for g in grilles_euro if g.backtest)
                mises_euro = len(grilles_euro) * 2.5
                
                # Totaux
                gains_total = gains_paris + gains_loto + gains_euro
                mises_total = mises_paris + mises_loto + mises_euro
                
                roi = obtenir_analytics().calculer_roi(mises_total, gains_total)
                benefice = gains_total - mises_total
                
                evolution.append({
                    "mois": f"{annee_courante}-{mois_courant:02d}",
                    "roi": round(roi, 2),
                    "benefice": round(benefice, 2),
                    "gains": round(gains_total, 2),
                    "mises": round(mises_total, 2)
                })
            
            # Inverser pour avoir ordre chronologique
            evolution.reverse()
            
            logger.info(f"✅ Évolution calculée pour {len(evolution)} mois")
            return {"evolution": evolution}
        
        except Exception as e:
            logger.error(f"❌ Erreur calcul évolution: {e}", exc_info=True)
            raise ErreurServiceIA(f"Échec calcul évolution: {e}")
