"""
Service Planning Unifié - Centre de Coordination Familiale

✅ Agrégation complète de TOUS les événements familiaux
✅ Utilise @avec_session_db, @avec_cache, décorateurs unifiés
✅ Cache agressif (TTL 30min) pour perfs
✅ IA intégrée pour générer semaines équilibrées
✅ Détection intelligente d'alertes (charge, couverture activités, budget)

Service complet pour le planning familial fusionnant :
- Planning repas (Planning + Repas)
- Activités famille (FamilyActivity)
- Événements calendrier (CalendarEvent)
- Projets domestiques (Project + ProjectTask)
- Routines quotidiennes (Routine + RoutineTask)
"""

import logging
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from src.core.ai import obtenir_client_ia
from src.core.cache import Cache
from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import (
    CalendarEvent,
    FamilyActivity,
    Project,
    Recette,
    Repas,
    Routine,
    RoutineTask,
)
from src.services.base import BaseAIService, BaseService, PlanningAIMixin

from .types import JourCompletSchema, SemaineCompleSchema, SemaineGenereeIASchema

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SERVICE PLANNING UNIFIÉ
# ═══════════════════════════════════════════════════════════


class ServicePlanningUnifie(BaseService[CalendarEvent], BaseAIService, PlanningAIMixin):
    """
    Service unifié pour le planning familial.

    ✅ Héritage multiple :
    - BaseService → CRUD optimisé pour CalendarEvent
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
        BaseService.__init__(self, CalendarEvent, cache_ttl=1800)

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
    # SECTION 2: CHARGEMENT DONNÉES OPTIMISÉ
    # ═══════════════════════════════════════════════════════════

    def _charger_repas(
        self, date_debut: date, date_fin: date, db: Session
    ) -> dict[str, list[dict]]:
        """Charge repas planifiés avec recettes"""
        repas_dict = {}

        repas = (
            db.query(Repas, Recette)
            .outerjoin(Recette, Repas.recette_id == Recette.id)
            .filter(Repas.date_repas >= date_debut, Repas.date_repas <= date_fin)
            .all()
        )

        for meal, recipe in repas:
            jour_str = meal.date_repas.isoformat()
            if jour_str not in repas_dict:
                repas_dict[jour_str] = []

            repas_dict[jour_str].append(
                {
                    "id": meal.id,
                    "type": meal.type_repas,
                    "recette": recipe.nom if recipe else "Non défini",
                    "recette_id": recipe.id if recipe else None,
                    "portions": meal.portion_ajustee or (recipe.portions if recipe else 4),
                    "temps_total": (recipe.temps_preparation + recipe.temps_cuisson)
                    if recipe
                    else 0,
                    "notes": meal.notes,
                }
            )

        return repas_dict

    def _charger_activites(
        self, date_debut: date, date_fin: date, db: Session
    ) -> dict[str, list[dict]]:
        """Charge activités familiales"""
        activites_dict = {}

        activites = (
            db.query(FamilyActivity)
            .filter(
                FamilyActivity.date_prevue
                >= datetime.combine(date_debut, datetime.min.time()).date(),
                FamilyActivity.date_prevue
                <= datetime.combine(date_fin, datetime.max.time()).date(),
            )
            .all()
        )

        for act in activites:
            jour_str = act.date_prevue.isoformat()
            if jour_str not in activites_dict:
                activites_dict[jour_str] = []

            activites_dict[jour_str].append(
                {
                    "id": act.id,
                    "titre": act.titre,
                    "type": act.type_activite,
                    "debut": act.date_prevue,
                    "fin": act.date_prevue,  # FamilyActivity n'a pas de date_fin séparée
                    "lieu": act.lieu,
                    "budget": act.cout_estime or 0,
                    "duree": act.duree_heures or 0,
                }
            )

        return activites_dict

    def _charger_projets(
        self, date_debut: date, date_fin: date, db: Session
    ) -> dict[str, list[dict]]:
        """Charge projets avec tâches"""
        projets_dict = {}

        projets = (
            db.query(Project)
            .filter(
                Project.statut.in_(["à_faire", "en_cours"]),
                (Project.date_fin_prevue == None)
                | (Project.date_fin_prevue.between(date_debut, date_fin)),
            )
            .all()
        )

        for projet in projets:
            jour_str = (projet.date_fin_prevue or date_fin).isoformat()
            if jour_str not in projets_dict:
                projets_dict[jour_str] = []

            projets_dict[jour_str].append(
                {
                    "id": projet.id,
                    "nom": projet.nom,
                    "priorite": projet.priorite,
                    "statut": projet.statut,
                    "echéance": projet.date_fin_prevue,
                }
            )

        return projets_dict

    def _charger_routines(self, db: Session) -> dict[str, list[dict]]:
        """Charge routines quotidiennes actives"""
        routines_dict = {}

        routines = (
            db.query(RoutineTask, Routine)
            .join(Routine, RoutineTask.routine_id == Routine.id)
            .filter(Routine.actif == True)
            .all()
        )

        for task, routine in routines:
            jour_str = "routine_quotidienne"  # Les routines sont quotidiennes
            if jour_str not in routines_dict:
                routines_dict[jour_str] = []

            routines_dict[jour_str].append(
                {
                    "id": task.id,
                    "nom": task.nom,
                    "routine": routine.nom,
                    "heure": task.heure_prevue,
                    "fait": task.fait_le is not None,
                }
            )

        return routines_dict

    def _charger_events(
        self, date_debut: date, date_fin: date, db: Session
    ) -> dict[str, list[dict]]:
        """Charge événements calendrier"""
        events_dict = {}

        events = (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.date_debut >= datetime.combine(date_debut, datetime.min.time()),
                CalendarEvent.date_debut <= datetime.combine(date_fin, datetime.max.time()),
            )
            .all()
        )

        for event in events:
            jour_str = event.date_debut.date().isoformat()
            if jour_str not in events_dict:
                events_dict[jour_str] = []

            events_dict[jour_str].append(
                {
                    "id": event.id,
                    "titre": event.titre,
                    "type": event.type_event,
                    "debut": event.date_debut,
                    "fin": event.date_fin,
                    "lieu": event.lieu,
                    "couleur": event.couleur,
                }
            )

        return events_dict

    # ═══════════════════════════════════════════════════════════
    # SECTION 3: CALCUL CHARGE & DÉTECTION ALERTES
    # ═══════════════════════════════════════════════════════════

    def _calculer_charge(
        self,
        repas: list[dict],
        activites: list[dict],
        projets: list[dict],
        routines: list[dict],
    ) -> int:
        """Calcule score de charge (0-100) pour un jour"""
        score = 0

        # Repas complexes
        if repas:
            temps_total = sum(r.get("temps_total", 0) for r in repas)
            score += min(30, (temps_total // 30))  # Max 30 pts pour repas

        # Activités
        score += min(20, len(activites) * 10)  # Max 20 pts

        # Projets urgents
        score += min(25, len([p for p in projets if p.get("priorite") == "haute"]) * 15)

        # Routines nombreuses
        score += min(25, len(routines) * 5)

        return min(100, score)

    def _score_to_charge(self, score: int) -> str:
        """Convertit score numérique en label"""
        if score < 35:
            return "faible"
        elif score < 70:
            return "normal"
        else:
            return "intense"

    def _detecter_alertes(
        self,
        jour: date,
        repas: list[dict],
        activites: list[dict],
        projets: list[dict],
        charge_score: int,
    ) -> list[str]:
        """Détecte alertes intelligentes pour un jour"""
        alertes = []

        # Surcharge
        if charge_score >= 80:
            alertes.append("⚠️ Jour très chargé - Penser à prendre du temps")

        # Pas d'activité pour Jules
        if not any(a.get("pour_jules") for a in activites):
            alertes.append("👶 Pas d'activité prévue pour Jules")

        # Projets urgents sans tâches
        projets_urgents = [p for p in projets if p.get("priorite") == "haute"]
        if projets_urgents:
            alertes.append(f"🔴 {len(projets_urgents)} projet(s) urgent(s)")

        # Repas trop nombreux/complexes
        if len(repas) > 3:
            alertes.append(f"🍽️ {len(repas)} repas ce jour - Vérifier préparation")

        return alertes

    def _detecter_alertes_semaine(self, jours: dict[str, JourCompletSchema]) -> list[str]:
        """Détecte alertes pour la semaine globale"""
        alertes = []

        jours_list = list(jours.values())

        # Couverture activités Jules
        activites_jules = sum(
            sum(1 for a in j.activites if a.get("pour_jules")) for j in jours_list
        )
        if activites_jules == 0:
            alertes.append("👶 Aucune activité Jules cette semaine")
        elif activites_jules < 3:
            alertes.append("👶 Peu d'activités pour Jules (recommandé: 3+)")

        # Charge globale
        charges_intenses = sum(1 for j in jours_list if j.charge_score >= 80)
        if charges_intenses >= 3:
            alertes.append("⚠️ Plus de 3 jours très chargés - Risque burnout familial")

        # Budget
        budget_total = sum(j.budget_jour for j in jours_list)
        if budget_total > 500:  # Adapter à votre budget famille
            alertes.append(f"💰 Budget semaine: {budget_total:.2f}€ - Veiller au budget")

        return alertes

    def _calculer_budget_jour(self, activites: list[dict], projets: list[dict]) -> float:
        """Calcule budget estimé du jour"""
        return sum(a.get("budget") or 0 for a in activites)

    def _calculer_stats_semaine(self, jours: dict[str, JourCompletSchema]) -> dict:
        """Calcule stats globales semaine"""
        jours_list = list(jours.values())

        return {
            "total_repas": sum(len(j.repas) for j in jours_list),
            "total_activites": sum(len(j.activites) for j in jours_list),
            "activites_jules": sum(
                sum(1 for a in j.activites if a.get("pour_jules")) for j in jours_list
            ),
            "total_projets": sum(len(j.projets) for j in jours_list),
            "total_events": sum(len(j.events) for j in jours_list),
            "budget_total": sum(j.budget_jour for j in jours_list),
            "charge_moyenne": int(sum(j.charge_score for j in jours_list) / len(jours_list))
            if jours_list
            else 0,
        }

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
        semaine = date_debut.strftime("%W")
        budget = contraintes.get("budget", 400)
        energie = contraintes.get("energie", "normal")
        jules_mois = contexte.get("jules_age_mois", 19)
        objectifs_sante = contexte.get("objectifs_sante", [])

        return f"""
        Génère un planning familial pour la semaine du {date_debut.isoformat()}.

        Contexte:
        - Jules a {jules_mois} mois
        - Budget semaine: {budget}€
        - Énergie famille: {energie}
        - Objectifs santé: {', '.join(objectifs_sante) if objectifs_sante else 'Maintenir équilibre'}

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
    ) -> CalendarEvent | None:
        """Crée un événement calendrier"""
        try:
            event = CalendarEvent(
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
# ALIAS DE COMPATIBILITÉ
# ═══════════════════════════════════════════════════════════


# Alias pour rétro-compatibilité
PlanningAIService = ServicePlanningUnifie


# ═══════════════════════════════════════════════════════════
# FACTORIES
# ═══════════════════════════════════════════════════════════


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
    # Alias de compatibilité
    "PlanningAIService",
    # Factories
    "obtenir_service_planning_unifie",
    "get_planning_unified_service",
    "get_unified_planning_service",
]
