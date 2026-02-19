"""
Assistant IA Maison - Orchestrateur intelligent pour la gestion maison.

Features:
- Briefing quotidien personnalisé
- Alertes proactives (météo, entretien, budget)
- Réponses contextuelles aux questions
- Coordination des services maison
"""

import logging
from datetime import date, datetime
from typing import Any

from sqlalchemy.orm import Session

from src.core.ai import ClientIA
from src.services.core.base import BaseAIService

from .schemas import (
    AlerteMaison,
    BriefingMaison,
    NiveauUrgence,
    TypeAlerteMaison,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# ASSISTANT IA MAISON
# ═══════════════════════════════════════════════════════════


class MaisonAssistantIA(BaseAIService):
    """Assistant IA orchestrant tous les services maison.

    L'assistant coordonne:
    - EntretienService pour les tâches ménagères
    - JardinService pour le jardin et météo
    - ProjetsService pour les travaux
    - EnergieService pour la consommation
    - InventaireMaisonService pour la recherche d'objets

    Example:
        >>> assistant = get_maison_assistant()
        >>> briefing = await assistant.generer_briefing_quotidien()
        >>> print(briefing.resume)
    """

    def __init__(self, client: ClientIA | None = None):
        """Initialise l'assistant maison.

        Args:
            client: Client IA optionnel
        """
        if client is None:
            client = ClientIA()
        super().__init__(
            client=client,
            cache_prefix="maison_assistant",
            default_ttl=1800,  # 30 min TTL
            service_name="maison_assistant",
        )

        # Services délégués (chargés paresseusement)
        self._entretien_service = None
        self._jardin_service = None
        self._projets_service = None
        self._energie_service = None
        self._inventaire_service = None
        self._plan_jardin_service = None

    # ─────────────────────────────────────────────────────────
    # ACCÈS PARESSEUX AUX SERVICES
    # ─────────────────────────────────────────────────────────

    @property
    def entretien(self):
        """Service entretien (lazy load)."""
        if self._entretien_service is None:
            from .entretien_service import get_entretien_service

            self._entretien_service = get_entretien_service(self.client)
        return self._entretien_service

    @property
    def jardin(self):
        """Service jardin (lazy load)."""
        if self._jardin_service is None:
            from .jardin_service import get_jardin_service

            self._jardin_service = get_jardin_service(self.client)
        return self._jardin_service

    @property
    def projets(self):
        """Service projets (lazy load)."""
        if self._projets_service is None:
            from .projets_service import get_projets_service

            self._projets_service = get_projets_service(self.client)
        return self._projets_service

    @property
    def energie(self):
        """Service énergie (lazy load)."""
        if self._energie_service is None:
            from .energie_service import get_energie_service

            self._energie_service = get_energie_service(self.client)
        return self._energie_service

    @property
    def inventaire(self):
        """Service inventaire (lazy load)."""
        if self._inventaire_service is None:
            from .inventaire_service import get_inventaire_service

            self._inventaire_service = get_inventaire_service(self.client)
        return self._inventaire_service

    @property
    def plan_jardin(self):
        """Service plan jardin (lazy load)."""
        if self._plan_jardin_service is None:
            from .plan_jardin_service import get_plan_jardin_service

            self._plan_jardin_service = get_plan_jardin_service(self.client)
        return self._plan_jardin_service

    # ─────────────────────────────────────────────────────────
    # BRIEFING QUOTIDIEN
    # ─────────────────────────────────────────────────────────

    async def generer_briefing_quotidien(self, db: Session | None = None) -> BriefingMaison:
        """Génère le briefing quotidien de la maison.

        Agrège:
        - Tâches ménagères du jour
        - Alertes météo jardin
        - Projets en cours
        - Consommation énergie
        - Rappels importants

        Args:
            db: Session DB optionnelle

        Returns:
            BriefingMaison complet
        """
        logger.info("Génération briefing quotidien maison")

        # Collecter les données de chaque service
        taches = await self._collecter_taches_jour(db)
        alertes = await self._collecter_alertes(db)
        meteo = await self._collecter_meteo()
        projets = await self._collecter_projets_actifs(db)

        # Générer un résumé IA personnalisé
        resume = await self._generer_resume_ia(
            taches=taches,
            alertes=alertes,
            meteo=meteo,
            projets=projets,
        )

        # Suggérer les priorités
        priorites = self._calculer_priorites(taches, alertes)

        return BriefingMaison(
            date=date.today(),
            resume=resume,
            taches_jour=taches,
            alertes=alertes,
            meteo_impact=meteo,
            projets_actifs=[p.get("nom", "") for p in projets],
            priorites=priorites,
        )

    async def _collecter_taches_jour(self, db: Session | None) -> list[str]:
        """Collecte les tâches du jour depuis EntretienService."""
        try:
            # TODO: Appeler entretien.obtenir_taches_jour(db)
            # Simulation pour l'instant
            return [
                "Passer l'aspirateur (salon, chambres)",
                "Arroser les plantes d'intérieur",
                "Sortir les poubelles recyclage",
            ]
        except Exception as e:
            logger.warning(f"Erreur collecte tâches: {e}")
            return []

    async def _collecter_alertes(self, db: Session | None) -> list[AlerteMaison]:
        """Collecte les alertes de tous les services."""
        alertes = []

        try:
            # Alertes entretien (tâches en retard)
            # TODO: Implémenter avec données réelles
            alertes.append(
                AlerteMaison(
                    type=TypeAlerteMaison.ENTRETIEN,
                    niveau=NiveauUrgence.MOYENNE,
                    titre="Nettoyage filtres VMC",
                    message="Prévu il y a 5 jours, à faire cette semaine",
                    action_suggeree="Planifier 30min ce weekend",
                )
            )

            # Alertes jardin (météo)
            # TODO: Intégrer avec service météo réel
            alertes.append(
                AlerteMaison(
                    type=TypeAlerteMaison.METEO,
                    niveau=NiveauUrgence.HAUTE,
                    titre="Gel nocturne prévu",
                    message="Températures négatives cette nuit",
                    action_suggeree="Protéger les plantes sensibles",
                )
            )

        except Exception as e:
            logger.warning(f"Erreur collecte alertes: {e}")

        return alertes

    async def _collecter_meteo(self) -> str:
        """Collecte les informations météo pertinentes."""
        try:
            # TODO: Intégrer avec ServiceMeteo
            return "Ensoleillé, 18°C, risque de gel cette nuit (-2°C)"
        except Exception as e:
            logger.warning(f"Erreur collecte météo: {e}")
            return "Météo indisponible"

    async def _collecter_projets_actifs(self, db: Session | None) -> list[dict]:
        """Collecte les projets en cours."""
        try:
            # TODO: Appeler projets.obtenir_projets_actifs(db)
            return [
                {"nom": "Peinture chambre", "avancement": 60},
                {"nom": "Installation étagères", "avancement": 20},
            ]
        except Exception as e:
            logger.warning(f"Erreur collecte projets: {e}")
            return []

    async def _generer_resume_ia(
        self,
        taches: list[str],
        alertes: list[AlerteMaison],
        meteo: str,
        projets: list[dict],
    ) -> str:
        """Génère un résumé personnalisé avec l'IA."""
        nb_taches = len(taches)
        nb_alertes = len(
            [a for a in alertes if a.niveau in [NiveauUrgence.HAUTE, NiveauUrgence.CRITIQUE]]
        )
        nb_projets = len(projets)

        prompt = f"""Génère un briefing maison court et actionnable:
- {nb_taches} tâches aujourd'hui
- {nb_alertes} alertes importantes
- Météo: {meteo}
- {nb_projets} projets en cours

Style: Direct, pratique, encourageant. 2-3 phrases max."""

        try:
            return await self.call_with_cache(
                prompt=prompt,
                system_prompt="Tu es un assistant maison efficace et bienveillant",
                max_tokens=150,
            )
        except Exception as e:
            logger.warning(f"Génération résumé IA échouée: {e}")
            return f"Aujourd'hui: {nb_taches} tâches, {nb_alertes} alertes. Météo: {meteo}"

    def _calculer_priorites(
        self,
        taches: list[str],
        alertes: list[AlerteMaison],
    ) -> list[str]:
        """Calcule les priorités du jour."""
        priorites = []

        # Alertes critiques/hautes d'abord
        for alerte in alertes:
            if alerte.niveau in [NiveauUrgence.CRITIQUE, NiveauUrgence.HAUTE]:
                priorites.append(alerte.action_suggeree or alerte.titre)

        # Puis les tâches (max 3)
        priorites.extend(taches[:3])

        return priorites[:5]  # Max 5 priorités

    # ─────────────────────────────────────────────────────────
    # QUESTIONS CONTEXTUELLES
    # ─────────────────────────────────────────────────────────

    async def repondre_question(
        self,
        question: str,
        db: Session | None = None,
    ) -> str:
        """Répond à une question sur la maison.

        Détecte le contexte et délègue au service approprié:
        - "Où est..." → InventaireMaisonService
        - "Comment entretenir..." → EntretienService
        - "Quand planter..." → JardinService
        - etc.

        Args:
            question: Question utilisateur
            db: Session DB optionnelle

        Returns:
            Réponse contextualisée
        """
        question_lower = question.lower()

        # Détection du contexte
        if any(mot in question_lower for mot in ["où est", "où se trouve", "cherche"]):
            # Recherche inventaire
            objet = self._extraire_objet_recherche(question)
            result = await self.inventaire.rechercher(objet, db)
            if result:
                return f"🔍 **{result.objet_trouve}** est dans: {result.emplacement}"
            return f"❓ Je n'ai pas trouvé '{objet}' dans l'inventaire."

        elif any(mot in question_lower for mot in ["arroser", "planter", "jardin", "plante"]):
            # Question jardin
            return await self._repondre_jardin(question)

        elif any(mot in question_lower for mot in ["nettoyer", "entretien", "ménage"]):
            # Question entretien
            return await self._repondre_entretien(question)

        elif any(mot in question_lower for mot in ["projet", "travaux", "rénovation"]):
            # Question projets
            return await self._repondre_projets(question)

        elif any(mot in question_lower for mot in ["énergie", "électricité", "consommation"]):
            # Question énergie
            return await self._repondre_energie(question)

        else:
            # Question générale → IA
            return await self._repondre_general(question)

    def _extraire_objet_recherche(self, question: str) -> str:
        """Extrait l'objet recherché d'une question."""
        mots_ignorés = [
            "où",
            "est",
            "se",
            "trouve",
            "mon",
            "ma",
            "mes",
            "le",
            "la",
            "les",
            "cherche",
        ]
        mots = question.lower().replace("?", "").split()
        mots_filtres = [m for m in mots if m not in mots_ignorés]
        return " ".join(mots_filtres)

    async def _repondre_jardin(self, question: str) -> str:
        """Répond à une question jardin."""
        prompt = f"Question jardin: {question}\nRéponds de façon pratique et concise."
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en jardinage amateur",
            max_tokens=300,
        )

    async def _repondre_entretien(self, question: str) -> str:
        """Répond à une question entretien."""
        prompt = f"Question entretien maison: {question}\nDonne des conseils pratiques."
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en entretien domestique",
            max_tokens=300,
        )

    async def _repondre_projets(self, question: str) -> str:
        """Répond à une question projets/travaux."""
        prompt = f"Question bricolage/travaux: {question}\nConseils pour un bricoleur amateur."
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en bricolage et rénovation",
            max_tokens=300,
        )

    async def _repondre_energie(self, question: str) -> str:
        """Répond à une question énergie."""
        prompt = f"Question économies d'énergie: {question}\nConseils éco-responsables pratiques."
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en efficacité énergétique domestique",
            max_tokens=300,
        )

    async def _repondre_general(self, question: str) -> str:
        """Répond à une question générale maison."""
        prompt = f"Question maison: {question}\nRéponds de façon utile et pratique."
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es un assistant maison polyvalent",
            max_tokens=300,
        )

    # ─────────────────────────────────────────────────────────
    # RECOMMANDATIONS PROACTIVES
    # ─────────────────────────────────────────────────────────

    async def generer_recommandations(
        self,
        contexte: dict[str, Any] | None = None,
        db: Session | None = None,
    ) -> list[str]:
        """Génère des recommandations proactives.

        Args:
            contexte: Contexte additionnel (saison, événements...)
            db: Session DB optionnelle

        Returns:
            Liste de recommandations
        """
        mois = datetime.now().month
        saison = self._obtenir_saison(mois)

        prompt = f"""Donne 3 recommandations proactives pour une maison en {saison}:
- Entretien préventif
- Économies d'énergie
- Jardin/extérieur

Format: Liste courte et actionnable."""

        try:
            response = await self.call_with_cache(
                prompt=prompt,
                system_prompt="Tu es expert en gestion domestique",
                max_tokens=300,
            )
            # Parser la réponse en liste
            return [line.strip("- ").strip() for line in response.split("\n") if line.strip()]
        except Exception as e:
            logger.warning(f"Génération recommandations échouée: {e}")
            return [
                f"Vérifier les équipements saisonniers ({saison})",
                "Contrôler la consommation d'énergie",
                "Planifier l'entretien préventif",
            ]

    def _obtenir_saison(self, mois: int) -> str:
        """Détermine la saison en fonction du mois."""
        if mois in [3, 4, 5]:
            return "printemps"
        elif mois in [6, 7, 8]:
            return "été"
        elif mois in [9, 10, 11]:
            return "automne"
        else:
            return "hiver"

    # ─────────────────────────────────────────────────────────
    # PLANIFICATION AUTOMATIQUE
    # ─────────────────────────────────────────────────────────

    async def planifier_semaine(
        self,
        preferences: dict[str, Any] | None = None,
        db: Session | None = None,
    ) -> dict[str, list[str]]:
        """Génère un planning hebdomadaire optimisé.

        Args:
            preferences: Préférences utilisateur (jours off, heures disponibles...)
            db: Session DB optionnelle

        Returns:
            Dict jour → liste de tâches
        """
        # TODO: Intégrer avec les préférences utilisateur et services
        jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        planning = {}

        for jour in jours:
            planning[jour] = []

        # Distribution intelligente des tâches
        planning["lundi"] = ["Courses", "Tri du courrier"]
        planning["mardi"] = ["Aspirateur étages"]
        planning["mercredi"] = ["Arrosage jardin", "Entretien plantes"]
        planning["jeudi"] = ["Nettoyage cuisine"]
        planning["vendredi"] = ["Nettoyage salles de bain"]
        planning["samedi"] = ["Projets bricolage", "Jardin"]
        planning["dimanche"] = ["Repos 🌿"]

        return planning


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def get_maison_assistant(client: ClientIA | None = None) -> MaisonAssistantIA:
    """Factory pour obtenir l'assistant maison.

    Args:
        client: Client IA optionnel

    Returns:
        Instance de MaisonAssistantIA
    """
    return MaisonAssistantIA(client=client)
