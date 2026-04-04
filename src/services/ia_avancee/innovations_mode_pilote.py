"""Fonctions mode pilote extraites du service innovations."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from src.core.db import obtenir_contexte_db

from .innovations_types import ActionPiloteAutomatique, ModePiloteAutomatiqueResponse, SuggestionRepasSoirResponse

logger = logging.getLogger(__name__)


def normaliser_niveau_autonomie(niveau: str | None) -> str:
    """Normalise le niveau d'autonomie du mode pilote."""
    if not niveau:
        return "validation_requise"
    niveau_norm = niveau.strip().lower()
    niveaux_valides = {"off", "proposee", "validation_requise", "semi_auto", "auto"}
    if niveau_norm not in niveaux_valides:
        return "validation_requise"
    return niveau_norm


def lire_config_mode_pilote(service: Any, user_id: int | None) -> tuple[bool, str]:
    """Lit la configuration du mode pilote depuis les préférences profil."""
    if not user_id:
        return True, "validation_requise"

    try:
        with obtenir_contexte_db() as session:
            from src.core.models.users import ProfilUtilisateur

            profil = session.get(ProfilUtilisateur, user_id)
            if not profil:
                return True, "validation_requise"

            preferences = dict(profil.preferences_modules or {})
            innovations = dict(preferences.get("innovations") or {})
            mode_pilote = dict(innovations.get("mode_pilote") or {})

            actif = bool(mode_pilote.get("actif", True))
            niveau = normaliser_niveau_autonomie(mode_pilote.get("niveau_autonomie"))
            return actif, niveau
    except Exception:
        logger.warning("Lecture config mode pilote impossible", exc_info=True)
        return True, "validation_requise"


def configurer_mode_pilote_automatique(
    service: Any,
    user_id: int | None,
    actif: bool,
    niveau_autonomie: str = "validation_requise",
) -> ModePiloteAutomatiqueResponse | None:
    """Active/desactive le mode pilote et persiste la configuration utilisateur."""
    if not user_id:
        return service.obtenir_mode_pilote_automatique(user_id=None)

    niveau_normalise = normaliser_niveau_autonomie(niveau_autonomie)

    try:
        with obtenir_contexte_db() as session:
            from src.core.models.users import ProfilUtilisateur

            profil = session.get(ProfilUtilisateur, user_id)
            if not profil:
                return service.obtenir_mode_pilote_automatique(user_id=None)

            preferences = dict(profil.preferences_modules or {})
            innovations = dict(preferences.get("innovations") or {})
            innovations["mode_pilote"] = {
                "actif": bool(actif),
                "niveau_autonomie": niveau_normalise,
                "updated_at": datetime.now(UTC).isoformat(),
            }
            preferences["innovations"] = innovations
            profil.preferences_modules = preferences
            session.add(profil)
            session.commit()
    except Exception:
        logger.warning("Ecriture config mode pilote impossible", exc_info=True)

    return service.obtenir_mode_pilote_automatique(user_id=user_id)


def obtenir_mode_pilote_automatique(service: Any, user_id: int | None = None) -> ModePiloteAutomatiqueResponse | None:
    """Mode pilote automatique (propositions + validations)."""
    actif, niveau_autonomie = lire_config_mode_pilote(service, user_id)
    if not actif:
        return ModePiloteAutomatiqueResponse(
            actif=False,
            niveau_autonomie="off",
            actions=[],
            recommandations=[
                "Mode pilote desactive. Activez-le pour recevoir des propositions IA automatiques.",
            ],
        )

    actions: list[ActionPiloteAutomatique] = []

    try:
        with obtenir_contexte_db() as session:
            from sqlalchemy import func
            from src.core.models import ArticleCourses, ListeCourses, Planning, Repas
            from src.core.models.famille import Routine

            planning_actif = session.query(Planning).filter(Planning.statut == "actif").first()
            nb_repas = 0
            if planning_actif:
                nb_repas = int(
                    session.query(func.count(Repas.id)).filter(Repas.planning_id == planning_actif.id).scalar() or 0
                )
            if nb_repas < 14:
                actions.append(
                    ActionPiloteAutomatique(
                        module="planning",
                        action="proposer_generation_planning",
                        statut="validation_requise",
                        details="Planning incomplet : generation d'une semaine equilibree proposee.",
                    )
                )

            liste = (
                session.query(ListeCourses)
                .filter(ListeCourses.archivee.is_(False))
                .order_by(ListeCourses.id.desc())
                .first()
            )
            if liste:
                nb_articles = int(
                    session.query(func.count(ArticleCourses.id))
                    .filter(ArticleCourses.liste_id == liste.id, ArticleCourses.coche.is_(False))
                    .scalar() or 0
                )
                if nb_articles < 8:
                    actions.append(
                        ActionPiloteAutomatique(
                            module="courses",
                            action="proposer_complement_liste",
                            statut="validation_requise",
                            details="Liste de courses courte : suggestion de complement depuis historique.",
                        )
                    )

            routines = session.query(Routine).filter(Routine.actif.is_(True)).all()
            if not routines:
                actions.append(
                    ActionPiloteAutomatique(
                        module="routines",
                        action="activer_routines_defaut",
                        statut="proposee",
                        details="Aucune routine active detectee.",
                    )
                )
    except Exception:
        logger.warning("Mode pilote automatique partiel", exc_info=True)

    return ModePiloteAutomatiqueResponse(
        actif=True,
        niveau_autonomie=niveau_autonomie,
        actions=actions,
        recommandations=[
            "Valider les actions proposees pour activer l'automatisation complete.",
            "Configurer une plage horaire de pilotage (soir 20h recommande).",
        ],
    )


def proposer_repas_adapte_garmin(service: Any, user_id: int | None = None) -> SuggestionRepasSoirResponse | None:
    """Adapte la proposition de repas selon la depense Garmin du jour."""
    calories_brulees = 0
    try:
        with obtenir_contexte_db() as session:
            from src.core.models import Recette
            from src.core.models.users import ProfilUtilisateur, ResumeQuotidienGarmin

            profil_id = user_id
            if not profil_id:
                profil = session.query(ProfilUtilisateur).order_by(ProfilUtilisateur.id.asc()).first()
                profil_id = profil.id if profil else None

            if profil_id:
                resume = (
                    session.query(ResumeQuotidienGarmin)
                    .filter(ResumeQuotidienGarmin.user_id == profil_id)
                    .order_by(ResumeQuotidienGarmin.date.desc())
                    .first()
                )
                if resume:
                    calories_brulees = int(resume.calories_actives or 0)

            if calories_brulees >= 600:
                cible_max = 850
                strategie = "recharge"
            elif calories_brulees >= 350:
                cible_max = 700
                strategie = "equilibre"
            else:
                cible_max = 550
                strategie = "leger"

            recettes = (
                session.query(Recette)
                .filter(Recette.calories.isnot(None), Recette.calories <= cible_max)
                .order_by(Recette.calories.desc())
                .limit(4)
                .all()
            )
            if not recettes:
                return service.suggerer_repas_ce_soir(temps_disponible_min=30, humeur="equilibre")

            recette_principale = recettes[0]
            alternatives = [r.nom for r in recettes[1:4]]
            return SuggestionRepasSoirResponse(
                recette_suggeree=recette_principale.nom,
                raison=(
                    f"Strategie {strategie} selon Garmin ({calories_brulees} kcal actives) "
                    f"avec cible <= {cible_max} kcal."
                ),
                temps_total_estime_min=int(
                    (recette_principale.temps_preparation or 0) + (recette_principale.temps_cuisson or 0)
                ),
                alternatives=alternatives,
            )
    except Exception:
        logger.warning("Recommandation repas Garmin indisponible", exc_info=True)
        return service.suggerer_repas_ce_soir(temps_disponible_min=25, humeur="rapide")
