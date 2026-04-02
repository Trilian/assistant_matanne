"""
Service Inter-Modules — Bridges entre modules.

Connecte les modules via l'event bus pour :
- B5.1: Récolte jardin → Recettes semaine suivante
- B5.2: Budget anomalie → Notification proactive
- B5.3: Documents expirés → Dashboard alerte
- B5.5: Entretien récurrent → Planning unifié
- B5.6: Voyages → Inventaire (déstockage)
- B5.7: Anniversaire proche → Suggestions cadeaux IA
- B5.8: Météo → Entretien maison
"""

import logging
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.events.bus import EvenementDomaine
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class BridgesInterModulesService:
    """Service de bridges inter-modules."""

    # ── B5.1: Récolte jardin → Suggestions recettes ────────

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def recolte_vers_recettes(self, element_nom: str, db: Session | None = None) -> list[dict]:
        """Cherche des recettes utilisant un ingrédient récolté au jardin.

        Args:
            element_nom: Nom de l'élément récolté (tomate, basilic, etc.)

        Returns:
            Liste de recettes correspondantes
        """
        from src.core.models.recettes import Recette, Ingredient

        recettes = (
            db.query(Recette)
            .join(Ingredient, Ingredient.recette_id == Recette.id)
            .filter(Ingredient.nom.ilike(f"%{element_nom}%"))
            .limit(10)
            .all()
        )

        return [
            {
                "id": r.id,
                "nom": r.nom,
                "description": r.description,
                "temps_total": r.temps_total,
            }
            for r in recettes
        ]

    # ── B5.3: Documents expirés → Dashboard alerte ─────────

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def documents_expires_alertes(self, jours_avant: int = 30, db: Session | None = None) -> list[dict]:
        """Liste les documents qui expirent bientôt ou sont déjà expirés.

        Args:
            jours_avant: Nombre de jours avant expiration pour alerter

        Returns:
            Liste de documents avec statut expiration
        """
        from src.core.models import DocumentFamille

        seuil = date.today() + timedelta(days=jours_avant)

        documents = (
            db.query(DocumentFamille)
            .filter(
                DocumentFamille.actif.is_(True),
                DocumentFamille.date_expiration.isnot(None),
                DocumentFamille.date_expiration <= seuil,
            )
            .order_by(DocumentFamille.date_expiration)
            .all()
        )

        return [
            {
                "id": d.id,
                "titre": d.titre,
                "categorie": d.categorie,
                "membre_famille": d.membre_famille,
                "date_expiration": str(d.date_expiration),
                "jours_restants": d.jours_avant_expiration,
                "est_expire": d.est_expire,
                "niveau": "critique" if d.est_expire else (
                    "urgent" if d.jours_avant_expiration and d.jours_avant_expiration <= 7 else "attention"
                ),
            }
            for d in documents
        ]

    # ── B5.5: Entretien récurrent → Planning unifié ─────────

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def entretien_planning_unifie(self, nb_jours: int = 7, db: Session | None = None) -> list[dict]:
        """Récupère les tâches d'entretien planifiées pour les N prochains jours.

        Returns:
            Liste de tâches avec dates et priorités
        """
        from src.core.models import TacheEntretien

        seuil = date.today() + timedelta(days=nb_jours)
        aujourd_hui = date.today()

        taches = (
            db.query(TacheEntretien)
            .filter(
                TacheEntretien.prochaine_fois <= seuil,
                TacheEntretien.fait.is_(False),
            )
            .order_by(TacheEntretien.prochaine_fois)
            .all()
        )

        return [
            {
                "id": t.id,
                "nom": t.nom,
                "prochaine_fois": str(t.prochaine_fois),
                "en_retard": t.prochaine_fois < aujourd_hui if t.prochaine_fois else False,
                "jours_restants": (t.prochaine_fois - aujourd_hui).days if t.prochaine_fois else None,
                "type": "entretien",
            }
            for t in taches
        ]

    # ── B5.2: Budget anomalie → Notification ────────────────

    def verifier_anomalies_budget_et_notifier(self) -> list[dict]:
        """Vérifie les anomalies budgétaires et émet des événements.

        Returns:
            Liste des anomalies détectées
        """
        from src.services.ia.prevision_budget import obtenir_service_prevision_budget
        from src.services.core.events import obtenir_bus

        service = obtenir_service_prevision_budget()
        anomalies = service.detecter_anomalies_budget(seuil_pct=80)

        bus = obtenir_bus()
        for anomalie in anomalies:
            bus.emettre("budget.depassement", {
                "categorie": anomalie["categorie"],
                "depense": anomalie["depense"],
                "budget_ref": anomalie["budget_ref"],
                "pourcentage": anomalie["pourcentage"],
                "niveau": anomalie["niveau"],
            })

        return anomalies

    # ── B5.8: Météo → Entretien maison ──────────────────────

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def meteo_vers_entretien(self, conditions_meteo: dict, db: Session | None = None) -> list[dict]:
        """Génère des alertes entretien basées sur les conditions météo.

        Args:
            conditions_meteo: Dict avec temperature, vent, precipitations

        Returns:
            Liste d'alertes avec conseils
        """
        alertes = []
        temp = conditions_meteo.get("temperature", 15)
        vent = conditions_meteo.get("vent_kmh", 0)
        pluie = conditions_meteo.get("precipitations_mm", 0)

        if temp <= 0:
            alertes.append({
                "type": "gel",
                "message": "🥶 Gel annoncé ! Protéger les plantes, purger les tuyaux extérieurs.",
                "priorite": "haute",
                "domaine": "jardin",
            })
        if temp >= 35:
            alertes.append({
                "type": "canicule",
                "message": "🌡️ Canicule ! Arroser le jardin tôt/tard, fermer les volets.",
                "priorite": "haute",
                "domaine": "jardin",
            })
        if vent >= 80:
            alertes.append({
                "type": "vent_fort",
                "message": "💨 Vent fort ! Rentrer les meubles de jardin, vérifier les fixations.",
                "priorite": "moyenne",
                "domaine": "exterieur",
            })
        if pluie >= 50:
            alertes.append({
                "type": "pluie_forte",
                "message": "🌧️ Pluie forte ! Vérifier les gouttières et évacuations.",
                "priorite": "moyenne",
                "domaine": "maison",
            })

        return alertes


# ═══════════════════════════════════════════════════════════
# EVENT HANDLERS (subscribers)
# ═══════════════════════════════════════════════════════════


def _on_jardin_recolte(event: EvenementDomaine) -> None:
    """Handler: Quand une récolte jardin est validée → suggérer des recettes."""
    try:
        nom = event.data.get("nom", "")
        if not nom:
            return

        service = obtenir_service_bridges()
        recettes = service.recolte_vers_recettes(nom)

        if recettes:
            logger.info(
                f"🌱→🍽️ Récolte '{nom}' → {len(recettes)} recette(s) trouvée(s): "
                f"{', '.join(r['nom'] for r in recettes[:3])}"
            )
            # Émettre un événement pour notification
            from src.services.core.events import obtenir_bus
            obtenir_bus().emettre("bridge.recolte_recettes", {
                "ingredient": nom,
                "recettes": recettes[:5],
                "nb_recettes": len(recettes),
            })
    except Exception as e:
        logger.warning(f"Erreur bridge récolte→recettes: {e}")


def _on_budget_modifie(event: EvenementDomaine) -> None:
    """Handler: Quand le budget est modifié → vérifier les anomalies."""
    try:
        service = obtenir_service_bridges()
        anomalies = service.verifier_anomalies_budget_et_notifier()
        if anomalies:
            logger.info(f"💰 {len(anomalies)} anomalie(s) budget détectée(s)")
    except Exception as e:
        logger.warning(f"Erreur bridge budget→notification: {e}")


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("bridges_inter_modules", tags={"bridges"})
def obtenir_service_bridges() -> BridgesInterModulesService:
    """Factory singleton."""
    return BridgesInterModulesService()


get_bridges_service = obtenir_service_bridges


def enregistrer_bridges_subscribers() -> None:
    """Enregistre tous les subscribers de bridges inter-modules dans le bus."""
    from src.services.core.events import obtenir_bus

    bus = obtenir_bus()
    bus.souscrire("jardin.recolte", _on_jardin_recolte)
    bus.souscrire("budget.modifie", _on_budget_modifie)

    logger.info("✅ Bridges inter-modules enregistrés (jardin→recettes, budget→notification)")
