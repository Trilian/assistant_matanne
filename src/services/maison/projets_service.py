"""
Service Projets - Gestion intelligente des projets maison avec estimation IA.

Features:
- Estimation budget et matériaux par IA
- Suggestions de tâches ordonnées
- Pipeline automatique vers courses/budget
- Alternatives économiques suggérées
- Calcul ROI rénovations
"""

import logging
from decimal import Decimal

from sqlalchemy.orm import Session

from src.core.ai import ClientIA, obtenir_client_ia
from src.core.decorators import avec_cache, avec_session_db
from src.core.models import Projet
from src.services.core.base import BaseAIService
from src.services.core.events.bus import obtenir_bus
from src.services.core.registry import service_factory

from .schemas import (
    MaterielProjet,
    ProjetEstimation,
    TacheProjetCreate,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

CATEGORIES_PROJET = [
    "travaux",
    "renovation",
    "amenagement",
    "reparation",
    "decoration",
    "jardin",
    "exterieur",
]

PRIORITES = ["haute", "moyenne", "basse"]

MAGASINS_BRICOLAGE = [
    "Leroy Merlin",
    "Castorama",
    "Brico Dépôt",
    "Mr Bricolage",
    "Bricomarché",
]


# ═══════════════════════════════════════════════════════════
# SERVICE PROJETS
# ═══════════════════════════════════════════════════════════


class ProjetsService(BaseAIService):
    """Service IA pour la gestion intelligente des projets maison.

    Hérite de BaseAIService pour les appels IA. Les opérations CRUD DB
    sont gérées via @avec_session_db plutôt que BaseService[ProjetMaison] car :
    - Les méthodes CRUD sont spécifiques au domaine (pas de CRUD générique)
    - BaseAIService et BaseService[T] ont des constructeurs incompatibles
    - Le pattern @avec_session_db est cohérent avec le reste du service

    Fonctionnalités:
    - Analyse projet et estimation complète
    - Génération liste matériaux avec prix
    - Suggestions alternatives économiques
    - Pipeline vers module courses

    Example:
        >>> service = get_projets_service()
        >>> estimation = await service.estimer_projet("Repeindre chambre", "15m², 2 couches")
        >>> print(estimation.materiels_necessaires)
    """

    def __init__(self, client: ClientIA | None = None):
        """Initialise le service projets.

        Args:
            client: Client IA optionnel
        """
        if client is None:
            client = obtenir_client_ia()
        super().__init__(
            client=client,
            cache_prefix="projets",
            default_ttl=3600,
            service_name="projets",
        )

    # ─────────────────────────────────────────────────────────
    # ESTIMATION COMPLÈTE
    # ─────────────────────────────────────────────────────────

    async def estimer_projet(
        self, nom: str, description: str, categorie: str = "travaux"
    ) -> ProjetEstimation:
        """Estimation complète d'un projet par l'IA.

        Args:
            nom: Nom du projet
            description: Description détaillée
            categorie: Catégorie du projet

        Returns:
            ProjetEstimation avec budget, tâches, matériaux
        """
        prompt = f"""Analyse ce projet maison et fournis une estimation complète:

Projet: {nom}
Description: {description}
Catégorie: {categorie}

Génère en JSON:
{{
    "budget_min": 100,
    "budget_max": 200,
    "duree_jours": 2,
    "taches": [
        {{"nom": "Préparation", "ordre": 1, "duree_min": 60, "materiels": ["bâche"]}},
        ...
    ],
    "materiels": [
        {{"nom": "Peinture blanche 10L", "quantite": 2, "prix": 35, "magasin": "Leroy Merlin", "alternatif": "Marque distributeur 25€"}},
        ...
    ],
    "risques": ["Mauvaise préparation des murs", ...],
    "conseils": ["Bien protéger le sol", ...]
}}

Sois réaliste sur les prix (France 2026)."""

        try:
            response = await self.call_with_cache(
                prompt=prompt,
                system_prompt="Tu es entrepreneur en rénovation avec 20 ans d'expérience. Donne des estimations précises.",
                max_tokens=1200,
            )
            import json

            data = json.loads(response)

            # Parser les tâches
            taches = [
                TacheProjetCreate(
                    nom=t.get("nom", "Tâche"),
                    ordre=t.get("ordre", 0),
                    duree_estimee_min=t.get("duree_min"),
                    materiels_requis=t.get("materiels", []),
                )
                for t in data.get("taches", [])
            ]

            # Parser les matériaux
            materiels = [
                MaterielProjet(
                    nom=m.get("nom", "Matériel"),
                    quantite=m.get("quantite", 1),
                    prix_estime=Decimal(str(m.get("prix", 0))) if m.get("prix") else None,
                    magasin_suggere=m.get("magasin"),
                    alternatif_eco=m.get("alternatif"),
                )
                for m in data.get("materiels", [])
            ]

            return ProjetEstimation(
                nom_projet=nom,
                description_analysee=description,
                budget_estime_min=Decimal(str(data.get("budget_min", 50))),
                budget_estime_max=Decimal(str(data.get("budget_max", 100))),
                duree_estimee_jours=data.get("duree_jours", 1),
                taches_suggerees=taches,
                materiels_necessaires=materiels,
                risques_identifies=data.get("risques", []),
                conseils_ia=data.get("conseils", []),
            )

        except Exception as e:
            logger.warning(f"Estimation projet IA échouée: {e}")
            # Fallback minimal
            return ProjetEstimation(
                nom_projet=nom,
                description_analysee=description,
                budget_estime_min=Decimal("50"),
                budget_estime_max=Decimal("200"),
                duree_estimee_jours=2,
                taches_suggerees=[
                    TacheProjetCreate(nom="Préparation", ordre=1),
                    TacheProjetCreate(nom="Exécution", ordre=2),
                    TacheProjetCreate(nom="Finition", ordre=3),
                ],
                materiels_necessaires=[],
                risques_identifies=["Estimation automatique non disponible"],
                conseils_ia=["Demander un devis professionnel pour validation"],
            )

    async def suggerer_taches(self, nom_projet: str, description: str) -> str:
        """Suggère des tâches pour un projet.

        Args:
            nom_projet: Nom du projet
            description: Description du projet

        Returns:
            Texte avec tâches suggérées
        """
        prompt = f"""Pour le projet "{nom_projet}" : {description}
Suggère 5-7 tâches concrètes et numérotées. Ordonne par ordre logique.
Inclus le temps estimé pour chaque tâche."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en gestion de projets domestiques",
            max_tokens=700,
        )

    # ─────────────────────────────────────────────────────────
    # ESTIMATION BUDGET
    # ─────────────────────────────────────────────────────────

    async def estimer_budget(
        self, nom_projet: str, complexite: str = "moyen"
    ) -> dict[str, Decimal]:
        """Estime le budget d'un projet.

        Args:
            nom_projet: Nom du projet
            complexite: Niveau de complexité (simple, moyen, complexe)

        Returns:
            Dict avec budget min/max
        """
        prompt = f"""Pour un projet "{nom_projet}" de complexité {complexite}:
- Estime le budget matériaux (min-max)
- Estime le budget si fait par pro (min-max)

Format JSON: {{"materiaux_min": 100, "materiaux_max": 200, "pro_min": 500, "pro_max": 1000}}"""

        try:
            response = await self.call_with_cache(
                prompt=prompt,
                system_prompt="Tu es expert en estimation de coûts travaux",
                max_tokens=300,
            )
            import json

            data = json.loads(response)
            return {
                "materiaux_min": Decimal(str(data.get("materiaux_min", 50))),
                "materiaux_max": Decimal(str(data.get("materiaux_max", 200))),
                "pro_min": Decimal(str(data.get("pro_min", 300))),
                "pro_max": Decimal(str(data.get("pro_max", 800))),
            }
        except Exception as e:
            logger.warning(f"Estimation budget échouée: {e}")
            return {
                "materiaux_min": Decimal("50"),
                "materiaux_max": Decimal("200"),
                "pro_min": Decimal("300"),
                "pro_max": Decimal("800"),
            }

    async def suggerer_alternatives(self, materiels: list[MaterielProjet]) -> list[MaterielProjet]:
        """Suggère des alternatives économiques pour les matériaux.

        Args:
            materiels: Liste de matériaux originaux

        Returns:
            Liste de matériaux avec alternatives
        """
        if not materiels:
            return []

        materiels_txt = "\n".join(
            f"- {m.nom}: {m.prix_estime}€" for m in materiels if m.prix_estime
        )

        prompt = f"""Pour ces matériaux de bricolage:
{materiels_txt}

Suggère pour chaque une alternative moins chère mais de qualité acceptable.
Format JSON: [{{"original": "Nom", "alternatif": "Alternative", "prix_alternatif": 20}}]"""

        try:
            response = await self.call_with_cache(
                prompt=prompt,
                system_prompt="Tu es expert en matériaux de construction et rapport qualité/prix",
                max_tokens=600,
            )
            import json

            alternatives = json.loads(response)

            # Mettre à jour les matériels avec les alternatives
            for m in materiels:
                for alt in alternatives:
                    if m.nom in alt.get("original", ""):
                        m.alternatif_eco = alt.get("alternatif")
                        if alt.get("prix_alternatif"):
                            m.alternatif_prix = Decimal(str(alt["prix_alternatif"]))

            return materiels
        except Exception as e:
            logger.warning(f"Suggestion alternatives échouée: {e}")
            return materiels

    # ─────────────────────────────────────────────────────────
    # PRIORISATION & PLANIFICATION
    # ─────────────────────────────────────────────────────────

    async def prioriser_taches(self, nom_projet: str, taches: list[str]) -> list[str]:
        """Priorise les tâches d'un projet.

        Args:
            nom_projet: Nom du projet
            taches: Liste des tâches à prioriser

        Returns:
            Liste des tâches réordonnées
        """
        taches_txt = "\n".join(f"- {t}" for t in taches)

        prompt = f"""Pour le projet "{nom_projet}", réordonne ces tâches par priorité:
{taches_txt}

Critères: dépendances, criticité, ordre logique.
Explique brièvement l'ordre choisi."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en priorisation et planification",
            max_tokens=500,
        )

    async def identifier_risques(self, nom_projet: str, description: str) -> list[str]:
        """Identifie les risques potentiels d'un projet.

        Args:
            nom_projet: Nom du projet
            description: Description du projet

        Returns:
            Liste des risques identifiés
        """
        prompt = f"""Pour "{nom_projet}" : {description}
Identifie 3-5 risques/blocages principaux et comment les éviter.
Format liste."""

        response = await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en gestion de risques de projets",
            max_tokens=500,
        )

        # Parser la réponse en liste
        return [
            line.strip("- •").strip()
            for line in response.split("\n")
            if line.strip() and line.strip()[0] in "-•"
        ]

    # ─────────────────────────────────────────────────────────
    # ROI RÉNOVATIONS
    # ─────────────────────────────────────────────────────────

    async def calculer_roi(self, type_renovation: str, cout_estime: Decimal) -> dict[str, any]:
        """Calcule le ROI d'une rénovation énergétique.

        Args:
            type_renovation: Type (isolation, fenêtres, chaudière)
            cout_estime: Coût estimé du projet

        Returns:
            Dict avec économies annuelles et temps de retour
        """
        prompt = f"""Pour une rénovation "{type_renovation}" coûtant {cout_estime}€:
- Estime les économies d'énergie annuelles (€)
- Calcule le temps de retour sur investissement
- Indique les aides disponibles (MaPrimeRénov, CEE)

Format JSON: {{"economies_annuelles": 200, "retour_annees": 5, "aides_estimees": 500}}"""

        try:
            response = await self.call_with_cache(
                prompt=prompt,
                system_prompt="Tu es conseiller en rénovation énergétique certifié",
                max_tokens=400,
            )
            import json

            return json.loads(response)
        except Exception as e:
            logger.warning(f"Calcul ROI échoué: {e}")
            return {
                "economies_annuelles": 0,
                "retour_annees": None,
                "aides_estimees": 0,
            }

    # ─────────────────────────────────────────────────────────
    # ÉMISSION D'ÉVÉNEMENTS — Appelé par les modules après CRUD
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def emettre_modification(
        projet_id: int = 0,
        nom: str = "",
        action: str = "modifie",
    ) -> None:
        """Émet un événement projets.modifie pour déclencher l'invalidation de cache.

        Doit être appelé par les modules après ajout/modification/suppression
        d'un projet.

        Args:
            projet_id: ID du projet
            nom: Nom du projet
            action: "cree", "modifie", "archive", "tache_ajoutee"
        """
        obtenir_bus().emettre(
            "projets.modifie",
            {"projet_id": projet_id, "nom": nom, "action": action},
            source="projets",
        )

    # ─────────────────────────────────────────────────────────
    # CRUD HELPERS
    # ─────────────────────────────────────────────────────────

    @avec_cache(ttl=300)
    @avec_session_db
    def obtenir_projets(self, db: Session | None = None, statut: str | None = None) -> list[Projet]:
        """Récupère les projets.

        Args:
            db: Session DB (injectée automatiquement par @avec_session_db)
            statut: Filtrer par statut (en_cours, termine, etc.)

        Returns:
            Liste des projets
        """
        return self._query_projets(db, statut)

    def get_projets(self, db: Session | None = None, statut: str | None = None) -> list[Projet]:
        """Alias anglais pour obtenir_projets (rétrocompatibilité)."""
        return self.obtenir_projets(db, statut)

    def _query_projets(self, db: Session, statut: str | None = None) -> list[Projet]:
        """Query interne pour projets."""
        query = db.query(Projet)
        if statut:
            query = query.filter(Projet.statut == statut)
        return query.order_by(Projet.priorite.desc()).all()

    @avec_cache(ttl=300)
    @avec_session_db
    def obtenir_projets_urgents(self, db: Session | None = None) -> list[Projet]:
        """Récupère les projets urgents/prioritaires.

        Args:
            db: Session DB (injectée automatiquement par @avec_session_db)

        Returns:
            Liste des projets urgents
        """
        return self._query_projets_urgents(db)

    def get_projets_urgents(self, db: Session | None = None) -> list[Projet]:
        """Alias anglais pour obtenir_projets_urgents (rétrocompatibilité)."""
        return self.obtenir_projets_urgents(db)

    def _query_projets_urgents(self, db: Session) -> list[Projet]:
        """Query interne pour projets urgents."""
        return (
            db.query(Projet)
            .filter(
                Projet.statut == "en_cours",
                Projet.priorite == "haute",
            )
            .all()
        )


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def obtenir_service_projets(client: ClientIA | None = None) -> ProjetsService:
    """Factory pour obtenir le service projets (convention française).

    Args:
        client: Client IA optionnel

    Returns:
        Instance de ProjetsService
    """
    return ProjetsService(client=client)


@service_factory("projets", tags={"maison", "crud", "projets"})
def get_projets_service(client: ClientIA | None = None) -> ProjetsService:
    """Factory pour obtenir le service projets (alias anglais)."""
    return obtenir_service_projets(client)
