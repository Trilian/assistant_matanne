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
        # TODO: Implémenter avec modèle PlanJardin
        logger.info(f"Création plan jardin: {plan.nom} ({plan.largeur}x{plan.hauteur}m)")
        return 1  # Placeholder

    def obtenir_plan(self, plan_id: int, db: Session | None = None) -> dict | None:
        """Récupère un plan avec toutes ses zones et plantes.

        Args:
            plan_id: ID du plan
            db: Session DB optionnelle

        Returns:
            Dict avec plan, zones et plantes ou None
        """
        # TODO: Implémenter avec modèle PlanJardin
        return {
            "id": plan_id,
            "nom": "Mon Jardin",
            "largeur": 20,
            "hauteur": 15,
            "zones": [],
            "plantes": [],
        }

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
        # TODO: Implémenter avec modèle ZoneJardin
        logger.info(f"Ajout zone: {zone.nom} ({zone.type.value})")
        return 1  # Placeholder

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
        # TODO: Implémenter
        return True

    def supprimer_zone(self, zone_id: int, db: Session | None = None) -> bool:
        """Supprime une zone (et déplace ses plantes si possible).

        Args:
            zone_id: ID de la zone
            db: Session DB optionnelle

        Returns:
            True si supprimé avec succès
        """
        # TODO: Implémenter
        return True

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
        # TODO: Implémenter avec modèle PlanteJardin
        logger.info(f"Ajout plante: {plante.nom} à ({plante.position_x}, {plante.position_y})")
        return 1  # Placeholder

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
        # TODO: Implémenter
        return True

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
        # TODO: Implémenter
        return True

    def enregistrer_action(self, action: ActionPlanteCreate, db: Session | None = None) -> int:
        """Enregistre une action effectuée sur une plante.

        Args:
            action: Données de l'action (arrosage, récolte, traitement...)
            db: Session DB optionnelle

        Returns:
            ID de l'action créée
        """
        # TODO: Implémenter avec modèle ActionPlante
        logger.info(f"Action enregistrée: {action.type_action} sur plante {action.plante_id}")
        return 1  # Placeholder

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
        # TODO: Implémenter avec historique réel
        return [
            {"annee": 2024, "culture": "Tomates"},
            {"annee": 2023, "culture": "Courgettes"},
            {"annee": 2022, "culture": "Haricots"},
        ]

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
        # TODO: Implémenter avec données réelles
        # Simulation
        evenements = []

        if mois == 3:  # Mars
            evenements = [
                {"jour": 15, "type": "semis", "plante": "Tomates", "action": "Semis sous abri"},
                {"jour": 20, "type": "entretien", "plante": None, "action": "Préparation sol"},
            ]
        elif mois == 6:  # Juin
            evenements = [
                {"jour": 1, "type": "plantation", "plante": "Tomates", "action": "Repiquage"},
                {"jour": 15, "type": "semis", "plante": "Haricots", "action": "Semis direct"},
            ]
        elif mois == 8:  # Août
            evenements = [
                {"jour": 1, "type": "recolte", "plante": "Tomates", "action": "Récolte"},
                {"jour": 15, "type": "recolte", "plante": "Haricots", "action": "Récolte"},
            ]

        return evenements

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
        # TODO: Implémenter avec dates de plantation réelles
        return [
            {
                "semaine": 1,
                "plantes": ["Tomates cerises", "Courgettes"],
                "quantite_estimee": "2-3 kg",
            },
            {
                "semaine": 2,
                "plantes": ["Haricots verts", "Tomates"],
                "quantite_estimee": "1.5 kg",
            },
        ]

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
        # TODO: Implémenter avec données réelles
        return {
            "score": 0.7,
            "niveau": "optimal",
            "suggestions": [
                "Espace suffisant entre les plants",
                "Possibilité d'ajouter des aromatiques en bordure",
            ],
        }

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
        # TODO: Implémenter avec orientation réelle
        return {
            "heures_soleil": 6,
            "orientation": "Sud-Ouest",
            "ombre": False,
            "recommandations": [
                "Idéal pour tomates, poivrons",
                "Éviter les salades en été (trop de soleil)",
            ],
        }


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
