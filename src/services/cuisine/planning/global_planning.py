"""
Service Planning Unifié - Centre de Coordination Familiale

✅ Agrégation complète de TOUS les événements familiaux
✅ Utilise @avec_session_db, @avec_cache, décorateurs unifiés
✅ Cache agressif (TTL 30min) pour perfs
✅ IA intégrée pour générer semaines équilibrées
✅ Détection intelligente d'alertes (charge, couverture activités, budget)

Service complet pour le planning familial fusionnant :
- Planning repas (Planning + Repas)
- Activités famille (ActiviteFamille)
- Événements calendrier (EvenementPlanning)
- Projets domestiques (Projet + TacheProjet)
- Routines quotidiennes (Routine + TacheRoutine)
"""

import logging
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from src.core.ai import obtenir_client_ia
from src.core.caching import Cache
from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import EvenementPlanning
from src.services.core.base import BaseAIService, BaseService, PlanningAIMixin
from src.services.core.registry import service_factory

from .analysis import PlanningAnalysisMixin
from .loaders import PlanningLoadersMixin
from .types import JourCompletSchema, SemaineCompleSchema, SemaineGenereeIASchema

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SERVICE PLANNING UNIFIÉ
# ═══════════════════════════════════════════════════════════


class ServicePlanningUnifie(
    BaseService[EvenementPlanning],
    BaseAIService,
    PlanningAIMixin,
    PlanningLoadersMixin,
    PlanningAnalysisMixin,
):
    """
    Service unifié pour le planning familial.

    ✅ Héritage multiple :
    - BaseService → CRUD optimisé pour EvenementPlanning
    - BaseAIService → IA avec rate limiting auto
    - PlanningAIMixin → Contextes métier planning

    Fonctionnalités :
    - ✅ Agrégation complète (repas, activités, projets, routines, events)
    - ✅ Cache agressif (TTL 30min) invalidé intelligemment
    - ✅ Calcul charge familiale par jour
    - ✅ Détection alertes intelligentes
    - ✅ Génération IA avec contraintes familiales
    - ✅ Suggestions intelligentes basées sur contexte
    """

    def __init__(self):
        # Initialisation CRUD
        BaseService.__init__(self, EvenementPlanning, cache_ttl=1800)

        # Initialisation IA (rate limiting + cache auto)
        BaseAIService.__init__(
            self,
            client=obtenir_client_ia(),
            cache_prefix="planning",
            default_ttl=1800,
            default_temperature=0.6,  # Plus déterministe pour planning
            service_name="planning",
        )

    # ═══════════════════════════════════════════════════════════
    # SECTION 1: AGRÉGATION COMPLÈTE SEMAINE
    # ═══════════════════════════════════════════════════════════

    @avec_cache(
        ttl=1800,
        key_func=lambda self, date_debut, **kw: f"semaine_complete_{date_debut.isoformat()}",
    )
    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def get_semaine_complete(
        self, date_debut: date, db: Session | None = None
    ) -> SemaineCompleSchema | None:
        """
        Retourne TOUS les événements familiaux agrégés par jour.

        Args:
            date_debut: Premier jour de la semaine
            db: Session DB (injected)

        Returns:
            SemaineCompleSchema complète ou None
        """
        date_fin = date_debut + timedelta(days=6)

        # Charger TOUS les événements en parallèle (optimisé avec joinedload)
        repas_dict = self._charger_repas(date_debut, date_fin, db)
        activites_dict = self._charger_activites(date_debut, date_fin, db)
        projets_dict = self._charger_projets(date_debut, date_fin, db)
        routines_dict = self._charger_routines(db)
        events_dict = self._charger_events(date_debut, date_fin, db)

        # Construire vue par jour
        jours = {}
        for i in range(7):
            jour = date_debut + timedelta(days=i)
            jour_str = jour.isoformat()

            # Calcul charge et alertes
            charge_score = self._calculer_charge(
                repas=repas_dict.get(jour_str, []),
                activites=activites_dict.get(jour_str, []),
                projets=projets_dict.get(jour_str, []),
                routines=routines_dict.get(jour_str, []),
            )

            alertes = self._detecter_alertes(
                jour=jour,
                repas=repas_dict.get(jour_str, []),
                activites=activites_dict.get(jour_str, []),
                projets=projets_dict.get(jour_str, []),
                charge_score=charge_score,
            )

            jours[jour_str] = JourCompletSchema(
                date=jour,
                charge=self._score_to_charge(charge_score),
                charge_score=charge_score,
                repas=repas_dict.get(jour_str, []),
                activites=activites_dict.get(jour_str, []),
                projets=projets_dict.get(jour_str, []),
                routines=routines_dict.get(jour_str, []),
                events=events_dict.get(jour_str, []),
                budget_jour=self._calculer_budget_jour(
                    activites=activites_dict.get(jour_str, []),
                    projets=projets_dict.get(jour_str, []),
                ),
                alertes=alertes,
            )

        # Stats semaine globale
        stats = self._calculer_stats_semaine(jours)
        alertes_semaine = self._detecter_alertes_semaine(jours)

        # Charge globale
        charges = [j.charge_score for j in jours.values()]
        charge_moyenne = sum(charges) / len(charges) if charges else 0

        return SemaineCompleSchema(
            semaine_debut=date_debut,
            semaine_fin=date_fin,
            jours=jours,
            stats_semaine=stats,
            charge_globale=self._score_to_charge(int(charge_moyenne)),
            alertes_semaine=alertes_semaine,
        )

    # ═══════════════════════════════════════════════════════════
    # SECTION 4: GÉNÉRATION IA
    # ═══════════════════════════════════════════════════════════

    @avec_cache(
        ttl=1800, key_func=lambda self, date_debut, **kw: f"semaine_ia_{date_debut.isoformat()}"
    )
    @avec_gestion_erreurs(default_return=None)
    def generer_semaine_ia(
        self,
        date_debut: date,
        contraintes: dict | None = None,
        contexte: dict | None = None,
    ) -> SemaineGenereeIASchema | None:
        """
        Génère une semaine intelligente avec l'IA.

        Args:
            date_debut: Premier jour semaine
            contraintes: {"budget": 300, "energie": "faible", ...}
            contexte: {"jules_age_mois": 19, "objectifs_sante": [...], ...}

        Returns:
            SemaineGenereeIASchema avec propositions ou None
        """
        if not contraintes:
            contraintes = {}
        if not contexte:
            contexte = {}

        # Construire prompt contextuel
        prompt = self._construire_prompt_generation(date_debut, contraintes, contexte)

        # Appel IA
        response = self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=dict,  # Parser JSON directement
            system_prompt="Tu es un assistant de planification familiale expert. "
            "Tu dois générer des semaines équilibrées, inclusives et réalistes.",
        )

        if not response:
            logger.warning("❌ Génération IA échouée")
            return None

        return SemaineGenereeIASchema(**response[0]) if response else None

    def _construire_prompt_generation(
        self,
        date_debut: date,
        contraintes: dict,
        contexte: dict,
    ) -> str:
        """Construit prompt pour génération IA"""
        budget = contraintes.get("budget", 400)
        energie = contraintes.get("energie", "normal")
        # Défaut dynamique basé sur la date de naissance réelle
        from src.modules.famille.age_utils import get_age_jules_mois

        jules_mois = contexte.get("jules_age_mois", get_age_jules_mois())
        objectifs_sante = contexte.get("objectifs_sante", [])

        return f"""
        Génère un planning familial pour la semaine du {date_debut.isoformat()}.

        Contexte:
        - Jules a {jules_mois} mois
        - Budget semaine: {budget}€
        - Énergie famille: {energie}
        - Objectifs santé: {", ".join(objectifs_sante) if objectifs_sante else "Maintenir équilibre"}

        Retourne JSON avec:
        - repas_proposes: Liste repas (4 éléments)
        - activites_proposees: Liste activités adaptées Jules
        - projets_suggeres: Tâches maison prioritaires
        - harmonie_description: Une phrase sur l'équilibre
        - raisons: Justifications (liste)
        """

    # ═══════════════════════════════════════════════════════════
    # SECTION 5: CRUD ÉVÉNEMENTS CALENDRIER
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def creer_event(
        self,
        titre: str,
        date_debut: datetime,
        type_event: str = "autre",
        date_fin: datetime | None = None,
        description: str | None = None,
        lieu: str | None = None,
        couleur: str | None = None,
        db: Session | None = None,
    ) -> EvenementPlanning | None:
        """Crée un événement calendrier"""
        try:
            event = EvenementPlanning(
                titre=titre,
                date_debut=date_debut,
                date_fin=date_fin,
                type_event=type_event,
                description=description,
                lieu=lieu,
                couleur=couleur,
            )
            db.add(event)
            db.commit()

            # Invalider cache
            self._invalider_cache_semaine(date_debut.date())

            logger.info(f"✅ Événement créé: {titre}")
            return event
        except Exception as e:
            logger.error(f"❌ Erreur création événement: {e}")
            db.rollback()
            return None

    def _invalider_cache_semaine(self, date_jour: date) -> None:
        """Invalide cache pour la semaine contenant date_jour"""
        # Trouver début semaine (lundi)
        debut_semaine = date_jour - timedelta(days=date_jour.weekday())
        Cache.invalider(pattern=f"semaine_complete_{debut_semaine.isoformat()}")
        Cache.invalider(pattern=f"semaine_ia_{debut_semaine.isoformat()}")
        logger.debug(f"🔄 Cache semaine invalidé: {debut_semaine}")


# ═══════════════════════════════════════════════════════════
# FACTORIES
# ═══════════════════════════════════════════════════════════


@service_factory("planning_unifie", tags={"planning", "ia", "cuisine"})
def obtenir_service_planning_unifie() -> ServicePlanningUnifie:
    """Factory pour obtenir le service de planning unifié (repas + activités + projets)"""
    return ServicePlanningUnifie()


# Alias pour rétro-compatibilité
get_planning_unified_service = obtenir_service_planning_unifie
get_unified_planning_service = obtenir_service_planning_unifie


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════


__all__ = [
    # Classe principale
    "ServicePlanningUnifie",
    # Factories
    "obtenir_service_planning_unifie",
    "get_planning_unified_service",
    "get_unified_planning_service",
]
