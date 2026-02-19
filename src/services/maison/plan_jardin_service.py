"""
Service Plan Jardin - Gestion du plan 2D avec zones et plantes.

Features:
- Zones définissables (potager, verger, pelouse, compost...)
- Positionnement des plantes avec coordonnées
- Vue temporelle (cycle de vie, récoltes)
- Conseils compagnonnage
- Rotation des cultures
"""

import logging
from typing import Any

from sqlalchemy.orm import Session

from src.core.ai import ClientIA
from src.services.core.base import BaseAIService

from .schemas import (
    ActionPlanteCreate,
    EtatPlante,
    PlanJardinCreate,
    PlanteJardinCreate,
    TypeZoneJardin,
    ZoneJardinCreate,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SERVICE PLAN JARDIN
# ═══════════════════════════════════════════════════════════


class PlanJardinService(BaseAIService):
    """Service pour la gestion du plan jardin 2D.

    Fonctionnalités:
    - Création/modification zones
    - Positionnement plantes
    - Conseils compagnonnage IA
    - Suivi rotation cultures
    - Vue temporelle

    Example:
        >>> service = get_plan_jardin_service()
        >>> plan = service.creer_plan(PlanJardinCreate(nom="Mon Jardin", largeur=20, hauteur=15))
        >>> zone = service.ajouter_zone(ZoneJardinCreate(nom="Potager", type=TypeZoneJardin.POTAGER, ...))
    """

    def __init__(self, client: ClientIA | None = None):
        """Initialise le service plan jardin.

        Args:
            client: Client IA optionnel
        """
        if client is None:
            client = ClientIA()
        super().__init__(
            client=client,
            cache_prefix="plan_jardin",
            default_ttl=3600,
            service_name="plan_jardin",
        )

    # ─────────────────────────────────────────────────────────
    # GESTION DU PLAN
    # ─────────────────────────────────────────────────────────

    def creer_plan(self, plan: PlanJardinCreate, db: Session | None = None) -> int:
        """Crée un nouveau plan de jardin.

        Args:
            plan: Données du plan
            db: Session DB optionnelle

        Returns:
            ID du plan créé
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import PlanJardin

        def _impl(session: Session) -> int:
            plan_db = PlanJardin(
                nom=plan.nom,
                largeur=plan.largeur,
                hauteur=plan.hauteur,
                description=plan.description,
            )
            session.add(plan_db)
            session.commit()
            logger.info(
                f"Plan jardin créé: {plan.nom} ({plan.largeur}x{plan.hauteur}m, ID={plan_db.id})"
            )
            return plan_db.id

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    def obtenir_plan(self, plan_id: int, db: Session | None = None) -> dict | None:
        """Récupère un plan avec toutes ses zones et plantes.

        Args:
            plan_id: ID du plan
            db: Session DB optionnelle

        Returns:
            Dict avec plan, zones et plantes ou None
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import PlanJardin, PlanteJardin, ZoneJardin

        def _impl(session: Session) -> dict | None:
            plan = session.query(PlanJardin).filter(PlanJardin.id == plan_id).first()
            if not plan:
                return None

            # Récupérer les zones liées à ce plan
            zones = session.query(ZoneJardin).filter(ZoneJardin.plan_id == plan_id).all()

            # Récupérer toutes les plantes de ces zones
            zone_ids = [z.id for z in zones]
            plantes = []
            if zone_ids:
                plantes = (
                    session.query(PlanteJardin).filter(PlanteJardin.zone_id.in_(zone_ids)).all()
                )

            return {
                "id": plan.id,
                "nom": plan.nom,
                "largeur": float(plan.largeur),
                "hauteur": float(plan.hauteur),
                "description": plan.description,
                "zones": [
                    {
                        "id": z.id,
                        "nom": z.nom,
                        "type_zone": z.type_zone,
                        "superficie_m2": float(z.superficie_m2) if z.superficie_m2 else None,
                        "exposition": z.exposition,
                    }
                    for z in zones
                ],
                "plantes": [
                    {
                        "id": p.id,
                        "nom": p.nom,
                        "zone_id": p.zone_id,
                        "position_x": float(p.position_x) if p.position_x else None,
                        "position_y": float(p.position_y) if p.position_y else None,
                        "etat": p.etat,
                    }
                    for p in plantes
                ],
            }

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    def exporter_plan_svg(self, plan_id: int, db: Session | None = None) -> str:
        """Exporte le plan en SVG pour affichage.

        Args:
            plan_id: ID du plan
            db: Session DB optionnelle

        Returns:
            Code SVG du plan
        """
        plan = self.obtenir_plan(plan_id, db)
        if not plan:
            return ""

        largeur = plan.get("largeur", 20) * 50  # 50px par mètre
        hauteur = plan.get("hauteur", 15) * 50

        svg = f"""<svg width="{largeur}" height="{hauteur}" viewBox="0 0 {largeur} {hauteur}">
  <rect width="100%" height="100%" fill="#90EE90"/>
  <!-- Zones et plantes à ajouter dynamiquement -->
  <text x="10" y="30" fill="#333">Plan: {plan.get("nom", "Jardin")}</text>
</svg>"""

        return svg

    # ─────────────────────────────────────────────────────────
    # GESTION DES ZONES
    # ─────────────────────────────────────────────────────────

    def ajouter_zone(self, zone: ZoneJardinCreate, db: Session | None = None) -> int:
        """Ajoute une zone au plan.

        Args:
            zone: Données de la zone
            db: Session DB optionnelle

        Returns:
            ID de la zone créée
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import ZoneJardin

        def _impl(session: Session) -> int:
            zone_db = ZoneJardin(
                nom=zone.nom,
                type_zone=zone.type_zone.value,
                superficie_m2=zone.superficie_m2,
                exposition=zone.exposition,
                type_sol=zone.type_sol,
                arrosage_auto=zone.arrosage_auto,
                description=zone.notes,
            )
            session.add(zone_db)
            session.commit()
            logger.info(f"Zone ajoutée: {zone.nom} ({zone.type_zone.value}, ID={zone_db.id})")
            return zone_db.id

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    def modifier_zone(
        self,
        zone_id: int,
        updates: dict[str, Any],
        db: Session | None = None,
    ) -> bool:
        """Modifie une zone existante.

        Args:
            zone_id: ID de la zone
            updates: Champs à mettre à jour
            db: Session DB optionnelle

        Returns:
            True si modifié avec succès
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import ZoneJardin

        def _impl(session: Session) -> bool:
            zone = session.query(ZoneJardin).filter(ZoneJardin.id == zone_id).first()
            if not zone:
                logger.warning(f"Zone {zone_id} non trouvée")
                return False

            for key, value in updates.items():
                if hasattr(zone, key):
                    # Convertir les enums si nécessaire
                    if key == "type_zone" and hasattr(value, "value"):
                        value = value.value
                    setattr(zone, key, value)

            session.commit()
            logger.info(f"Zone {zone_id} modifiée")
            return True

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    def supprimer_zone(self, zone_id: int, db: Session | None = None) -> bool:
        """Supprime une zone (et déplace ses plantes si possible).

        Args:
            zone_id: ID de la zone
            db: Session DB optionnelle

        Returns:
            True si supprimé avec succès
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import ZoneJardin

        def _impl(session: Session) -> bool:
            zone = session.query(ZoneJardin).filter(ZoneJardin.id == zone_id).first()
            if not zone:
                logger.warning(f"Zone {zone_id} non trouvée")
                return False

            # Supprimer la zone (les plantes seront supprimées en cascade)
            session.delete(zone)
            session.commit()
            logger.info(f"Zone {zone_id} supprimée")
            return True

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    def obtenir_couleur_zone(self, type_zone: TypeZoneJardin) -> str:
        """Retourne la couleur pour un type de zone.

        Args:
            type_zone: Type de zone

        Returns:
            Code couleur hexadécimal
        """
        couleurs = {
            TypeZoneJardin.POTAGER: "#8B4513",  # Marron (terre)
            TypeZoneJardin.VERGER: "#228B22",  # Vert forêt
            TypeZoneJardin.PELOUSE: "#90EE90",  # Vert clair
            TypeZoneJardin.FLEURS: "#FF69B4",  # Rose
            TypeZoneJardin.AROMATIQUES: "#9ACD32",  # Vert jaune
            TypeZoneJardin.COMPOST: "#654321",  # Brun foncé
            TypeZoneJardin.SERRE: "#ADD8E6",  # Bleu clair (verre)
            TypeZoneJardin.ABRI: "#A0522D",  # Sienna
            TypeZoneJardin.TERRASSE: "#D2B48C",  # Tan
            TypeZoneJardin.BASSIN: "#4169E1",  # Bleu royal
        }
        return couleurs.get(type_zone, "#CCCCCC")

    # ─────────────────────────────────────────────────────────
    # GESTION DES PLANTES
    # ─────────────────────────────────────────────────────────

    def ajouter_plante(self, plante: PlanteJardinCreate, db: Session | None = None) -> int:
        """Ajoute une plante dans une zone.

        Args:
            plante: Données de la plante
            db: Session DB optionnelle

        Returns:
            ID de la plante créée
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import PlanteJardin

        def _impl(session: Session) -> int:
            plante_db = PlanteJardin(
                zone_id=plante.zone_id,
                nom=plante.nom,
                variete=plante.variete,
                position_x=plante.position_x,
                position_y=plante.position_y,
                date_plantation=plante.date_plantation,
                etat=plante.etat.value if hasattr(plante.etat, "value") else plante.etat,
                notes=plante.notes,
            )
            session.add(plante_db)
            session.commit()
            logger.info(
                f"Plante ajoutée: {plante.nom} à ({plante.position_x}, {plante.position_y}, ID={plante_db.id})"
            )
            return plante_db.id

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    def deplacer_plante(
        self,
        plante_id: int,
        nouvelle_pos_x: float,
        nouvelle_pos_y: float,
        db: Session | None = None,
    ) -> bool:
        """Déplace une plante sur le plan.

        Args:
            plante_id: ID de la plante
            nouvelle_pos_x: Nouvelle position X
            nouvelle_pos_y: Nouvelle position Y
            db: Session DB optionnelle

        Returns:
            True si déplacé avec succès
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import PlanteJardin

        def _impl(session: Session) -> bool:
            plante = session.query(PlanteJardin).filter(PlanteJardin.id == plante_id).first()
            if not plante:
                logger.warning(f"Plante {plante_id} non trouvée")
                return False

            plante.position_x = nouvelle_pos_x
            plante.position_y = nouvelle_pos_y
            session.commit()
            logger.info(f"Plante {plante_id} déplacée vers ({nouvelle_pos_x}, {nouvelle_pos_y})")
            return True

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    def mettre_a_jour_etat(
        self,
        plante_id: int,
        nouvel_etat: EtatPlante,
        db: Session | None = None,
    ) -> bool:
        """Met à jour l'état d'une plante.

        Args:
            plante_id: ID de la plante
            nouvel_etat: Nouvel état
            db: Session DB optionnelle

        Returns:
            True si mis à jour avec succès
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import PlanteJardin

        def _impl(session: Session) -> bool:
            plante = session.query(PlanteJardin).filter(PlanteJardin.id == plante_id).first()
            if not plante:
                logger.warning(f"Plante {plante_id} non trouvée")
                return False

            plante.etat = nouvel_etat.value if hasattr(nouvel_etat, "value") else nouvel_etat
            session.commit()
            logger.info(f"Plante {plante_id} état mis à jour: {nouvel_etat}")
            return True

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    def enregistrer_action(self, action: ActionPlanteCreate, db: Session | None = None) -> int:
        """Enregistre une action effectuée sur une plante.

        Args:
            action: Données de l'action (arrosage, récolte, traitement...)
            db: Session DB optionnelle

        Returns:
            ID de l'action créée
        """
        from datetime import date

        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import ActionPlante

        def _impl(session: Session) -> int:
            action_db = ActionPlante(
                plante_id=action.plante_id,
                type_action=action.type_action,
                date_action=action.date_action or date.today(),
                quantite=action.quantite,
                notes=action.notes,
            )
            session.add(action_db)
            session.commit()
            logger.info(
                f"Action enregistrée: {action.type_action} sur plante {action.plante_id} (ID={action_db.id})"
            )
            return action_db.id

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    # ─────────────────────────────────────────────────────────
    # COMPAGNONNAGE IA
    # ─────────────────────────────────────────────────────────

    async def verifier_compagnonnage(
        self,
        plante_nom: str,
        voisins: list[str],
    ) -> dict[str, str]:
        """Vérifie la compatibilité avec les plantes voisines.

        Args:
            plante_nom: Nom de la plante à placer
            voisins: Noms des plantes voisines

        Returns:
            Dict avec compatibilité par voisin
        """
        if not voisins:
            return {}

        prompt = f"""Compatibilité compagnonnage pour "{plante_nom}" avec:
{", ".join(voisins)}

Pour chaque voisin, indique: bon, neutre, ou mauvais.
Format JSON: {{"tomate": "bon", "fenouil": "mauvais"}}"""

        try:
            response = await self.call_with_cache(
                prompt=prompt,
                system_prompt="Tu es expert en permaculture et compagnonnage des plantes",
                max_tokens=300,
            )
            import json

            return json.loads(response)
        except Exception as e:
            logger.warning(f"Vérification compagnonnage échouée: {e}")
            return dict.fromkeys(voisins, "neutre")

    async def suggerer_compagnons(self, plante_nom: str) -> list[str]:
        """Suggère des plantes compagnes idéales.

        Args:
            plante_nom: Nom de la plante

        Returns:
            Liste des compagnons recommandés
        """
        prompt = f"""Quelles plantes sont les meilleures compagnes pour "{plante_nom}"?
Liste les 5 meilleures associations avec une brève raison.
Format JSON: ["tomate - aide à repousser les pucerons", ...]"""

        try:
            response = await self.call_with_cache(
                prompt=prompt,
                system_prompt="Tu es expert en permaculture",
                max_tokens=300,
            )
            import json

            return json.loads(response)
        except Exception as e:
            logger.warning(f"Suggestion compagnons échouée: {e}")
            return []

    # ─────────────────────────────────────────────────────────
    # ROTATION DES CULTURES
    # ─────────────────────────────────────────────────────────

    def obtenir_historique_zone(
        self,
        zone_id: int,
        annees: int = 3,
        db: Session | None = None,
    ) -> list[dict]:
        """Récupère l'historique des cultures d'une zone.

        Args:
            zone_id: ID de la zone
            annees: Nombre d'années d'historique
            db: Session DB optionnelle

        Returns:
            Liste des cultures par année
        """
        from datetime import date

        from sqlalchemy import extract, func

        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import ActionPlante, PlanteJardin

        def _impl(session: Session) -> list[dict]:
            annee_courante = date.today().year
            annee_min = annee_courante - annees

            # Récupérer les récoltes groupées par année
            resultats = (
                session.query(
                    extract("year", ActionPlante.date_action).label("annee"),
                    PlanteJardin.nom,
                    func.sum(ActionPlante.quantite).label("quantite_totale"),
                )
                .join(PlanteJardin, ActionPlante.plante_id == PlanteJardin.id)
                .filter(PlanteJardin.zone_id == zone_id)
                .filter(ActionPlante.type_action == "recolte")
                .filter(extract("year", ActionPlante.date_action) >= annee_min)
                .group_by(extract("year", ActionPlante.date_action), PlanteJardin.nom)
                .order_by(extract("year", ActionPlante.date_action).desc())
                .all()
            )

            # Grouper par année
            historique_par_annee: dict[int, list[str]] = {}
            for annee, nom_plante, _ in resultats:
                annee_int = int(annee)
                if annee_int not in historique_par_annee:
                    historique_par_annee[annee_int] = []
                if nom_plante not in historique_par_annee[annee_int]:
                    historique_par_annee[annee_int].append(nom_plante)

            return [
                {"annee": annee, "culture": ", ".join(cultures)}
                for annee, cultures in sorted(historique_par_annee.items(), reverse=True)
            ]

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    async def suggerer_rotation(
        self,
        zone_id: int,
        db: Session | None = None,
    ) -> list[str]:
        """Suggère les cultures pour l'année suivante.

        Args:
            zone_id: ID de la zone
            db: Session DB optionnelle

        Returns:
            Liste des cultures suggérées
        """
        historique = self.obtenir_historique_zone(zone_id, db=db)

        if not historique:
            return ["Commencer par des légumineuses pour enrichir le sol"]

        cultures_passees = [h["culture"] for h in historique[:3]]

        prompt = f"""Historique de rotation de cette parcelle:
{", ".join(cultures_passees)} (du plus récent au plus ancien)

Suggère 3 cultures pour l'année suivante en respectant la rotation:
- Éviter la même famille botanique 2 ans de suite
- Alterner légumes-feuilles, légumes-fruits, légumineuses, racines
Format JSON: ["suggestion1", "suggestion2", "suggestion3"]"""

        try:
            response = await self.call_with_cache(
                prompt=prompt,
                system_prompt="Tu es expert en maraîchage et rotation des cultures",
                max_tokens=200,
            )
            import json

            return json.loads(response)
        except Exception as e:
            logger.warning(f"Suggestion rotation échouée: {e}")
            return ["Légumineuses (haricots, pois)", "Légumes-feuilles (salades)"]

    # ─────────────────────────────────────────────────────────
    # VUE TEMPORELLE
    # ─────────────────────────────────────────────────────────

    def obtenir_calendrier_zone(
        self,
        zone_id: int,
        mois: int,
        db: Session | None = None,
    ) -> list[dict]:
        """Récupère le calendrier d'une zone pour un mois.

        Args:
            zone_id: ID de la zone
            mois: Numéro du mois (1-12)
            db: Session DB optionnelle

        Returns:
            Liste des événements (semis, récoltes, entretien)
        """
        import json

        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import PlanteJardin

        def _impl(session: Session) -> list[dict]:
            plantes = session.query(PlanteJardin).filter(PlanteJardin.zone_id == zone_id).all()

            evenements = []
            for plante in plantes:
                # Vérifier semis
                if plante.mois_semis:
                    try:
                        mois_semis = json.loads(plante.mois_semis)
                        if mois in mois_semis:
                            evenements.append(
                                {
                                    "jour": 1,
                                    "type": "semis",
                                    "plante": plante.nom,
                                    "action": f"Période de semis pour {plante.nom}",
                                }
                            )
                    except (json.JSONDecodeError, TypeError):
                        pass

                # Vérifier récolte
                if plante.mois_recolte:
                    try:
                        mois_recolte = json.loads(plante.mois_recolte)
                        if mois in mois_recolte:
                            evenements.append(
                                {
                                    "jour": 15,
                                    "type": "recolte",
                                    "plante": plante.nom,
                                    "action": f"Période de récolte pour {plante.nom}",
                                }
                            )
                    except (json.JSONDecodeError, TypeError):
                        pass

            return sorted(evenements, key=lambda x: x["jour"])

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    def prevoir_recoltes(
        self,
        plan_id: int,
        nb_semaines: int = 4,
        db: Session | None = None,
    ) -> list[dict]:
        """Prévoit les récoltes à venir.

        Args:
            plan_id: ID du plan
            nb_semaines: Nombre de semaines de prévision
            db: Session DB optionnelle

        Returns:
            Liste des récoltes prévues
        """
        import json
        from datetime import date, timedelta

        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import PlanteJardin, ZoneJardin

        def _impl(session: Session) -> list[dict]:
            # Récupérer les plantes du plan
            zones = session.query(ZoneJardin).filter(ZoneJardin.plan_id == plan_id).all()
            zone_ids = [z.id for z in zones]

            if not zone_ids:
                return []

            plantes = session.query(PlanteJardin).filter(PlanteJardin.zone_id.in_(zone_ids)).all()

            aujourd_hui = date.today()
            mois_courant = aujourd_hui.month

            # Prévisions par semaine
            previsions = []
            for semaine in range(1, nb_semaines + 1):
                date_semaine = aujourd_hui + timedelta(weeks=semaine)
                mois_semaine = date_semaine.month

                plantes_recolte = []
                for plante in plantes:
                    if plante.mois_recolte:
                        try:
                            mois_recolte = json.loads(plante.mois_recolte)
                            if mois_semaine in mois_recolte:
                                plantes_recolte.append(plante.nom)
                        except (json.JSONDecodeError, TypeError):
                            pass

                if plantes_recolte:
                    previsions.append(
                        {
                            "semaine": semaine,
                            "plantes": plantes_recolte,
                            "quantite_estimee": f"{len(plantes_recolte) * 0.5}-{len(plantes_recolte)} kg",
                        }
                    )

            return previsions

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    # ─────────────────────────────────────────────────────────
    # ANALYSE ESPACE
    # ─────────────────────────────────────────────────────────

    async def analyser_densite(
        self,
        zone_id: int,
        db: Session | None = None,
    ) -> dict:
        """Analyse la densité de plantation d'une zone.

        Args:
            zone_id: ID de la zone
            db: Session DB optionnelle

        Returns:
            Analyse avec score et suggestions
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import PlanteJardin, ZoneJardin

        def _impl(session: Session) -> dict:
            zone = session.query(ZoneJardin).filter(ZoneJardin.id == zone_id).first()
            if not zone:
                return {"score": 0, "niveau": "inconnu", "suggestions": ["Zone non trouvée"]}

            plantes = session.query(PlanteJardin).filter(PlanteJardin.zone_id == zone_id).all()
            nb_plantes = len(plantes)
            superficie = float(zone.superficie_m2) if zone.superficie_m2 else 10.0

            # Calcul de densité (plantes par m²)
            densite = nb_plantes / superficie if superficie > 0 else 0

            # Évaluation
            if densite < 0.5:
                score = 0.4
                niveau = "faible"
                suggestions = [
                    "Zone peu plantée - espace disponible pour plus de cultures",
                    "Envisagez d'ajouter des plantes compagnes",
                ]
            elif densite < 2:
                score = 0.8
                niveau = "optimal"
                suggestions = [
                    "Densité idéale pour la plupart des cultures",
                    "Possibilité d'ajouter des aromatiques en bordure",
                ]
            else:
                score = 0.5
                niveau = "dense"
                suggestions = [
                    "Zone très dense - surveiller la ventilation",
                    "Risque de maladies par manque d'aération",
                ]

            return {
                "score": score,
                "niveau": niveau,
                "densite_m2": round(densite, 2),
                "nb_plantes": nb_plantes,
                "superficie_m2": superficie,
                "suggestions": suggestions,
            }

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    async def calculer_exposition(
        self,
        zone_id: int,
        db: Session | None = None,
    ) -> dict:
        """Calcule l'exposition solaire d'une zone.

        Args:
            zone_id: ID de la zone
            db: Session DB optionnelle

        Returns:
            Dict avec heures de soleil et recommandations
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import ZoneJardin

        # Mapping exposition -> heures de soleil estimées
        exposition_heures = {
            "S": 8,
            "SO": 7,
            "SE": 7,
            "O": 5,
            "E": 5,
            "NO": 4,
            "NE": 4,
            "N": 3,
        }

        def _impl(session: Session) -> dict:
            zone = session.query(ZoneJardin).filter(ZoneJardin.id == zone_id).first()
            if not zone:
                return {
                    "heures_soleil": 0,
                    "orientation": "Inconnue",
                    "ombre": True,
                    "recommandations": ["Zone non trouvée"],
                }

            orientation = zone.exposition or "S"  # Défaut Sud
            orientation_upper = orientation.upper().replace(" ", "")
            heures = exposition_heures.get(orientation_upper, 5)
            ombre = heures < 5

            # Recommandations basées sur l'exposition
            if heures >= 7:
                recommandations = [
                    "Idéal pour tomates, poivrons, aubergines",
                    "Parfait pour les légumes-fruits",
                    "Éviter les salades en plein été (trop de soleil)",
                ]
            elif heures >= 5:
                recommandations = [
                    "Bon pour la plupart des légumes",
                    "Convient aux haricots, pois, choux",
                ]
            else:
                recommandations = [
                    "Zone ombragée - privilégier les légumes-feuilles",
                    "Idéal pour salades, épinards, oseille",
                    "Les aromatiques (persil, ciboulette) peuvent s'y plaire",
                ]

            return {
                "heures_soleil": heures,
                "orientation": orientation,
                "ombre": ombre,
                "recommandations": recommandations,
            }

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def obtenir_service_plan_jardin(client: ClientIA | None = None) -> PlanJardinService:
    """Factory pour obtenir le service plan jardin (convention française).

    Args:
        client: Client IA optionnel

    Returns:
        Instance de PlanJardinService
    """
    return PlanJardinService(client=client)


def get_plan_jardin_service(client: ClientIA | None = None) -> PlanJardinService:
    """Factory pour obtenir le service plan jardin (alias anglais)."""
    return obtenir_service_plan_jardin(client)
